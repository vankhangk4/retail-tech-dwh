import pandas as pd


def smart_parse_date(series: pd.Series) -> pd.Series:
    """
    Parse mixed date formats: yyyy-mm-dd, dd/mm/yyyy, dd-mm-yyyy.
    Vectorized with explicit format strings.
    """
    # Clean: convert to string and replace empty/null values
    s_str = series.astype(str).str.strip().replace(
        ['', 'nan', 'None', 'NaT', '0000-00-00'], pd.NA
    )

    # All null → return NaT
    if s_str.isna().all():
        return pd.Series(pd.NaT, index=series.index)

    result = pd.Series(pd.NaT, index=series.index)

    # Format 1: yyyy-mm-dd (ISO)
    iso_mask = s_str.str.match(r'^\d{4}-\d{2}-\d{2}', na=False)
    if iso_mask.any():
        result[iso_mask] = pd.to_datetime(s_str[iso_mask], format='%Y-%m-%d', errors='coerce')

    # Format 2 & 3: try both dd-mm-yyyy and dd/mm/yyyy for remaining
    remaining = s_str[~iso_mask & s_str.notna()]
    if len(remaining) > 0:
        # Try dd-mm-yyyy
        r1 = pd.to_datetime(remaining, format='%d-%m-%Y', errors='coerce')
        # Try dd/mm/yyyy
        r2 = pd.to_datetime(remaining, format='%d/%m/%Y', errors='coerce')
        # Merge: prefer r1 (dd-mm-yyyy), fill gaps with r2 (dd/mm/yyyy)
        result[remaining.index] = r1.fillna(r2)

    return result
