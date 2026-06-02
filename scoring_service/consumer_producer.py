import json
import os
import time
from pathlib import Path

import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

from src.preprocess import preprocess_data
from src.predict import load_model, load_threshold, make_predictions


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TRANSACTIONS_TOPIC = os.getenv("TRANSACTIONS_TOPIC", "transactions")
SCORES_TOPIC = os.getenv("SCORES_TOPIC", "scores")

MODEL_PATH = os.getenv("MODEL_PATH", "models/model.cbm")
THRESHOLD_PATH = os.getenv("THRESHOLD_PATH", "models/threshold.json")


def wait_for_kafka():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            producer.close()
            print("Kafka is available")
            break
        except NoBrokersAvailable:
            print("Kafka is not available yet. Waiting...")
            time.sleep(5)


def create_consumer():
    return KafkaConsumer(
        TRANSACTIONS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="fraud-scoring-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    )


def get_transaction_id(transaction: dict) -> str:
    if "transaction_id" in transaction:
        return str(transaction["transaction_id"])
    if "id" in transaction:
        return str(transaction["id"])
    if "index" in transaction:
        return str(transaction["index"])
    return str(int(time.time() * 1000))


def score_one_transaction(transaction: dict, model, threshold: float) -> dict:
    transaction_df = pd.DataFrame([transaction])
    processed_df = preprocess_data(transaction_df)

    predictions, scores = make_predictions(model, processed_df, threshold)

    score = float(scores[0])
    fraud_flag = int(predictions[0])

    return {
        "transaction_id": get_transaction_id(transaction),
        "score": score,
        "fraud_flag": fraud_flag,
        "us_state": transaction.get("us_state"),
        "merch": transaction.get("merch"),
        "cat_id": transaction.get("cat_id"),
    }


def main():
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    if not Path(THRESHOLD_PATH).exists():
        raise FileNotFoundError(f"Threshold not found: {THRESHOLD_PATH}")

    wait_for_kafka()

    model = load_model(MODEL_PATH)
    threshold = load_threshold(THRESHOLD_PATH)

    consumer = create_consumer()
    producer = create_producer()

    print(f"Listening topic: {TRANSACTIONS_TOPIC}")
    print(f"Writing topic: {SCORES_TOPIC}")

    for message in consumer:
        transaction = message.value

        try:
            result = score_one_transaction(transaction, model, threshold)
            producer.send(SCORES_TOPIC, value=result)
            producer.flush()

            print(f"Scored transaction: {result}")

        except Exception as error:
            print(f"Error while scoring transaction: {error}")
            print(f"Bad transaction: {transaction}")


if __name__ == "__main__":
    main()