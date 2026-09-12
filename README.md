# 🚀 flask-backend-complex

Инструкция по развертыванию и запуску проекта

### 🛠 Подготовка окружения

Сначала настройте виртуальное окружение:

```
    py -3 -m venv .venv
```

### 📦 Установка зависимостей

Активируйте виртуальное окружение и установите необходимые библиотеки:

```
    .venv\Scripts\activate
```

```
    pip install -r requirements.txt
```

### 🐘 Настройка базы данных PostgreSQL

Запустите контейнер PostgreSQL с помощью Docker:

```
    docker run --name flask-backend-complex -p 5433:5432 -e POSTGRES_PASSWORD=root -d postgres
```

После запуска контейнера создайте базу данных:

```
    CREATE DATABASE "flask-backend-complex-db";
```

### ⚙️ Миграции и запуск

Примените последние миграции базы данных и запустите сервер:

```
    flask db upgrade
```

**Обычный запуск**

```
    flask --app main.py run
```

**Запуск в режиме отладки (Debug mode)**

```
    flask --app main.py run --debug
```

---

⚠️ _Убедитесь, что Docker запущен перед выполнением команд по настройке базы данных._

### ⌨️ Flask команда для загрузки в базу информации из csv-файла

```
    flask import-csv file_path user_name --chunk-size 2000   
```