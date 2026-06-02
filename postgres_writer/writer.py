import json
import os
import time

import psycopg2
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
from psycopg2 import OperationalError


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
SCORES_TOPIC = os.getenv("SCORES_TOPIC", "scores")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "fraud_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "fraud_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "fraud_password")


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


def get_postgres_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def wait_for_postgres():
    while True:
        try:
            conn = get_postgres_connection()
            conn.close()
            print("PostgreSQL is available")
            break
        except OperationalError:
            print("PostgreSQL is not available yet. Waiting...")
            time.sleep(5)


def create_consumer():
    return KafkaConsumer(
        SCORES_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="postgres-writer-service",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )


def insert_score(conn, score_message: dict):
    query = """
        INSERT INTO fraud_scores (
            transaction_id,
            score,
            fraud_flag,
            us_state,
            merch,
            cat_id
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    values = (
        str(score_message.get("transaction_id")),
        float(score_message.get("score")),
        int(score_message.get("fraud_flag")),
        score_message.get("us_state"),
        score_message.get("merch"),
        score_message.get("cat_id"),
    )

    with conn.cursor() as cur:
        cur.execute(query, values)

    conn.commit()


def main():
    wait_for_kafka()
    wait_for_postgres()

    conn = get_postgres_connection()
    consumer = create_consumer()

    print(f"Listening topic: {SCORES_TOPIC}")
    print("Writing scores to PostgreSQL")

    for message in consumer:
        score_message = message.value

        try:
            insert_score(conn, score_message)
            print(f"Inserted score: {score_message}")

        except Exception as error:
            conn.rollback()
            print(f"Error while writing to PostgreSQL: {error}")
            print(f"Bad message: {score_message}")


if __name__ == "__main__":
    main()