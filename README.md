# MLOps МТС ШАД: Card Fraud Detection
<img width="1330" height="1328" alt="изображение" src="https://github.com/user-attachments/assets/eeda138f-1e01-45c0-9ecf-ddb22723a9e0" />

(https://www.kaggle.com/competitions/teta-ml-1-2025)
Docker-сервис для инференса модели fraud detection

## Структура проекта

```text
.
├── input/
│   └── .gitkeep
├── output/
│   └── .gitkeep
├── models/
│   ├── model.cbm
│   └── threshold.json
├── src/
│   ├── __init__.py
│   ├── load_data.py
│   ├── preprocess.py
│   ├── predict.py
│   ├── save_submission.py
│   └── run_pipeline.py
├── train_model.py
├── Dockerfile
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

Файл модели хранится через Git LFS, потому что он больше 100 MB.

После клонирования репозитория нужно выполнить:

```bash
git lfs install
git lfs pull
```

Дальше нужно положить файл test.csv в папку input/.
```bash
cp /путь/к/твоему/test.csv input/test.csv
```

После этого можно собирать Docker image.
Сначала нужно положить файл `test.csv` в папку:

```text
input/test.csv
```

Потом собрать Docker image:

```bash
docker build -t fraud .
```

Запустить контейнер:

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  fraud
```

После запуска результаты появятся в папке:

```text
output/
```

---

## Что будет в output

```text
sample_submission.csv
```

Файл с предсказаниями в нужном формате.

```text
feature_importances.json
```

JSON-файл с топ-5 важными признаками модели.

```text
prediction_density.png
```

График распределения предсказанных моделью скоров.

---

## Этапы пайплайна

Сервис выполняет несколько отдельных шагов:

1. `load_data.py` — загружает `input/test.csv`
2. `preprocess.py` — обрабатывает данные
3. `predict.py` — загружает модель и делает предсказания
4. `save_submission.py` — сохраняет результат
5. `run_pipeline.py` — запускает все этапы по порядку

---

## Модель

Используется `CatBoostClassifier`.

Модель обучается заранее и хранится в файле:

```text
models/model.cbm
```

Порог для перевода вероятностей в классы `0/1` хранится здесь:

```text
models/threshold.json
```

---
