# ============================================================
# transform/handle_nulls.py
# Xử lý giá trị NULL
# ============================================================
import pandas as pd
import logging
from typing import Any, List

logger = logging.getLogger("etl.transform")


class NullHandler:
    """Chiến lược xử lý NULL cho DataFrame."""

    @staticmethod
    def fill_default(df: pd.DataFrame, defaults: dict) -> pd.DataFrame:
        """Điền giá trị mặc định."""
        for col, default in defaults.items():
            if col in df.columns:
                df[col] = df[col].fillna(default)
        return df

    @staticmethod
    def fill_numeric_mean(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Điền giá trị trung bình cho cột numeric."""
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                mean_val = df[col].mean()
                filled = df[col].fillna(mean_val)
                null_count = df[col].isna().sum()
                df[col] = filled
                if null_count > 0:
                    logger.info(f"Filled {null_count} NULLs in '{col}' with mean={mean_val:.2f}")
        return df

    @staticmethod
    def flag_nulls(df: pd.DataFrame, columns: List[str], prefix: str = "Has") -> pd.DataFrame:
        """Tạo cột flag cho biết giá trị NULL."""
        for col in columns:
            if col in df.columns:
                flag_col = f"{prefix}{col}"
                df[flag_col] = df[col].isna().astype(int)
        return df

    @staticmethod
    def log_nulls(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        """Ghi log các giá trị NULL."""
        for col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                pct = (null_count / len(df)) * 100
                logger.warning(
                    f"[{source_name}] Column '{col}': {null_count} NULLs ({pct:.1f}%)"
                )
        return df
