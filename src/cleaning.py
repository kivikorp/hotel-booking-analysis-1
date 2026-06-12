"""Utilities for loading, inspecting, cleaning, and saving hotel booking data."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "hotel_bookings.csv"
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "hotel_bookings_clean.csv"


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw hotel booking dataset from a CSV file.

    Args:
        path: Path to the raw CSV file.

    Returns:
        DataFrame containing the raw hotel booking records.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Dataset file was not found: {path}")

    return pd.read_csv(path)


def get_cleaning_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create a data quality summary for each column.

    The summary includes data types, missing value counts, missing value
    percentages, and the number of unique values.

    Args:
        df: DataFrame to inspect.

    Returns:
        DataFrame containing column-level data quality information.
    """
    summary = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "missing_count": df.isna().sum(),
            "missing_percent": df.isna().mean() * 100,
            "unique_values": df.nunique(dropna=True),
        }
    )

    return summary.sort_values("missing_count", ascending=False)


def remove_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows.

    Args:
        df: Hotel booking DataFrame.

    Returns:
        DataFrame without exact duplicate rows.
    """
    return df.drop_duplicates(ignore_index=True)


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle selected missing values in the hotel booking dataset.

    Args:
        df: Hotel booking DataFrame.

    Returns:
        DataFrame with selected missing values filled.

    Notes:
        Missing `children` values are treated as 0.
        Missing `country` values are treated as "Unknown".
    """
    df = df.copy()

    df["children"] = df["children"].fillna(0)
    df["country"] = df["country"].fillna("Unknown")

    return df


def drop_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns that are not needed for the analysis.

    Args:
        df: Hotel booking DataFrame.

    Returns:
        DataFrame without selected unnecessary columns.
    """
    columns_to_drop = ["company", "agent"]
    existing_columns = [col for col in columns_to_drop if col in df.columns]

    return df.drop(columns=existing_columns)


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Fix selected data types for analysis.

    Args:
        df: Hotel booking DataFrame.

    Returns:
        DataFrame with corrected data types.
    """
    df = df.copy()

    df["children"] = df["children"].astype(int)
    df["reservation_status_date"] = pd.to_datetime(
        df["reservation_status_date"],
        errors="coerce",
    )

    return df


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with impossible or meaningless values.

    Args:
        df: Hotel booking DataFrame.

    Returns:
        DataFrame without invalid rows.

    Notes:
        Rows with zero total guests are removed.
        Rows with negative `adr` are removed.
    """
    df = df.copy()

    has_guests = (df["adults"] > 0) | (df["children"] > 0) | (df["babies"] > 0)

    df = df[has_guests]
    df = df[df["adr"] >= 0]

    return df.reset_index(drop=True)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the hotel booking dataset for analysis.

    The cleaning pipeline removes exact duplicates, handles selected missing
    values, drops unnecessary columns, fixes selected data types, and removes
    invalid records.

    Args:
        df: Raw hotel booking DataFrame.

    Returns:
        Cleaned copy of the input DataFrame.
    """
    cleaned = df.copy()

    cleaned = remove_duplicate_rows(cleaned)
    cleaned = handle_missing_values(cleaned)
    cleaned = drop_unnecessary_columns(cleaned)
    cleaned = fix_data_types(cleaned)
    cleaned = remove_invalid_rows(cleaned)
    cleaned = remove_duplicate_rows(cleaned)

    return cleaned.reset_index(drop=True)


def get_duplicate_count(df: pd.DataFrame) -> int:
    """Return the number of exact duplicate rows."""
    return int(df.duplicated().sum())


def get_total_missing_values(df: pd.DataFrame) -> int:
    """Return the total number of missing values in the DataFrame."""
    return int(df.isna().sum().sum())


def save_clean_data(df: pd.DataFrame, path: Path = CLEAN_DATA_PATH) -> None:
    """Save the cleaned dataset to a CSV file.

    Args:
        df: Cleaned DataFrame to save.
        path: Output path for the cleaned CSV file.

    Returns:
        None.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
