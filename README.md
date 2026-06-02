````markdown
# MLOps МТС ШАД: Realtime Card Fraud Detection

Схема работы:

```text
test.csv → Streamlit → Kafka transactions → scoring service → Kafka scores → postgres writer → PostgreSQL → Streamlit / Grafana
````

---

## Структура проекта

```text
.
├── app/
│   └── streamlit_app.py
├── grafana/
│   ├── dashboards/
│   └── provisioning/
│       ├── dashboards/
│       └── datasources/
│           └── postgres.yml
├── init_db/
│   └── init.sql
├── input/
│   └── .gitkeep
├── models/
│   ├── model.cbm
│   └── threshold.json
├── postgres_writer/
│   ├── __init__.py
│   └── writer.py
├── scoring_service/
│   ├── __init__.py
│   └── consumer_producer.py
├── src/
│   ├── __init__.py
│   ├── preprocess.py
│   └── predict.py
├── train_model.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Как запустить

Сначала нужно склонировать репозиторий:

```bash
git clone git@github.com:mizamoon/mlops_card_fraud_MTS.git
cd mlops_card_fraud_MTS
```

Перейти на ветку с realtime-сервисом:

```bash
git checkout hw2-kafka-streaming
```

Модель хранится через Git LFS, поэтому после клонирования нужно выполнить:

```bash
git lfs install
git lfs pull
```

Дальше нужно положить `test.csv` в папку `input/`:

```bash
mkdir -p input
cp /путь/к/твоему/test.csv input/test.csv
```

Запустить все контейнеры:

```bash
docker compose up -d --build
```
---

## Как проверить работу

Открыть Streamlit:

```text
http://localhost:8501
```

Во вкладке `Отправка транзакций` нажать:

```text
Отправить транзакции в Kafka
```

Потом перейти во вкладку `Результаты` и нажать:

```text
Посмотреть результаты
```

UI показывает:

```text
10 последних транзакций с fraud_flag = 1
гистограмму score последних 100 транзакций
```

## Grafana

Открыть Grafana:

```text
http://localhost:3000
```

Логин и пароль:

```text
admin / admin
```

В Grafana настроен datasource:

```text
Fraud PostgreSQL
```

Dashboard содержит графики:

```text
Score distribution
TPS by second
Fraud share by cat_id
```

Также есть фильтры:

```text
us_state
merch
```

Графики строятся по данным из PostgreSQL.

---

## Kafka

Используются два topic:

```text
transactions
scores
```

`transactions` — входные транзакции из Streamlit.

`scores` — результат скоринга модели:

---

## PostgreSQL

База данных:

```text
fraud_db
```

Таблица:

```text
fraud_scores
```

Поля таблицы:

```text
transaction_id
score
fraud_flag
us_state
merch
cat_id
created_at
```
