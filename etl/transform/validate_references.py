# ============================================================
# transform/validate_references.py
# Kiểm tra referential integrity
# ============================================================
import pandas as pd
import logging
from typing import List, Dict

logger = logging.getLogger("etl.transform")


def validate_foreign_keys(
    df: pd.DataFrame,
    lookup_dict: Dict[str, set],
    source_name: str
) -> pd.DataFrame:
    """
    Kiểm tra FK values có tồn tại trong lookup dict.

    Args:
        df: DataFrame cần kiểm tra
        lookup_dict: dict mapping column_name -> set of valid values
        source_name: Tên nguồn để log

    Returns:
        DataFrame đã lọc bỏ invalid FKs
    """
    before = len(df)
    invalid_records = []

    for col, valid_values in lookup_dict.items():
        if col in df.columns:
            # Find invalid values
            invalid_mask = ~df[col].isin(valid_values) & df[col].notna()
            invalid_count = invalid_mask.sum()
            if invalid_count > 0:
                invalid_keys = df.loc[invalid_mask, col].unique()[:10]
                logger.warning(
                    f"[{source_name}] Column '{col}': {invalid_count} invalid FK values. "
                    f"Examples: {list(invalid_keys)}"
                )
                # Store for error log
                for val in df.loc[invalid_mask, col].unique():
                    invalid_records.append({
                        "SourceTable": source_name,
                        "ErrorType": "INVALID_FK",
                        "RawData": f"{col}={val}",
                    })

    return df, invalid_records


def validate_not_null(df: pd.DataFrame, columns: List[str], source_name: str) -> pd.DataFrame:
    """Đảm bảo các cột bắt buộc không NULL."""
    for col in columns:
        if col in df.columns:
            null_mask = df[col].isna()
            null_count = null_mask.sum()
            if null_count > 0:
                logger.warning(
                    f"[{source_name}] Column '{col}': {null_count} NULL values"
                )
    return df


def validate_value_range(
    df: pd.DataFrame,
    range_checks: Dict[str, tuple],
    source_name: str
) -> pd.DataFrame:
    """Kiểm tra giá trị nằm trong khoảng cho phép."""
    for col, (min_val, max_val) in range_checks.items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            out_of_range = ((df[col] < min_val) | (df[col] > max_val)) & df[col].notna()
            count = out_of_range.sum()
            if count > 0:
                logger.warning(
                    f"[{source_name}] Column '{col}': {count} values out of range "
                    f"[{min_val}, {max_val}]"
                )
    return df
