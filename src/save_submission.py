import os
import json
import pandas as pd
import matplotlib.pyplot as plt

def save_submission(original_df, predictions, output_path):
    print(f"SAVING SUBMISSION{output_path}...")

    submission = pd.DataFrame({
        "index": original_df.index,
        "prediction": predictions})

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    submission.to_csv(output_path, index=False)


def save_feature_importances(model, output_path):
    print(f"SAVING FEATURE IMPORTANCES TO {output_path}...")

    importances = model.get_feature_importance()
    feature_names = model.feature_names_

    top_5 = sorted(
        zip(feature_names, importances),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    result = {
        feature: float(importance)
        for feature, importance in top_5
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def save_prediction_density(scores, output_path: str):
    print(f"SAVING IMAGE OF PREDICTION DENSITY TO {output_path}...")

    plt.figure(figsize=(8, 5))
    plt.hist(scores, bins=50, density=True)
    plt.xlabel("Predicted score")
    plt.ylabel("Density")
    plt.title("Distribution of predicted scores")
    plt.xlim(0, 1)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()