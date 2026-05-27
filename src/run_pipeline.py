from src.load_data import load_data
from src.preprocess import preprocess_data
from src.predict import load_model, load_threshold, make_predictions
from src.save_submission import save_prediction_density, save_submission, save_feature_importances


INPUT_PATH = "input/test.csv"
MODEL_PATH = "models/model.cbm"
THRESHOLD_PATH = "models/threshold.json"

SUBMISSION_OUTPUT_PATH = "output/sample_submission.csv"
FEATURE_IMPORTANCES_OUTPUT_PATH = "output/feature_importances.json"
DENSITY_PLOT_OUTPUT_PATH = "output/prediction_density.png"


def main():
    print("STARTING PIPELINE...")

    raw_df = load_data(INPUT_PATH)
    processed_df = preprocess_data(raw_df)
    model = load_model(MODEL_PATH)
    threshold = load_threshold(THRESHOLD_PATH)

    predictions, scores = make_predictions(
        model=model,
        X=processed_df,
        threshold=threshold)

    save_submission(
        original_df=raw_df,
        predictions=predictions,
        output_path=SUBMISSION_OUTPUT_PATH,)

    save_feature_importances(
        model=model,
        output_path=FEATURE_IMPORTANCES_OUTPUT_PATH,)

    save_prediction_density(
        scores=scores,
        output_path=DENSITY_PLOT_OUTPUT_PATH)

    print("FINISHED SUCCESFFULLY!!!!")


if __name__ == "__main__":
    main()