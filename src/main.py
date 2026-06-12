from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import pandas as pd
import os
from src.cleaning import clean_data  # Uses your existing cleaning function

app = FastAPI(
    title="Hotel Booking REST API",
    description="API for accessing and updating hotel booking CSV datasets",
    version="1.0.0",
)

# File Paths
RAW_CSV = "data/raw/hotel_bookings.csv"
EXTENDED_CSV = "data/raw/hotel_bookings_extended.csv"
CLEAN_CSV = "data/processed/hotel_bookings_clean.csv"


# Simplistic Pydantic Model for POST requests
class BookingCreate(BaseModel):
    hotel: str = "City Hotel"
    is_canceled: int = 0
    lead_time: int = 15
    stays_in_weekend_nights: int = 1
    stays_in_week_nights: int = 2
    adults: int = 2
    children: float = 0.0
    babies: int = 0
    adr: float = 120.0
    total_of_special_requests: int = 1


@app.on_event("startup")
def startup_event():
    """Initializes the three CSV files when the server starts."""
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # 1. Create Extended CSV if it doesn't exist
    if not os.path.exists(EXTENDED_CSV) and os.path.exists(RAW_CSV):
        df = pd.read_csv(RAW_CSV)
        df.to_csv(EXTENDED_CSV, index=False)

    # 2. Create Cleaned CSV
    if not os.path.exists(CLEAN_CSV) and os.path.exists(EXTENDED_CSV):
        df = pd.read_csv(EXTENDED_CSV)
        clean_df = clean_data(df)
        clean_df.to_csv(CLEAN_CSV, index=False)


@app.get("/bookings/", tags=["Bookings"])
def read_bookings(skip: int = 0, limit: int = 5, hotel: Optional[str] = None):
    """GET Method: Returns records from the extended dataset."""
    if not os.path.exists(EXTENDED_CSV):
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(EXTENDED_CSV)
    if hotel:
        df = df[df["hotel"] == hotel]

    # Convert to JSON format and replace NaNs with empty strings for API safety
    records = df.iloc[skip : skip + limit].fillna("").to_dict(orient="records")
    return records


@app.post("/bookings/", tags=["Bookings"])
def create_booking(booking: BookingCreate):
    """POST Method: Appends new instance to extended CSV and updates cleaned CSV."""
    df = pd.read_csv(EXTENDED_CSV)
    new_row_df = pd.DataFrame([booking.model_dump()])

    # Automatically align columns (fills missing columns from raw CSV with None)
    for col in df.columns:
        if col not in new_row_df.columns:
            new_row_df[col] = None
    new_row_df = new_row_df[df.columns]

    # Append to Extended CSV
    new_row_df.to_csv(EXTENDED_CSV, mode="a", header=False, index=False)

    # Re-clean and overwrite Cleaned CSV
    updated_df = pd.read_csv(EXTENDED_CSV)
    clean_df = clean_data(updated_df)
    clean_df.to_csv(CLEAN_CSV, index=False)

    return {
        "status": "success",
        "message": "Booking added to extended and clean CSVs.",
        "data": booking.model_dump(),
    }
