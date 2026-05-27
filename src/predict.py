import pandas as pd
from catboost import CatBoostClassifier
import json



def load_model(model_path):
    print(f"LOADING MODEL FROM {model_path}...")

    model = CatBoostClassifier()
    model.load_model(model_path)

    return model

def load_threshold(threshold_path):
    print(f"LOADING THRESHOLD FROM {threshold_path}...")

    with open(threshold_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["threshold"]


def make_predictions(model, X, threshold):
    print("Making predictions...")

    scores = model.predict_proba(X)[:, 1]
    predictions = (scores >= threshold).astype(int)

    return predictions, scores