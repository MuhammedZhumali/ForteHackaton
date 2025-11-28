# Forte Fraud Shield ML

Forte Fraud Shield - это комплексная система для обнаружения мошеннических транзакций в реальном времени. Система может использовать несколько ML-моделей (GradientBoosting, RandomForest, LogisticRegression) для анализа транзакций и определения уровня риска.

## Основные возможности

- **Онлайн-скоринг транзакций** - мгновенная оценка риска мошенничества
- **Пакетная обработка** - анализ до 1000 транзакций одновременно
- **Аналитика и дашборды** - визуализация метрик и паттернов
- **Симуляция транзакций** - генерация тестовых данных для проверки системы
- **Веб-интерфейс** - удобный UI для работы с системой в стиле liquid glass
- **История транзакций** - хранение и фильтрация всех проверенных транзакций

## Структура проекта

```
ForteHackaton/
├── api/                    # API роутеры и схемы
│   ├── routers/
│   │   ├── analytics.py
│   │   ├── fraud_detection.py
│   │   ├── simulation.py
│   │   └── transactions.py
│   └── schemas.py          # pydantic схемы
├── core/                   # основная конфигурация
│   ├── config.py
│   └── database.py
├── ml/                     # ML компоненты
│   ├── model_loader.py
│   └── predictor.py
├── models/                 # модели данных
│   └── database.py
├── services/               # бизнес-логика
│   ├── analytics_service.py
│   ├── fraud_service.py
│   ├── simulation_service.py
│   └── transaction_service.py
├── trained_model/          # обученные ML модели
│   ├── GradientBoosting_fraud_model.pkl
│   ├── XGBoost_fraud_model.pkl
│   ├── RandomForest_fraud_model.pkl
│   ├── LogisticRegression_fraud_model.pkl
│   ├── imputer.pkl
│   └── scaler.pkl
├── webapp/                 # веб-интерфейс
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── data/                   # данные для обучения
├── main.py                 # точка входа приложения
└── requirements.txt        # зависимости Python
```

## Установка и запуск

**Клонируйте репозиторий и перейдите в корневую директорию**:
```bash
   git clone <repository-url>
   cd ForteHackaton
```
**Далее запустите проект одним из двух споосбов**:

### Вариант 1: запуск через Docker Compose (рекомендуется)
**В корне проекта выполните**:
```bash
   docker compose up --build
```

### Вариант 2: запуск через uvicorn
1. **Создайте виртуальное окружение**:
```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows
```

2. **Установите зависимости**:
```bash
   pip install -r requirements.txt
```

3. **Запустите приложение**:
```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Откройте в браузере
- API документация: http://localhost:8080/docs
- Веб-интерфейс: http://localhost:8080/webapp


## API Endpoints

### Fraud Detection

- `POST /api/v1/fraud/predict` - Предсказание мошенничества для одной транзакции
- `POST /api/v1/fraud/batch` - Пакетная обработка транзакций (до 1000)

### Transactions

- `GET /api/v1/transactions/` - Список транзакций с фильтрацией
- `GET /api/v1/transactions/{transaction_id}` - Детали транзакции
- `DELETE /api/v1/transactions/{transaction_id}` - Удаление транзакции
- `GET /api/v1/transactions/stats/summary` - Сводная статистика

### Analytics

- `GET /api/v1/analytics/dashboard` - Метрики для дашборда
- `GET /api/v1/analytics/risk-patterns` - Топ паттернов риска
- `GET /api/v1/analytics/feature-importance` - Важность признаков модели

### Simulation

- `POST /api/v1/simulation/generate` - Генерация тестовых транзакций
- `GET /api/v1/simulation/templates` - Шаблоны транзакций

## Веб-интерфейс

Веб-интерфейс доступен по адресу `http://localhost:8080/webapp` и включает:

- **Онлайн скоринг** - форма для проверки транзакций
- **Транзакции** - просмотр истории транзакций с фильтрацией
- **Аналитика** - дашборд с метриками и графиками

## Примеры использования

### Предсказание мошенничества

```bash
curl -X POST "http://localhost:8080/api/v1/fraud/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500000,
    "client_id": "12345",
    "os_ver_count_30d": 5,
    "phone_model_count_30d": 5,
    "logins_7d": 1,
    "logins_30d": 2,
    "logins_per_day_7": 0.14,
    "logins_per_day_30": 0.067,
    "rel_change_7_vs_30": 2.0,
    "share_7_of_30": 0.5,
    "mean_interval_30d": 200000,
    "std_interval_30d": 400000,
    "var_interval_30d": 160000000000,
    "ewm_interval_7d": 10000,
    "burstiness": 0.9,
    "fano_factor": 500000,
    "z_score_7d_vs_30d": 3.0
  }'
```

### Ответ:

```json
{
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
  "fraud_probability": 0.9443,
  "is_fraud": true,
  "risk_level": "CRITICAL",
  "reasons": [
    "Крупная сумма транзакции (1500000 тг)",
    "Множество устройств за 30 дней (5)",
    "Низкая активность входов (2 за 30 дней)"
  ],
  "model_version": "GradientBoosting_v1.0",
  "timestamp": "2025-11-28T10:00:00Z"
}
```

## ML Модели

Система поддерживает несколько ML моделей:

- **GradientBoosting** (активная по умолчанию)
- **RandomForest**
- **LogisticRegression**
- **XGBoost**

Все модели загружаются при старте приложения. Модели используют предобработку данных через:
- `imputer.pkl` - для заполнения пропущенных значений
- `scaler.pkl` - для нормализации признаков

### Признаки модели

Модель анализирует следующие признаки:
- Сумма транзакции
- Количество версий ОС за 30 дней
- Количество моделей телефона за 30 дней
- Статистика логинов (7 и 30 дней)
- Интервалы между сессиями
- Временные паттерны (burstiness, fano_factor, z-score)

### Уровни риска

- **LOW** - вероятность < 0.3
- **MEDIUM** - вероятность 0.3 - 0.6
- **HIGH** - вероятность 0.6 - 0.8
- **CRITICAL** - вероятность > 0.8

## База данных

По умолчанию используется SQLite база данных (`forte_fraud.db`). Для использования PostgreSQL измените `DATABASE_URL` в конфигурации.

Схема базы данных включает:
- Таблица транзакций с полями: transaction_id, client_id, amount, fraud_probability, is_fraud, risk_level, created_at


### Добавление новой модели

1. Обучите модель и сохраните в `trained_model/`
2. Добавьте имя модели в `model_files` в `ml/model_loader.py`
3. Замените значение параметра `active_model_name` в `ml/model_loader.py` на название новой модели которую вы добавили в `model_files`


## Авторы ^^

Nurkhat S., Arsen G., Mukhammed Z.
