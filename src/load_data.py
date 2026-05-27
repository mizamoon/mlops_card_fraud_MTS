import pandas as pd


def load_data(input_path):
    print(f"LOADING DATA {input_path}...")
    df = pd.read_csv(input_path)
    return df