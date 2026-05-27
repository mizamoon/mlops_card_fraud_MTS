import os
import json
import numpy as np
import pandas as pd

from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

from src.preprocess import preprocess_data, CATEGORICAL_COLUMNS


TRAIN_PATH = "data/train.csv"
MODEL_PATH = "models/model.cbm"
THRESHOLD_PATH = "models/threshold.json"


def find_best_threshold(y_true, scores):
    best_threshold = 0.5
    best_f1 = 0

    thresholds = np.arange(0.01, 1.00, 0.01)

    for threshold in thresholds:
        predictions = (scores >= threshold).astype(int)
        f1 = f1_score(y_true, predictions)

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    return best_threshold, best_f1


def main():
    print("LOADING TRAIN DATA...")
    train_df = pd.read_csv(TRAIN_PATH)

    print("PREPROCESSING DATA...")
    X = train_df.drop(columns=["target"])
    y = train_df["target"]

    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    X_train_processed = preprocess_data(X_train)
    X_valid_processed = preprocess_data(X_valid)

    print("TRAINING CATBOST MODEL...")

    model = CatBoostClassifier(
        iterations=2000,
        learning_rate=0.03,
        depth=6,
        loss_function="Logloss",
        eval_metric="F1",
        random_seed=42,
        auto_class_weights="Balanced",
        l2_leaf_reg=5,
        random_strength=1,
        bagging_temperature=1,
        allow_writing_files=False,
        verbose=100,
        task_type="CPU")

    model.fit(
        X_train_processed,
        y_train,
        cat_features=CATEGORICAL_COLUMNS,
        eval_set=(X_valid_processed, y_valid),
        use_best_model=True,
        early_stopping_rounds=100)

    print("FINDING BEST THRESHOLD FOR F1...")

    valid_scores = model.predict_proba(X_valid_processed)[:, 1]

    best_threshold, best_f1 = find_best_threshold(
        y_true=y_valid,
        scores=valid_scores)

    print(f"Best threshold: {best_threshold}")
    print(f"Best validation F1: {best_f1}")

    os.makedirs("models", exist_ok=True)

    print(f"Saving model to {MODEL_PATH}...")
    model.save_model(MODEL_PATH)

    print(f"Saving threshold to {THRESHOLD_PATH}...")
    with open(THRESHOLD_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "threshold": float(best_threshold),
                "validation_f1": float(best_f1)
            },
            f,
            indent=4
        )

    print("Done.")


if __name__ == "__main__":
    main()