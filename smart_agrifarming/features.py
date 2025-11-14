from typing import Any

import numpy as np
import pandas as pd
from scipy.fft import fft

from smart_agrifarming.config import ACTIVITY_COL, ID_COL, TIME_COL


def _extract_magnitude_features(df_window: pd.DataFrame) -> dict[str, Any]:
    features: dict[str, Any] = {}

    # Acceleration magnitude.
    mpu_acc_mag = np.sqrt(
        df_window["MPU9250_AX"] ** 2
        + df_window["MPU9250_AY"] ** 2
        + df_window["MPU9250_AZ"] ** 2
    )
    bno_acc_mag = np.sqrt(
        df_window["BNO055_AX"] ** 2
        + df_window["BNO055_AY"] ** 2
        + df_window["BNO055_AZ"] ** 2
    )
    avg_acc_mag = (mpu_acc_mag + bno_acc_mag) / 2

    # Statistical features of magnitude.
    features["acc_mag_mean"] = np.mean(avg_acc_mag)
    features["acc_mag_std"] = np.std(avg_acc_mag)
    features["acc_mag_min"] = np.min(avg_acc_mag)
    features["acc_mag_max"] = np.max(avg_acc_mag)
    features["acc_mag_range"] = features["acc_mag_max"] - features["acc_mag_min"]

    # Gyroscope magnitude.
    gyro_mag = np.sqrt(
        df_window["MPU9250_GX"] ** 2
        + df_window["MPU9250_GY"] ** 2
        + df_window["MPU9250_GZ"] ** 2
    )

    # Statistical features of gyroscopic magnitude.
    features["gyro_mag_mean"] = np.mean(gyro_mag)
    features["gyro_mag_std"] = np.std(gyro_mag)

    # Signal Magnitude Area (SMA).
    features["sma"] = np.sum(
        np.abs(df_window[["MPU9250_AX", "MPU9250_AY", "MPU9250_AZ"]].values)
    )

    return features


def _extract_axis_features(
    df_window: pd.DataFrame,
    sensor_prefix: str,
) -> dict[str, Any]:
    features: dict[str, Any] = {}

    axis_suffixes = ["AX", "AY", "AZ", "GX", "GY", "GZ"]

    for axis_suffix in axis_suffixes:
        col = f"{sensor_prefix}_{axis_suffix}"
        if col not in df_window.columns:
            continue

        signal = df_window[col]

        # Time-domain.
        features[f"{col}_mean"] = np.mean(signal)
        features[f"{col}_std"] = np.std(signal)
        features[f"{col}_min"] = np.min(signal)
        features[f"{col}_max"] = np.max(signal)
        features[f"{col}_range"] = features[f"{col}_max"] - features[f"{col}_min"]

        # Percentiles.
        features[f"{col}_q25"] = np.percentile(signal, 25)
        features[f"{col}_q75"] = np.percentile(signal, 75)
        features[f"{col}_iqr"] = features[f"{col}_q75"] - features[f"{col}_q25"]

        # Zero-crossing rate.
        features[f"{col}_zcr"] = np.sum(np.diff(np.sign(signal)) != 0) / len(signal)

        # Frequency-domain.
        fft_result = fft(signal)
        # Array is symmetrical, only take one half.
        # TODO: fft_result has a weird type that np.abs apparently
        # doesn't support, even though it does.
        fft_magnitude = np.abs(fft_result[: len(signal) // 2])
        features[f"{col}_fft_mean"] = float(np.mean(fft_magnitude))
        features[f"{col}_fft_std"] = float(np.std(fft_magnitude))
        features[f"{col}_dominant_freq"] = float(np.argmax(fft_magnitude))

    return features


def extract_features(df_window: pd.DataFrame) -> dict[str, Any]:
    """Extracts features from a window of raw data."""
    features: dict[str, Any] = {}

    features.update(_extract_magnitude_features(df_window))
    features.update(_extract_axis_features(df_window, "MPU9250"))

    return features


def create_windowed_features(
    df: pd.DataFrame,
    window_size: int,
    step_size: int,
) -> pd.DataFrame:
    windowed_data: list[dict[str, Any]] = []

    df_sorted = df.sort_values(TIME_COL)
    for device_id, df_device in df_sorted.groupby(ID_COL):
        for i in range(0, len(df_device) - window_size + 1, step_size):
            df_window = df_device.iloc[i : i + window_size]

            # Window features.
            features = extract_features(df_window)

            # Window metadata.
            features[ID_COL] = device_id
            features[ACTIVITY_COL] = df_window[ACTIVITY_COL].mode()[0]
            features[TIME_COL] = df_window[TIME_COL].iloc[0]

            windowed_data.append(features)

    return pd.DataFrame(windowed_data)
