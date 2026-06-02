import os
import json
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TRANSACTIONS_TOPIC = os.getenv("TRANSACTIONS_TOPIC", "transactions")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "fraud_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "fraud_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "fraud_password")


def make_json_serializable(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    )


def row_to_message(row, row_index):
    message = {
        col: make_json_serializable(value)
        for col, value in row.items()
    }

    if "transaction_id" not in message:
        if "id" in message:
            message["transaction_id"] = str(message["id"])
        elif "index" in message:
            message["transaction_id"] = str(message["index"])
        else:
            message["transaction_id"] = str(row_index)

    return message


def get_postgres_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def read_sql(query):
    conn = get_postgres_connection()
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    return df


def get_last_fraud_transactions():
    query = """
        SELECT
            transaction_id,
            score,
            fraud_flag,
            us_state,
            merch,
            cat_id,
            created_at
        FROM fraud_scores
        WHERE fraud_flag = 1
        ORDER BY created_at DESC
        LIMIT 10;
    """

    return read_sql(query)


def get_last_scores():
    query = """
        SELECT
            transaction_id,
            score,
            fraud_flag,
            us_state,
            merch,
            cat_id,
            created_at
        FROM fraud_scores
        ORDER BY created_at DESC
        LIMIT 100;
    """

    return read_sql(query)


st.set_page_config(
    page_title="Fraud Detector",
    layout="wide"
)

st.title("Fraud Transaction Scoring")
st.write("UI для имитации потока транзакций из test.csv и просмотра результатов скоринга из PostgreSQL.")

tab_send, tab_results = st.tabs(["Отправка транзакций", "Результаты"])

with tab_send:
    data_path = Path("input/test.csv")

    if not data_path.exists():
        st.error("Файл input/test.csv не найден. Положи test.csv в папку input/")
        st.stop()

    df = pd.read_csv(data_path)

    st.subheader("Данные из test.csv")
    st.write(f"Количество строк: {len(df)}")
    st.dataframe(df.head(10))

    rows_count = st.number_input(
        "Сколько транзакций отправить в Kafka",
        min_value=1,
        max_value=len(df),
        value=min(10, len(df)),
        step=1,
    )

    delay = st.number_input(
        "Задержка между транзакциями, секунд",
        min_value=0.0,
        max_value=5.0,
        value=0.1,
        step=0.1,
    )

if "current_offset" not in st.session_state:
    st.session_state.current_offset = 0

st.write(f"Текущая позиция в test.csv: {st.session_state.current_offset}")

if st.button("Отправить транзакции в Kafka"):
    try:
        producer = get_producer()

        start = st.session_state.current_offset
        end = min(start + rows_count, len(df))

        sample = df.iloc[start:end]

        if sample.empty:
            st.warning("Все строки из test.csv уже отправлены. Нажми кнопку сброса позиции.")
            st.stop()

        progress = st.progress(0)

        for i, (row_index, row) in enumerate(sample.iterrows(), start=1):
            message = row_to_message(row, row_index=row_index)

            producer.send(TRANSACTIONS_TOPIC, value=message)
            producer.flush()

            progress.progress(i / len(sample))

            if delay > 0:
                time.sleep(delay)

        st.session_state.current_offset = end

        st.success(
            f"Отправлено транзакций в Kafka: {len(sample)}. "
            f"Следующая позиция: {st.session_state.current_offset}"
        )

    except Exception as e:
        st.error(f"Ошибка при отправке в Kafka: {e}")

if st.button("Сбросить позицию отправки"):
    st.session_state.current_offset = 0
    st.success("Позиция сброшена. Следующая отправка начнется с первой строки.")


with tab_results:
    st.subheader("Результаты скоринга из PostgreSQL")

    if st.button("Посмотреть результаты"):
        try:
            fraud_df = get_last_fraud_transactions()
            scores_df = get_last_scores()

            st.markdown("### Последние 10 fraud-транзакций")

            if fraud_df.empty:
                st.info("В базе пока нет транзакций с fraud_flag = 1.")
            else:
                st.dataframe(fraud_df)

            st.markdown("### Распределение score последних 100 транзакций")

            if scores_df.empty:
                st.info("В базе пока нет результатов скоринга.")
            else:
                fig = px.histogram(
                    scores_df,
                    x="score",
                    nbins=20,
                    title="Score distribution"
                )

                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(scores_df)

        except Exception as e:
            st.error(f"Ошибка при чтении из PostgreSQL: {e}")