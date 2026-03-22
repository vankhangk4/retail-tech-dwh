# ============================================================
# transform/clean_data.py
# Các hàm làm sạch dữ liệu chung
# ============================================================
import pandas as pd
import logging
from typing import List

logger = logging.getLogger("etl.transform")


def trim_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Loại bỏ khoảng trắng thừa ở đầu/cuối string columns."""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(
            lambda x: str(x).strip() if pd.notna(x) and isinstance(x, str) else x
        )
    return df


def normalize_case(df: pd.DataFrame, columns: List[str], upper: bool = True) -> pd.DataFrame:
    """Chuẩn hóa hoa/thường."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: str(x).upper() if pd.notna(x) and isinstance(x, str) else x
            )
    return df


def deduplicate(df: pd.DataFrame, key_columns: List[str], keep: str = "last") -> pd.DataFrame:
    """Loại bỏ bản ghi trùng lặp theo key columns."""
    before = len(df)
    df = df.drop_duplicates(subset=key_columns, keep=keep)
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Deduplication: removed {removed} duplicate rows")
    return df


def remove_empty_rows(df: pd.DataFrame, key_columns: List[str]) -> pd.DataFrame:
    """Loại bỏ rows mà key columns bị NULL/empty."""
    before = len(df)
    mask = df[key_columns].notna().all(axis=1)
    df = df[mask]
    removed = before - len(df)
    if removed > 0:
        logger.warning(f"Removed {removed} rows with NULL key columns: {key_columns}")
    return df


def cast_types(df: pd.DataFrame, type_map: dict) -> pd.DataFrame:
    """Cast columns sang kiểu dữ liệu chỉ định."""
    for col, dtype in type_map.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
            except Exception as e:
                logger.warning(f"Failed to cast {col} to {dtype}: {e}")
    return df


def fill_nulls(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """Điền giá trị NULL theo strategy chỉ định."""
    for col, fill_value in strategy.items():
        if col in df.columns:
            df[col] = df[col].fillna(fill_value)
    return df
