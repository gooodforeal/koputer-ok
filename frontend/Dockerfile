FROM node:20-alpine

WORKDIR /frontend

# Копирование зависимостей
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование исходного кода
COPY . .

# Установка переменных окружения для Vite
ENV VITE_API_URL=http://localhost:8000
ENV VITE_FRONTEND_URL=http://localhost:3000

# Открытие порта
EXPOSE 3000

# Команда для запуска в режиме разработки (для hot reload)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

