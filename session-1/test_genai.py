"""
Contoh implementasi dasar package `google-genai` (Google Gen AI SDK untuk Python).

Persiapan:
    pip install -U google-genai

    # Buat API key gratis di https://aistudio.google.com/apikey lalu set:
    export GEMINI_API_KEY="isi_api_key_anda"        # Linux / macOS
    setx GEMINI_API_KEY "isi_api_key_anda"          # Windows (buka terminal baru setelahnya)

Jalankan:
    python contoh_google_genai.py
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ganti nama model bila perlu (cek daftar model terbaru di dokumentasi Gemini API)
MODEL = "gemini-3.6-flash"

# Client otomatis membaca API key dari environment variable GEMINI_API_KEY.
# Alternatif: genai.Client(api_key="isi_api_key_anda")
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# 1. Generate teks sederhana
# ---------------------------------------------------------------------------
def contoh_generate_teks():
    print("=== 1. Generate teks sederhana ===")
    response = client.models.generate_content(
        model=MODEL,
        contents="Jelaskan apa itu inventory turnover ratio dalam 3 kalimat.",
    )
    print(response.text)


# ---------------------------------------------------------------------------
# 2. Generate dengan konfigurasi (system instruction, temperature, dll.)
# ---------------------------------------------------------------------------
def contoh_dengan_konfigurasi():
    print("\n=== 2. Dengan system instruction & konfigurasi ===")
    response = client.models.generate_content(
        model=MODEL,
        contents="Berikan 3 tips mengurangi stok mati (dead stock) di gudang.",
        config=types.GenerateContentConfig(
            system_instruction="Anda adalah konsultan manajemen persediaan. "
                               "Jawab singkat, berbentuk poin, dalam Bahasa Indonesia.",
            temperature=0.4,         # 0 = lebih konsisten, 2 = lebih kreatif
            max_output_tokens=500,
        ),
    )
    print(response.text)


# ---------------------------------------------------------------------------
# 3. Streaming (teks muncul bertahap)
# ---------------------------------------------------------------------------
def contoh_streaming():
    print("\n=== 3. Streaming ===")
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents="Tuliskan paragraf singkat tentang peran semen dalam pembangunan.",
    ):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# 4. Chat multi-turn (riwayat percakapan disimpan otomatis)
# ---------------------------------------------------------------------------
def contoh_chat():
    print("\n=== 4. Chat multi-turn ===")
    chat = client.chats.create(model=MODEL)

    pertanyaan = [
        "Apa itu metode EOQ (Economic Order Quantity)?",
        "Tuliskan rumusnya.",                     # merujuk ke jawaban sebelumnya
        "Beri contoh hitungan dengan angka sederhana.",
    ]
    for p in pertanyaan:
        print(f"\nAnda : {p}")
        response = chat.send_message(p)
        print(f"Gemini: {response.text}")


# ---------------------------------------------------------------------------
# 5. Output terstruktur (JSON sesuai skema)
# ---------------------------------------------------------------------------
def contoh_output_json():
    print("\n=== 5. Output JSON terstruktur ===")
    from pydantic import BaseModel  # sudah terpasang bersama google-genai

    class Barang(BaseModel):
        nama: str
        kategori: str
        satuan: str

    response = client.models.generate_content(
        model=MODEL,
        contents="Buat 3 contoh barang persediaan di pabrik semen.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Barang],
        ),
    )
    print(response.text)          # string JSON mentah
    barang_list = response.parsed  # sudah jadi list[Barang]
    for b in barang_list:
        print(f"- {b.nama} ({b.kategori}, satuan: {b.satuan})")


# ---------------------------------------------------------------------------
# 6. Menghitung token (berguna untuk estimasi biaya/kuota)
# ---------------------------------------------------------------------------
def contoh_hitung_token():
    print("\n=== 6. Hitung token ===")
    hasil = client.models.count_tokens(
        model=MODEL,
        contents="Berapa banyak token di kalimat ini?",
    )
    print(f"Jumlah token: {hasil.total_tokens}")


if __name__ == "__main__":
    try:
        contoh_generate_teks()
        contoh_dengan_konfigurasi()
        contoh_streaming()
        contoh_chat()
        contoh_output_json()
        contoh_hitung_token()
    except Exception as e:
        print(f"\nTerjadi error: {e}")
        print("Pastikan GEMINI_API_KEY sudah di-set dan nama model masih tersedia.")
