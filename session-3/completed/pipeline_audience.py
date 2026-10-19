"""
Sesi 3 — 3.4 Data Pipeline (Versi PESERTA)

Isi bagian TODO. Setelah lengkap, jalankan dengan:

    python pipeline.py

Input:  orders_dirty.csv
Output: orders_processed.csv
"""
from __future__ import annotations
import pandas as pd
# from sklearn.preprocessing import MinMaxScaler


def load_data(filepath: str) -> pd.DataFrame:
    """Baca CSV lokal ke DataFrame."""
    df = pd.read_csv(filepath)
    print(f"[load]  {filepath} -> {len(df)} baris")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Missing values + duplicates + format + noisy values."""
    before = len(df)

    # Missing values
    df["rating"] = df["rating"].fillna(df["rating"].mean())
    df = df.dropna(subset=["city"])
    df["product_review"] = df["product_review"].fillna("")

    # Duplicates
    df = df.drop_duplicates()

    # Format konsistensi
    df["category"] = df["category"].str.lower().str.strip()
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce", format="mixed"
    )

    # Buang noisy values (harga ≤0, quantity aneh, rating di luar 0–5)
    mask_bad = (
        (df["price_idr"] <= 0)
        | (df["quantity"] <= 0)
        | (df["quantity"] > 100)
        | (df["rating"] < 0)
        | (df["rating"] > 5)
    )
    df = df[~mask_bad].copy()

    print(f"[clean] {before} -> {len(df)} baris ({before - len(df)} dibuang)")

    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Scaling numerik + one-hot encoding kategori + text cleaning ringan."""
    # MinMax scaling
    # scaler = MinMaxScaler()
    # df[["price_norm", "rating_norm"]] = scaler.fit_transform(
    #     df[["price_idr", "rating"]]
    # )

    # One-hot encoding
    df = pd.get_dummies(df, columns=["category"], prefix="cat")

    # Text cleaning ringan
    df["review_clean"] = (
        df["product_review"]
        .astype(str)
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.strip()
    )

    print(f"[transform] {df.shape[1]} kolom setelah transformasi")
    return df


def save_data(df: pd.DataFrame, filepath: str) -> None:
    """Persistensi hasil ke CSV."""
    df.to_csv(filepath, index=False)
    print(f"[save]  {filepath}")



def main() -> None:
    df = load_data("./datasets/orders_dirty.csv")
    df = clean_data(df)
    df = transform_data(df)
    save_data(df, "./datasets/orders_processed.csv")
    print("Pipeline selesai ✓")


if __name__ == "__main__":
    main()
