"""
Contoh implementasi dasar model LOKAL (Qwen & DeepSeek) melalui Ollama.
Model berjalan di komputer sendiri memakai GPU lokal: tanpa API key, tanpa biaya
per token, dan data tidak keluar dari komputer.

Struktur dan contoh dibuat setara dengan contoh_qwen.py dan contoh_deepseek.py.

Persiapan:
    1. Install Ollama dari https://ollama.com dan pastikan servernya berjalan
       (aplikasi Ollama aktif, atau jalankan `ollama serve` di terminal).

    2. Unduh model (pilih ukuran yang muat di VRAM GPU Anda), contoh:
         ollama pull qwen3:8b
         ollama pull deepseek-r1:8b
       Cek model yang sudah ada:  ollama list

    3. Install package Python:
         pip install -U ollama python-dotenv

    4. (Opsional) Atur di file `.env`, kalau tidak diisi dipakai nilai default:
         OLLAMA_HOST=http://localhost:11434
         OLLAMA_MODEL_QWEN=qwen3:8b
         OLLAMA_MODEL_DEEPSEEK=deepseek-r1:8b

Jalankan:
    python contoh_ollama.py qwen          # pakai model Qwen
    python contoh_ollama.py deepseek      # pakai model DeepSeek
    python contoh_ollama.py qwen3:14b     # atau tulis langsung nama model Ollama
"""

import os
import re
import sys

from dotenv import load_dotenv
from ollama import Client, ResponseError
from pydantic import BaseModel  # sudah terpasang bersama ollama

load_dotenv()

HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
PILIHAN_MODEL = {
    "qwen": os.getenv("OLLAMA_MODEL_QWEN", "qwen3:8b"),
    "deepseek": os.getenv("OLLAMA_MODEL_DEEPSEEK", "deepseek-r1:8b"),
}

# Model dipilih dari argumen command line (default: qwen)
pilihan = sys.argv[1] if len(sys.argv) > 1 else "qwen"
MODEL = PILIHAN_MODEL.get(pilihan.lower(), pilihan)

# Mode "berpikir" (thinking) untuk model reasoning seperti deepseek-r1 dan qwen3.
#   None  = ikuti bawaan model
#   False = matikan, jawaban lebih cepat
#   True  = aktifkan, proses berpikir dikembalikan terpisah di message.thinking
# Catatan: think=True hanya untuk model yang mendukung thinking.
THINK = None

# Parameter tambahan bila model tidak muat di VRAM atau ingin konteks lebih panjang:
#   "num_ctx": 8192   -> panjang konteks (makin besar makin banyak VRAM terpakai)
OPSI_DASAR = {}

client = Client(host=HOST)


def chat(**kwargs):
    """Bungkus client.chat agar parameter think hanya dikirim bila diatur."""
    if THINK is not None:
        kwargs["think"] = THINK
    return client.chat(model=MODEL, **kwargs)


def bersihkan(teks: str) -> str:
    """Buang blok <think>...</think> bila model menyisipkannya di jawaban."""
    return re.sub(r"<think>.*?</think>", "", teks or "", flags=re.DOTALL).strip()


# ---------------------------------------------------------------------------
# 0. Cek koneksi ke server Ollama & ketersediaan model
# ---------------------------------------------------------------------------
def cek_model():
    terpasang = [m.model for m in client.list().models]
    if MODEL not in terpasang:
        print(f"Model '{MODEL}' belum terpasang. Jalankan:  ollama pull {MODEL}")
        print("Model yang sudah ada:", ", ".join(terpasang) or "(belum ada)")
        sys.exit(1)
    print(f"Memakai model lokal: {MODEL}  (server: {HOST})\n")


# ---------------------------------------------------------------------------
# 1. Generate teks sederhana
#    Panggilan pertama sedikit lebih lama karena model dimuat ke GPU dulu.
# ---------------------------------------------------------------------------
def contoh_generate_teks():
    print("=== 1. Generate teks sederhana ===")
    response = chat(
        messages=[
            {"role": "user",
             "content": "Jelaskan apa itu inventory turnover ratio dalam 3 kalimat."}
        ],
        options=OPSI_DASAR,
    )
    print(bersihkan(response.message.content))


# ---------------------------------------------------------------------------
# 2. Generate dengan konfigurasi (system prompt, temperature, dll.)
#    Di Ollama, parameter sampling dikirim lewat `options`.
#    max_tokens di Ollama bernama `num_predict`.
# ---------------------------------------------------------------------------
def contoh_dengan_konfigurasi():
    print("\n=== 2. Dengan system prompt & konfigurasi ===")
    response = chat(
        messages=[
            {"role": "system",
             "content": "Anda adalah konsultan manajemen persediaan. "
                        "Jawab singkat, berbentuk poin, dalam Bahasa Indonesia."},
            {"role": "user",
             "content": "Berikan 3 tips mengurangi stok mati (dead stock) di gudang."},
        ],
        options={**OPSI_DASAR, "temperature": 0.4, "num_predict": 1000},
    )
    print(bersihkan(response.message.content))


