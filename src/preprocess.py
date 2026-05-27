import pandas as pd
import numpy as np


CATEGORICAL_COLUMNS = [
    "merch",
    "cat_id",
    "name_1",
    "name_2",
    "gender",
    "street",
    "one_city",
    "us_state",
    "post_code",
    "jobs",
]

NUMERIC_COLUMNS = [
    "amount",
    "lat",
    "lon",
    "population_city",
    "merchant_lat",
    "merchant_lon",
]

NEW_NUMERIC_COLUMNS = [
    "hour",
    "day",
    "month",
    "dayofweek",
    "distance",
]

FEATURE_COLUMNS = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS + NEW_NUMERIC_COLUMNS


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"],
        errors="coerce")

    df["hour"] = df["transaction_time"].dt.hour
    df["day"] = df["transaction_time"].dt.day
    df["month"] = df["transaction_time"].dt.month
    df["dayofweek"] = df["transaction_time"].dt.dayofweek

    df["distance"] = np.sqrt(
        (df["lat"] - df["merchant_lat"]) ** 2
        + (df["lon"] - df["merchant_lon"]) ** 2)

    for col in CATEGORICAL_COLUMNS:
        if col not in df.columns:
            df[col] = "unknown"

        df[col] = df[col].astype(str)
        df[col] = df[col].fillna("unknown")

    for col in NUMERIC_COLUMNS + NEW_NUMERIC_COLUMNS:
        if col not in df.columns:
            df[col] = 0

        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(0)

    df = df[FEATURE_COLUMNS]

    return df