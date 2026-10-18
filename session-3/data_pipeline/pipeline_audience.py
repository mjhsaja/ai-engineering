"""
Sesi 3 — 3.4 Data Pipeline 

Isi bagian TODO sesuai instruksi. Setelah lengkap, jalankan script dengan:

    python pipeline.py

Input:  orders_dirty.csv
Output: orders_processed.csv
"""
from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def load_data(filepath: str) -> pd.DataFrame:
    """Baca CSV lokal ke DataFrame."""
    # TODO: pakai pd.read_csv(filepath), return DataFrame-nya
    pass


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Missing values + duplicates + format + noisy values."""
    # TODO: fill rating dengan mean

    # TODO: dropna subset=["city"]

    # TODO: fill product_review yang null dengan ""

    # TODO: drop_duplicates()

    # TODO: category.str.lower().str.strip()

    # TODO: pd.to_datetime(order_date, errors="coerce", format="mixed")

    # TODO: filter noisy values (price_idr > 0, quantity 1-100, rating 0-5)

    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Scaling + encoding + text cleaning."""
    # TODO: MinMaxScaler untuk [price_idr, rating] -> [price_norm, rating_norm]

    # TODO: pd.get_dummies untuk kolom "category" dengan prefix "cat"

    # TODO: buat review_clean (lowercase, hapus tanda baca, strip)

    return df


def save_data(df: pd.DataFrame, filepath: str) -> None:
    """Simpan ke CSV."""
    # TODO: df.to_csv(filepath, index=False)
    pass


def main() -> None:
    print("Mulai jalankan pipeline...")
    df = load_data("orders_dirty.csv")
    df = clean_data(df)
    df = transform_data(df)
    save_data(df, "orders_processed.csv")
    print("Pipeline selesai...")


if __name__ == "__main__":
    main()
