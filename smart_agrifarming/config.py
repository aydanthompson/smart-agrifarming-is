from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_PATH = DATA_DIR / "master.parquet"

TIME_COL = "Time"
ID_COL = "Device ID"
ACTIVITY_COL = "Activity"
PITCH_COL = "pitch"
SENSOR_COLS = [
    "BNO055_ARX",
    "BNO055_ARY",
    "BNO055_ARZ",
    "BNO055_AX",
    "BNO055_AY",
    "BNO055_AZ",
    "BNO055_GX",
    "BNO055_GY",
    "BNO055_GZ",
    "BNO055_MX",
    "BNO055_MY",
    "BNO055_MZ",
    "BNO055_Q0",
    "BNO055_Q1",
    "BNO055_Q2",
    "BNO055_Q3",
    "MPU9250_AX",
    "MPU9250_AY",
    "MPU9250_AZ",
    "MPU9250_GX",
    "MPU9250_GY",
    "MPU9250_GZ",
    "MPU9250_MX",
    "MPU9250_MY",
    "MPU9250_MZ",
]
FEATURE_COLS = SENSOR_COLS + [PITCH_COL]
