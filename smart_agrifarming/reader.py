import pandas as pd

from smart_agrifarming.config import (
    ACTIVITY_COL,
    CACHE_PATH,
    DATA_DIR,
    ID_COL,
    TIME_COL,
)


def combine_datasets() -> pd.DataFrame:
    if CACHE_PATH.exists():
        df_master = pd.read_parquet(CACHE_PATH)
        print("Cache already exists.")
    else:
        all_paths = list(DATA_DIR.glob("*.csv"))

        if not all_paths:
            raise FileNotFoundError(f"No CSVs found: '{DATA_DIR}'")
        else:
            all_dataframes: list[pd.DataFrame] = []

            for path in all_paths:
                try:
                    parts = path.name.split("_")
                    activity = parts[1]
                    device_id = parts[2]

                    df = pd.read_csv(path)

                    df[ACTIVITY_COL] = activity
                    df[ID_COL] = device_id

                    all_dataframes.append(df)
                except Exception as ex:
                    print(f"Error processing file '{path}': '{ex}'")

            if all_dataframes:
                df_master = pd.concat(all_dataframes, ignore_index=True)

                # Drop overlapping data.
                # If a datapoint appears in two datasets (e.g., grazing and
                # walking), only the first occurrence will be kept.
                df_master.drop_duplicates(
                    subset=[TIME_COL, ID_COL],
                    keep="first",
                    inplace=True,
                )

                df_master.to_parquet(CACHE_PATH, engine="pyarrow", index=False)
                print("Successfully generated new cache.")
            else:
                raise FileNotFoundError("DataFrame list is empty.")

    return df_master