# ---------------------------------------------------------------------------
# 3. Streaming (teks muncul bertahap)
# ---------------------------------------------------------------------------
def contoh_streaming():
    print("\n=== 3. Streaming ===")
    stream = chat(
        messages=[
            {"role": "user",
             "content": "Tuliskan paragraf singkat tentang peran semen dalam pembangunan."}
        ],
        options=OPSI_DASAR,
        stream=True,
    )
    for chunk in stream:
        if chunk.message.content:
            print(chunk.message.content, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# 4. Chat multi-turn
#    Riwayat disimpan sendiri lalu dikirim ulang setiap request.
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

        response = chat(messages=riwayat, options=OPSI_DASAR)
        jawaban = bersihkan(response.message.content)
        print(f"Model : {jawaban}")

        # Simpan jawaban saja (tanpa proses berpikir) agar konteks tetap ringkas
        riwayat.append({"role": "assistant", "content": jawaban})


# ---------------------------------------------------------------------------
# 5. Output terstruktur (JSON sesuai skema)
#    Ollama bisa memaksa output mengikuti skema JSON lewat parameter `format`.
# ---------------------------------------------------------------------------
class Barang(BaseModel):
    nama: str
    kategori: str
    satuan: str


class DaftarBarang(BaseModel):
    barang: list[Barang]


def contoh_output_json():
    print("\n=== 5. Output JSON terstruktur ===")
    response = chat(
        messages=[
            {"role": "user",
             "content": "Buat 3 contoh barang persediaan di pabrik semen. "
                        "Jawab dalam format JSON."}
        ],
        format=DaftarBarang.model_json_schema(),
        options={**OPSI_DASAR, "temperature": 0},  # 0 = output lebih stabil untuk data
    )
    teks_json = bersihkan(response.message.content)
    print(teks_json)                                         # string JSON mentah
    hasil = DaftarBarang.model_validate_json(teks_json)      # divalidasi jadi objek Pydantic
    for b in hasil.barang:
        print(f"- {b.nama} ({b.kategori}, satuan: {b.satuan})")


# ---------------------------------------------------------------------------
# 6. Pemakaian token, kecepatan, & penggunaan GPU
#    Karena lokal, tidak ada biaya per token. Yang penting dipantau adalah
#    kecepatan (token/detik) dan apakah model benar-benar berjalan di GPU.
# ---------------------------------------------------------------------------
def contoh_statistik():
    print("\n=== 6. Token, kecepatan & GPU ===")
    response = chat(
        messages=[{"role": "user",
                   "content": "Sebutkan 5 jenis semen beserta kegunaannya."}],
        options=OPSI_DASAR,
    )
    token_output = response.eval_count or 0
    detik_output = (response.eval_duration or 0) / 1e9   # nanodetik -> detik

    print(f"Token input  : {response.prompt_eval_count}")
    print(f"Token output : {token_output}")
    print(f"Total waktu  : {(response.total_duration or 0) / 1e9:.1f} detik")
    if detik_output:
        print(f"Kecepatan    : {token_output / detik_output:.1f} token/detik")

    # Cek berapa bagian model yang dimuat ke VRAM GPU (setara `ollama ps`)
    for m in client.ps().models:
        if m.model == MODEL and m.size:
            persen_gpu = 100 * (m.size_vram or 0) / m.size
            print(f"Memori model : {m.size / 1e9:.1f} GB, "
                  f"{persen_gpu:.0f}% di GPU (VRAM {(m.size_vram or 0) / 1e9:.1f} GB)")
            if persen_gpu < 100:
                print("  Sebagian model berjalan di CPU sehingga lebih lambat. "
                      "Pertimbangkan model yang lebih kecil atau num_ctx lebih kecil.")


if __name__ == "__main__":
    try:
        cek_model()
        contoh_generate_teks()
        contoh_dengan_konfigurasi()
        contoh_streaming()
        contoh_chat()
        contoh_output_json()
        contoh_statistik()
    except ConnectionError:
        print(f"\nTidak bisa terhubung ke Ollama di {HOST}. "
              "Pastikan aplikasi Ollama berjalan (atau jalankan `ollama serve`).")
    except ResponseError as e:
        print(f"\nError dari Ollama (status {e.status_code}): {e.error}")
