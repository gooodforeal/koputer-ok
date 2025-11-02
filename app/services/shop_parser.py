"""
Shop Parser - Парсер товаров с сайта на aiohttp и BeautifulSoup
Функция: получение списка всех комплектующих из указанной категории
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from enum import Enum
import asyncio
import re
import urllib.parse
import logging
import os
import hashlib

# Настройка логирования только для консоли
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class ComponentsCategory(Enum):
    # Основные категории
    PROCESSORY = ("Процессоры", ["/protsessory"])
    MATERINSKIE_PLATY = ("Материнские платы", ["/materinskie-platy"])
    VIDEOKARTY = ("Видеокарты", ["/videokarty"])
    OPERATIVNAYA_PAMYAT = ("Оперативная память", ["/operativnaya-pamyat"])
    KORPUSA = ("Корпуса", ["/korpusa"])
    BLOKI_PITANIYA = ("Блоки питания", ["/bloki-pitaniya"])
    ZHESTKIE_DISKI = ("Жесткие диски", ["/diski-hdd"])
    OHLAZHDENIE = ("Охлаждение", ["/kulery"])
    SSD_NAKOPITELI = ("SSD накопители", ["/diski-ssd"])
    
    def __init__(self, display_name: str, paths: List[str]):
        self.display_name = display_name
        self.paths = paths
    
    def get_urls(self, base_url: str) -> List[str]:
        """Возвращает полные URL для всех путей категории"""
        return [f"{base_url}/category{path}" for path in self.paths]


class ShopParser:
    """Парсер товаров на aiohttp и BeautifulSoup"""
    
    def __init__(self, timeout: int = 10, max_concurrent: int = 5, use_cache: bool = True, cache_dir: str = "cache"):
        """
        Инициализация парсера
        
        Args:
            timeout: Таймаут для HTTP-запросов (секунды)
            max_concurrent: Максимальное количество одновременных запросов
            use_cache: Использовать кеширование HTML в файлы
            cache_dir: Директория для сохранения кеша
        """
        self.base_url = "https://28bit.ru"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        
        # Создаем директорию для кеша, если она не существует
        if self.use_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"[Инфо] Создана директория для кеша: {self.cache_dir}")
        
        # Заголовки из реального запроса браузера
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',  # zstd удален, так как требует дополнительную библиотеку
            'accept-language': 'ru,en-US;q=0.9,en;q=0.8,bg;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Opera";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',  # Будет изменено на 'same-origin' для внутренних запросов
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0 (Edition Yx 05)',
        }
        
        # Cookies из реального запроса
        self.cookies_str = (
            '__ddg1_=Ii2IxecvvoESN9JfFW3N; '
            '_ym_uid=1740512373874780590; '
            'isMobile=false; '
            'cityselect__kladr_id=7700000000000; '
            'cityselect__fias_id=0c5b2444-70a0-4932-980c-b4dc0d3f02b5; '
            'cityselect__constraints_street=7700000000000; '
            'cityselect__country=rus; '
            'cityselect__city=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0; '
            'cityselect__region=77; '
            'cityselect__zip=101000; '
            'cityselect__show_notifier=1752940197; '
            'referer=https%3A%2F%2Fyandex.ru%2F; '
            'landing=%2F; '
            'pricetype_manual=0; '
            'pricetype=0; '
            'PHPSESSID=1qce5stsv29mc2mkir6qfn5v2u; '
            '_ym_d=1762018404; '
            '_ym_isad=2; '
            '_ym_visorc=w; '
            'data-up-theme=dark; '
            'products_per_page=96; '
            'pricetype_set=1762018476'
        )
    
    async def _init_session(self):
        """Инициализация HTTP сессии"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100)
            
            # Создаем сессию
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout,
                connector=connector
            )
            
            logger.info("[Инфо] HTTP сессия инициализирована")
    
    def _get_cache_filename(self, url: str) -> str:
        """Генерирует имя файла кеша из URL"""
        # Создаем хеш URL для безопасного имени файла
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        # Очищаем URL для использования в имени файла
        safe_url = re.sub(r'[^\w\-_\.]', '_', url.replace('https://', '').replace('http://', ''))
        safe_url = safe_url[:100]  # Ограничиваем длину
        return os.path.join(self.cache_dir, f"{safe_url}_{url_hash}.html")
    
    def _load_from_cache(self, cache_file: str) -> Optional[str]:
        """Загружает HTML из кеша, если файл существует"""
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    html = f.read()
                logger.info(f"[Кеш] Загружено из кеша: {cache_file}")
                return html
            except Exception as e:
                logger.warning(f"[Предупреждение] Ошибка при чтении кеша {cache_file}: {e}")
                return None
        return None
    
    def _save_to_cache(self, cache_file: str, html: str):
        """Сохраняет HTML в кеш"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"[Кеш] Сохранено в кеш: {cache_file}")
        except Exception as e:
            logger.warning(f"[Предупреждение] Ошибка при сохранении кеша {cache_file}: {e}")
    
    async def fetch_page(self, url: str, force_refresh: bool = False) -> Optional[str]:
        """
        Получает HTML страницы с использованием сохраненной сессии и cookies
        
        Args:
            url: URL страницы
            force_refresh: Принудительно обновить кеш (игнорировать существующий)
            
        Returns:
            HTML содержимое страницы или None при ошибке
        """
        # Проверяем кеш перед запросом
        if self.use_cache and not force_refresh:
            cache_file = self._get_cache_filename(url)
            cached_html = self._load_from_cache(cache_file)
            if cached_html:
                return cached_html
        
        if not self.session:
            await self._init_session()
        
        try:
            # Извлекаем путь из URL (path + query)
            parsed_url = urllib.parse.urlparse(url)
            url_path = parsed_url.path
            if parsed_url.query:
                url_path += f"?{parsed_url.query}"
            
            # Добавляем Referer для внутренних страниц и cookies
            headers = {**self.headers, 'Cookie': self.cookies_str}
            if url != self.base_url:
                # Устанавливаем referer как полный URL текущей страницы
                headers['referer'] = url
                headers['sec-fetch-site'] = 'same-origin'
                headers['X-Requested-With'] = 'XMLHttpRequest'
            
            # Добавляем заголовок с путем текущей страницы
            headers['X-Request-Path'] = url_path
            
            async with self.session.get(url, headers=headers, allow_redirects=True) as response:
                logger.info(f"[Диагностика] HTTP статус: {response.status} для {url}")
                
                if response.status == 200:
                    html = await response.text()
                    logger.info(f"[Инфо] Страница загружена: {url} (размер: {len(html)} символов)")
                    
                    # Сохраняем в кеш
                    if self.use_cache:
                        cache_file = self._get_cache_filename(url)
                        self._save_to_cache(cache_file, html)
                    
                    return html
                elif response.status == 401:
                    error_body = await response.text()
                    logger.error(f"[Ошибка] 401 Unauthorized для {url}")
                    logger.error(f"[Диагностика] Заголовки ответа: {dict(response.headers)}")
                    logger.error(f"[Диагностика] Тело ответа (первые 1000 символов): {error_body[:1000]}")
                    return None
                else:
                    error_body = await response.text()
                    logger.warning(f"[Предупреждение] HTTP статус {response.status} для {url}")
                    logger.warning(f"[Диагностика] Тело ответа (первые 500 символов): {error_body[:500]}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"[Ошибка] Таймаут при загрузке {url}")
            return None
        except Exception as e:
            logger.error(f"[Ошибка] Ошибка при загрузке {url}: {e}")
            import traceback
            logger.error(f"[Диагностика] Трассировка: {traceback.format_exc()}")
            return None

    async def _get_products_from_page(self, html: str) -> List[Dict[str, str]]:
        page_products = []
        soup = BeautifulSoup(html, 'html.parser')

        items = soup.find_all('div', class_='products__item')

        for item in items:
            try:
                name = item.find('div', class_='products__content').find('a').text
                link = self.base_url + item.find('div', class_='products__content').find('a').get('href')
                price = item.find('div', class_='products__content').find('div', class_='products__prices').find("div", class_='prices__price').text
                image = self.base_url + item.find('div', class_='products__img-wrap').find('a').find("span").find("img").get('src')
            except Exception as e:
                logger.error(f"[Ошибка] Ошибка при парсинге товара: {e}")
                continue
            page_products.append({
                "name": name,
                "link": link,
                "price": int(price.replace("₽", "").replace(" ", "")),
                "image": image
            })
 
        return page_products

    async def get_category(self, category: ComponentsCategory) -> List[Dict[str, str]]:
        all_category_products = []
        for base_url_path in category.get_urls(self.base_url):
            page = 1
            # Сохраняем исходный URL без параметров
            base_url = base_url_path
            
            while True:
                await asyncio.sleep(1)

                if '?' in base_url:
                    url = f"{base_url}/&page={page}"
                else:
                    url = f"{base_url}/?page={page}"
                
                html = await self.fetch_page(url)

                if not html:  # Добавляем проверку на None
                    break
                    
                current_page_products = await self._get_products_from_page(html)

                if not len(current_page_products):
                    break

                all_category_products.extend(current_page_products)
                page += 1

        return all_category_products

    async def get_products_from_category(self, category_name: str | ComponentsCategory) -> List[Dict[str, str]]:
        """
        Получает товары из категории (для обратной совместимости)
        
        Args:
            category_name: Название категории (можно использовать ComponentsCategory или строку)
            
        Returns:
            Список товаров
        """
        # Определяем категорию (поддержка enum или строки)
        if isinstance(category_name, ComponentsCategory):
            category = category_name
        else:
            # Пытаемся найти категорию по названию
            category = None
            for cat in ComponentsCategory:
                if cat.display_name.lower() == category_name.lower() or cat.name.lower() == category_name.lower():
                    category = cat
                    break
            
            if category is None:
                # Если не найдена, используем процессоры по умолчанию
                logger.warning(f"[Предупреждение] Категория '{category_name}' не найдена, используем Процессоры")
                category = ComponentsCategory.PROCESSORY
        
        logger.info(f"[Инфо] Парсинг категории: {category.display_name}")
        return await self.get_category(category)

    async def close(self):
        if self.session:
            try:
                await self.session.close()
                logger.info("[Инфо] HTTP сессия закрыта")
            except Exception as e:
                logger.warning(f"[Предупреждение] Ошибка при закрытии сессии: {e}")
            finally:
                self.session = None


async def get_products_by_category(category_name: str | ComponentsCategory) -> List[Dict[str, str]]:
    """
    Получает товары из категории (асинхронная функция)
    
    Args:
        category_name: Название категории (строка или ComponentsCategory enum)
        
    Returns:
        Список товаров
        
    Example:
        # Использование enum
        products = await get_products_by_category(ComponentsCategory.PROCESSORY)
        
        # Использование строки
        products = await get_products_by_category("Процессоры")
    """
    parser = ShopParser()
    try:
        return await parser.get_products_from_category(category_name)
    finally:
        await parser.close()


async def main():
    """Пример использования парсера"""
    parser = ShopParser()
    try:
        print(await parser.get_category(ComponentsCategory.MATERINSKIE_PLATY))
    except Exception as e:
        logger.error(f"[Ошибка] Не удалось загрузить страницу")
    finally:
        await parser.close()


if __name__ == "__main__":
    asyncio.run(main())

