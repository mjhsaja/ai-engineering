"""
Contoh implementasi dasar package `anthropic` (Claude SDK untuk Python).
Struktur dan contoh dibuat setara dengan contoh_google_genai.py.

Persiapan:
    pip install -U anthropic python-dotenv

    # Buat API key di https://platform.claude.com (menu API Keys), lalu buat
    # file bernama `.env` di folder yang sama dengan skrip ini, isinya:
    ANTHROPIC_API_KEY=isi_api_key_anda

    # PENTING: tambahkan `.env` ke .gitignore agar API key tidak ikut ter-upload.

Jalankan:
    python contoh_anthropic_claude.py
"""

import os

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel  # sudah terpasang bersama anthropic

# Muat variabel dari file .env ke environment (os.environ).
# Secara default, variabel yang sudah ada di environment TIDAK ditimpa.
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise SystemExit("ANTHROPIC_API_KEY tidak ditemukan. "
                     "Pastikan file .env ada dan berisi ANTHROPIC_API_KEY=...")

# Pilihan model: claude-haiku-5-5 (cepat & murah), claude-sonnet-5-5 (seimbang),
# claude-opus-5-5 (paling kuat). Cek daftar terbaru di dokumentasi Claude.
MODEL = "claude-sonnet-5-5"

# API key diambil dari .env melalui load_dotenv() di atas
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def ambil_teks(message) -> str:
    """Gabungkan semua blok teks dari respons Claude menjadi satu string."""
    return "".join(block.text for block in message.content if block.type == "text")


# ---------------------------------------------------------------------------
# 1. Generate teks sederhana
#    (setara client.models.generate_content di google-genai)
# ---------------------------------------------------------------------------
def contoh_generate_teks():
    print("=== 1. Generate teks sederhana ===")
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,  # WAJIB diisi di Claude
        messages=[
            {"role": "user",
             "content": "Jelaskan apa itu inventory turnover ratio dalam 3 kalimat."}
        ],
    )
    print(ambil_teks(message))


# ---------------------------------------------------------------------------
# 2. Generate dengan konfigurasi (system prompt, temperature, dll.)
#    Di Claude, parameter ini langsung jadi argumen, tanpa objek config terpisah.
# ---------------------------------------------------------------------------
def contoh_dengan_konfigurasi():
    print("\n=== 2. Dengan system prompt & konfigurasi ===")
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system="Anda adalah konsultan manajemen persediaan. "
               "Jawab singkat, berbentuk poin, dalam Bahasa Indonesia.",
        temperature=0.4,  # rentang 0 - 1 (0 = lebih konsisten, 1 = lebih kreatif)
        messages=[
            {"role": "user",
             "content": "Berikan 3 tips mengurangi stok mati (dead stock) di gudang."}
        ],
    )
    print(ambil_teks(message))


# ---------------------------------------------------------------------------
# 3. Streaming (teks muncul bertahap)
# ---------------------------------------------------------------------------
def contoh_streaming():
    print("\n=== 3. Streaming ===")
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {"role": "user",
             "content": "Tuliskan paragraf singkat tentang peran semen dalam pembangunan."}
        ],
    ) as stream:
        for teks in stream.text_stream:
            print(teks, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# 4. Chat multi-turn
#    Claude tidak menyimpan riwayat otomatis: kita simpan sendiri di list
#    `riwayat`, lalu kirim ulang seluruhnya di setiap request.
# ---------------------------------------------------------------------------
def contoh_chat():
    print("\n=== 4. Chat multi-turn ===")
    riwayat = []

    pertanyaan = [
        "Apa itu metode EOQ (Economic Order Quantity)?",
        "Tuliskan rumusnya.",                     # merujuk ke jawaban sebelumnya
        "Beri contoh hitungan dengan angka sederhana.",
    ]
    for p in pertanyaan:
        print(f"\nAnda  : {p}")
        riwayat.append({"role": "user", "content": p})

        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=riwayat,
        )
        jawaban = ambil_teks(message)
        print(f"Claude: {jawaban}")

        # Simpan jawaban Claude agar pertanyaan berikutnya punya konteks
        riwayat.append({"role": "assistant", "content": jawaban})


# ---------------------------------------------------------------------------
# 5. Output terstruktur (JSON sesuai skema)
#    Caranya: definisikan sebuah "tool" dengan skema JSON, lalu paksa Claude
#    memakai tool itu. Isi argumen tool = data terstruktur yang kita mau.
# ---------------------------------------------------------------------------
class Barang(BaseModel):
    nama: str
    kategori: str
    satuan: str


class DaftarBarang(BaseModel):
    barang: list[Barang]


def contoh_output_json():
    print("\n=== 5. Output JSON terstruktur ===")
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[{
            "name": "simpan_daftar_barang",
            "description": "Simpan daftar barang persediaan.",
            "input_schema": DaftarBarang.model_json_schema(),
        }],
        tool_choice={"type": "tool", "name": "simpan_daftar_barang"},  # paksa pakai tool
        messages=[
            {"role": "user",
             "content": "Buat 3 contoh barang persediaan di pabrik semen."}
        ],
    )

    data_mentah = next(b.input for b in message.content if b.type == "tool_use")
    print(data_mentah)                                   # dict mentah
    hasil = DaftarBarang.model_validate(data_mentah)     # divalidasi jadi objek Pydantic
    for b in hasil.barang:
        print(f"- {b.nama} ({b.kategori}, satuan: {b.satuan})")


# ---------------------------------------------------------------------------
# 6. Menghitung token (berguna untuk estimasi biaya/kuota)
# ---------------------------------------------------------------------------
def contoh_hitung_token():
    print("\n=== 6. Hitung token ===")
    hasil = client.messages.count_tokens(
        model=MODEL,
        messages=[{"role": "user", "content": "Berapa banyak token di kalimat ini?"}],
    )
    print(f"Jumlah token input: {hasil.input_tokens}")


if __name__ == "__main__":
    try:
        contoh_generate_teks()
        contoh_dengan_konfigurasi()
        contoh_streaming()
        contoh_chat()
        contoh_output_json()
        contoh_hitung_token()
    except anthropic.AuthenticationError:
        print("\nAPI key tidak valid. Periksa nilai ANTHROPIC_API_KEY di file .env.")
    except anthropic.NotFoundError:
        print(f"\nModel '{MODEL}' tidak ditemukan. Cek nama model di dokumentasi Claude.")
    except anthropic.APIError as e:
        print(f"\nTerjadi error dari API: {e}")
