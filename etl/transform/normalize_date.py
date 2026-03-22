# ============================================================
# transform/normalize_date.py
# Chuẩn hóa định dạng ngày tháng
# ============================================================
import pandas as pd
import logging
from typing import List
from datetime import datetime

logger = logging.getLogger("etl.transform")


def parse_date_column(
    df: pd.DataFrame,
    date_columns: List[str],
    format_hints: List[str] = None
) -> pd.DataFrame:
    """
    Parse các cột ngày tháng về DATE type.

    Args:
        df: DataFrame đầu vào
        date_columns: Danh sách tên cột ngày
        format_hints: List of format strings (e.g. 'DD/MM/YYYY', 'MM/DD/YYYY')
    """
    for col in date_columns:
        if col not in df.columns:
            continue

        formats = ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]
        if format_hints:
            for hint in format_hints:
                if hint == "DD/MM/YYYY":
                    formats.insert(0, "%d/%m/%Y")
                elif hint == "MM/DD/YYYY":
                    formats.insert(0, "%m/%d/%Y")

        parsed = None
        for fmt in formats:
            try:
                parsed = pd.to_datetime(df[col], format=fmt, errors="raise")
                logger.debug(f"Parsed {col} with format {fmt}")
                break
            except Exception:
                continue

        if parsed is None:
            parsed = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

        df[col] = parsed.dt.date
        null_count = df[col].isna().sum()
        if null_count > 0:
            logger.warning(f"Column '{col}': {null_count} values could not be parsed as date")

    return df


def to_datekey(df: pd.DataFrame, date_col: str, datekey_col: str = "DateKey") -> pd.DataFrame:
    """Tạo cột DateKey (yyyyMMdd) từ cột ngày."""
    if date_col not in df.columns:
        return df

    df[datekey_col] = pd.to_datetime(df[date_col], errors="coerce").apply(
        lambda x: int(x.strftime("%Y%m%d")) if pd.notna(x) else None
    )
    return df
