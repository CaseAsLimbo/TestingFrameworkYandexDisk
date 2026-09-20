# Yandex.Disk API Test Framework

Фреймворк автоматизированного тестирования REST API Яндекс.Диска на Python 3 + pytest.

## 🎯 Цель проекта

Демонстрация подхода к интеграционному тестированию внешнего API:
- Слоистая архитектура (`BaseClient` → доменные клиенты → тесты).
- Валидация контрактов ответов через Pydantic-модели.
- Асинхронные операции (polling статуса).
- Ретраи с учётом идемпотентности HTTP-методов.
- Структурированное логирование с маскировкой секретов.
- CI/CD с отчётом Allure.

## 📋 Требования

- Python 3.10+
- OAuth-токен Яндекс.Диска (см. раздел «Получение токена»)

## 🚀 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/<username>/yandex-disk-api-tests.git
cd yandex-disk-api-tests
```

### 2. Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Настройка окружения

Скопируйте `.env.example` в `.env` и заполните токен:

```bash
cp .env.example .env
```

Содержимое `.env`:

```env
API_TOKEN=your_yandex_oauth_token_here
```

Дополнительные переменные (опционально, если нужно переопределить дефолты из `config/settings.py`):

```env
# BASE_URL=https://cloud-api.yandex.net
# API_VERSION=v1
```

## 🔑 Получение токена

1. Зарегистрируйте приложение на [oauth.yandex.ru](https://oauth.yandex.ru/client/new).
2. Укажите `Redirect URI: https://oauth.yandex.ru/verification_code`.
3. Выберите права доступа: `cloud_api:disk.read`, `cloud_api:disk.write`, `cloud_api:disk.info`.
4. После регистрации скопируйте `Client ID`.
5. Перейдите по ссылке (подставив свой `client_id`):

   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=<YOUR_CLIENT_ID>
   ```

6. Подтвердите доступ. Из адресной строки скопируйте значение `access_token`.
7. Вставьте его в `.env` как `API_TOKEN`.

> ⚠️ **Важно:** используйте изолированный тестовый аккаунт, а не личный.

## 🧪 Запуск тестов

```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/test_post_upload.py

# Конкретный тест
pytest tests/test_post_upload.py::TestPostUploadFromUrl::test_upload_from_url_success

# С Allure-отчётом
pytest --alluredir=allure-results
allure serve allure-results
```

### Makefile

```bash
make install    # установить зависимости
make test       # запустить тесты
make lint       # запустить ruff
make allure     # сгенерировать и открыть Allure-отчёт
```

## 📁 Структура проекта

```
.
├── api
│   ├── base_client.py                  # Базовый клиент, управляет сессией и ретраями
│   ├── clients
│   │   └── disk_client.py              # Кастомный клиент, реализует методы API
│   ├── hooks.py                        # хуки для логгирования запросов и ответов
│   └── routes
│       └── disk_routes.py              # Маршруты кастомного клиента, предполагается, что клиентов может быть несколько
├── config
│   └── settings.py
├── conftest.py                         # фикстуры общего назначения
├── env.example
├── Makefile
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── schemas
│   ├── base.py
│   └── models.py
└── tests
    ├── conftest.py                     # фикстуры для тестов
    └── test_disk                       # тесты на API YADisk 
        └── test_disk_general.py
```

## 🏗️ Архитектура

### Три слоя

1. **`BaseClient`** — транспортный слой. Отвечает только за HTTP: сессия, URL, авторизация, таймауты, ретраи, логирование. Не знает про домены.
2. **`DiskClient`** — доменный слой. Знает маршруты и модели Яндекс.Диска. Инкапсулирует polling асинхронных операций.
3. **Тесты** — слой проверок. Используют доменный клиент, валидируют модели и семантику.

### Принципы

- **Сквозные заботы в одном месте.** Ретраи, логирование, таймауты — в `BaseClient`.
- **Идемпотентность.** GET/PUT/DELETE ретраят 5xx, POST/PATCH — нет.
- **Композиция, не наследование.** `DiskClient(base_client)`.
- **Явное лучше неявного.** Ожидаемый статус передаётся в метод, а не угадывается.

## 🔧 Переменные окружения

| Переменная | Обязательна | Дефолт | Описание |
|---|---|---|---|
| `API_TOKEN` | ✅ | — | OAuth-токен Яндекс.Диска |
| `BASE_URL` | ❌ | `https://cloud-api.yandex.net` | Базовый URL API |
| `API_VERSION` | ❌ | `v1` | Версия API |

Секреты хранятся **только** в `.env` (локально) или в GitHub Secrets (CI). `.env` в `.gitignore`.

## 🎨 Логирование

Все запросы логируются через хук `requests` в JSON-совместимом формате:
- Метод, URL, статус, длительность.
- Заголовки запроса с маскировкой `Authorization`, `Cookie`.
- Тело запроса/ответа с маскировкой `access_token`, `password`, `secret`.
- Усечение длинных тел (500 символов).

## 🤖 CI/CD

GitHub Actions workflow `.github/workflows/checks.yml` запускается на каждый push и PR:
1. Устанавливает зависимости.
2. Запускает `pytest` с Allure-отчётом.
3. Публикует отчёт на GitHub Pages.

## 📊 Allure-отчёт

Локально:

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

В CI — отчёт публикуется автоматически на `https://<username>.github.io/<repo>/`.

## ⚠️ Ограничения

- Тесты **не идемпотентны** в части использования Диска: создают и удаляют файлы. Не запускайте против продакшн-аккаунта с важными данными.
- Троттлинг загрузки: Яндекс ограничивает скорость для неофициальных клиентов. Если тесты начнут тормозить — см. `User-Agent` в `BaseClient`.
- Токен долгоживущий, но при смене пароля Яндекс-аккаунта — отзывается.
