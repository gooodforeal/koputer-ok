"""
Задачи Celery для отправки email
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from celery_workers.celery_app import celery_app
from celery_workers.config import settings
from celery_workers.template_loader import template_loader

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@celery_app.task(name="send_login_email", bind=True, max_retries=3)
def send_login_email(
    self,
    email: str,
    user_name: str,
    login_time: Optional[str] = None
):
    """
    Отправляет email пользователю при входе в систему
    
    Args:
        email: Email адрес получателя
        user_name: Имя пользователя
        login_time: Время входа (опционально)
    """
    try:
        # Получаем настройки SMTP из настроек
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port
        smtp_user = settings.smtp_user
        smtp_password = settings.smtp_password
        smtp_from_email = settings.smtp_from_email or smtp_user
        
        if not smtp_user or not smtp_password:
            logger.error("SMTP credentials not configured")
            return {"status": "error", "message": "SMTP credentials not configured"}
        
        # Создаем сообщение
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Успешный вход в систему"
        msg["From"] = smtp_from_email
        msg["To"] = email
        
        # Подготавливаем данные для шаблонов
        # Форматируем время входа для лучшей читаемости
        if login_time:
            try:
                # Пытаемся распарсить разные форматы времени
                from datetime import datetime
                # Если это ISO формат (с T или Z)
                if 'T' in login_time or 'Z' in login_time:
                    try:
                        dt = datetime.fromisoformat(login_time.replace('Z', '+00:00'))
                        login_time_str = dt.strftime("%d.%m.%Y в %H:%M:%S")
                    except:
                        # Если не получилось распарсить ISO, пробуем другие форматы
                        login_time_str = login_time
                # Если это уже отформатированное время (YYYY-MM-DD HH:MM:SS)
                elif len(login_time) > 10 and ' ' in login_time:
                    try:
                        dt = datetime.strptime(login_time, "%Y-%m-%d %H:%M:%S")
                        login_time_str = dt.strftime("%d.%m.%Y в %H:%M:%S")
                    except:
                        login_time_str = login_time
                else:
                    login_time_str = login_time
            except Exception as e:
                logger.warning(f"Не удалось распарсить время входа '{login_time}': {e}")
                login_time_str = login_time
        else:
            login_time_str = "только что"
        
        template_vars = {
            "user_name": user_name or "Пользователь",
            "login_time": login_time_str
        }
        
        # Логируем переменные для отладки
        logger.info(f"Рендеринг шаблона email с переменными: user_name={template_vars['user_name']}, login_time={template_vars['login_time']}")
        
        # Загружаем и рендерим шаблоны
        try:
            text_content = template_loader.render_template(
                "login_email.txt",
                **template_vars
            )
            html_content = template_loader.render_template(
                "login_email.html",
                **template_vars
            )
            
            # Проверяем, что переменные подставились
            if "{{user_name}}" in html_content or "{{login_time}}" in html_content:
                logger.warning(f"Переменные не были подставлены в шаблон! Проверьте шаблон.")
                logger.debug(f"HTML контент (первые 500 символов): {html_content[:500]}")
        except FileNotFoundError as e:
            logger.error(f"Ошибка загрузки шаблона: {str(e)}")
            # Fallback на простой текст, если шаблон не найден
            text_content = f"""
                Здравствуйте, {user_name}!

                Вы успешно вошли в систему.

                Время входа: {login_time_str}

                Если это были не вы, пожалуйста, свяжитесь с поддержкой.

                С уважением,
                Команда поддержки
            """
            html_content = None
        
        # Добавляем части сообщения
        text_part = MIMEText(text_content, "plain", "utf-8")
        msg.attach(text_part)
        
        # Добавляем HTML часть, если она есть
        if html_content:
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
        
        # Отправляем email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email успешно отправлен на {email}")
        return {"status": "success", "email": email}
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error при отправке email на {email}: {str(e)}")
        # Повторяем попытку при временных ошибках
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
    except Exception as e:
        logger.error(f"Ошибка при отправке email на {email}: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@celery_app.task(name="send_balance_email", bind=True, max_retries=3)
def send_balance_email(
    self,
    email: str,
    user_name: str,
    amount: str,
    new_balance: str,
    payment_time: Optional[str] = None,
    transaction_id: Optional[str] = None
):
    """
    Отправляет email пользователю при успешном пополнении баланса
    
    Args:
        email: Email адрес получателя
        user_name: Имя пользователя
        amount: Сумма пополнения
        new_balance: Новый баланс после пополнения
        payment_time: Время пополнения (опционально)
        transaction_id: ID транзакции (опционально)
    """
    try:
        # Получаем настройки SMTP из настроек
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port
        smtp_user = settings.smtp_user
        smtp_password = settings.smtp_password
        smtp_from_email = settings.smtp_from_email or smtp_user
        
        if not smtp_user or not smtp_password:
            logger.error("SMTP credentials not configured")
            return {"status": "error", "message": "SMTP credentials not configured"}
        
        # Создаем сообщение
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Баланс успешно пополнен"
        msg["From"] = smtp_from_email
        msg["To"] = email
        
        # Подготавливаем данные для шаблонов
        # Форматируем время пополнения для лучшей читаемости
        if payment_time:
            try:
                from datetime import datetime
                # Если это ISO формат (с T или Z)
                if 'T' in payment_time or 'Z' in payment_time:
                    try:
                        dt = datetime.fromisoformat(payment_time.replace('Z', '+00:00'))
                        payment_time_str = dt.strftime("%d.%m.%Y в %H:%M:%S")
                    except:
                        payment_time_str = payment_time
                # Если это уже отформатированное время (YYYY-MM-DD HH:MM:SS)
                elif len(payment_time) > 10 and ' ' in payment_time:
                    try:
                        dt = datetime.strptime(payment_time, "%Y-%m-%d %H:%M:%S")
                        payment_time_str = dt.strftime("%d.%m.%Y в %H:%M:%S")
                    except:
                        payment_time_str = payment_time
                else:
                    payment_time_str = payment_time
            except Exception as e:
                logger.warning(f"Не удалось распарсить время пополнения '{payment_time}': {e}")
                payment_time_str = payment_time
        else:
            from datetime import datetime
            payment_time_str = datetime.now().strftime("%d.%m.%Y в %H:%M:%S")
        
        template_vars = {
            "user_name": user_name or "Пользователь",
            "amount": amount,
            "new_balance": new_balance,
            "payment_time": payment_time_str,
            "transaction_id": transaction_id or "N/A"
        }
        
        # Логируем переменные для отладки
        logger.info(f"Рендеринг шаблона email о пополнении баланса: user_name={template_vars['user_name']}, amount={template_vars['amount']}")
        
        # Загружаем и рендерим шаблоны
        try:
            text_content = template_loader.render_template(
                "balance_email.txt",
                **template_vars
            )
            html_content = template_loader.render_template(
                "balance_email.html",
                **template_vars
            )
            
            # Проверяем, что переменные подставились
            if "{{user_name}}" in html_content or "{{amount}}" in html_content:
                logger.warning(f"Переменные не были подставлены в шаблон! Проверьте шаблон.")
                logger.debug(f"HTML контент (первые 500 символов): {html_content[:500]}")
        except FileNotFoundError as e:
            logger.error(f"Ошибка загрузки шаблона: {str(e)}")
            # Fallback на простой текст, если шаблон не найден
            text_content = f"""
                Здравствуйте, {user_name}!

                Ваш баланс успешно пополнен на сумму {amount} ₽.

                Новый баланс: {new_balance} ₽
                Время пополнения: {payment_time_str}
                ID транзакции: {transaction_id or 'N/A'}

                Спасибо за использование нашего сервиса!

                С уважением,
                Команда поддержки Компьютер.ок
            """
            html_content = None
        
        # Добавляем части сообщения
        text_part = MIMEText(text_content, "plain", "utf-8")
        msg.attach(text_part)
        
        # Добавляем HTML часть, если она есть
        if html_content:
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
        
        # Отправляем email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email о пополнении баланса успешно отправлен на {email}")
        return {"status": "success", "email": email}
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error при отправке email на {email}: {str(e)}")
        # Повторяем попытку при временных ошибках
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
    except Exception as e:
        logger.error(f"Ошибка при отправке email на {email}: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

