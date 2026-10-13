"""
Sesi 1 - Demo: FAQ Bot Sederhana (Rule-Based)
================================================
Versi MENTOR (kode lengkap)

Tujuan demo ini: menunjukkan secara KONKRET empat komponen arsitektur
sistem AI yang sudah dibahas di Slide 18-21, lewat contoh kecil yang
bisa langsung dijalankan dan dicoba di kelas.

    1. PENGGUNA          -> mengetik pertanyaan
    2. APPLICATION LAYER  -> menerima & membersihkan input, mengirim ke "model"
    3. MODEL / "API" AI   -> mesin pencocokan aturan (rule-based) yang
                             mencari jawaban paling relevan
    4. KEMBALI KE PENGGUNA -> jawaban ditampilkan balik ke pengguna

Catatan: bot ini SENGAJA dibuat rule-based (bukan memanggil Gemini API)
supaya bisa dijalankan tanpa API key, dan supaya komponen "Model / API AI"
terlihat jelas sebagai satu blok kode yang bisa diganti nanti dengan
panggilan API sungguhan (persis seperti test_gemini.py di live coding
sebelumnya) tanpa mengubah arsitektur di sekelilingnya.

Cara menjalankan:
    (venv) $ python mentor_faq_bot.py
"""

# =========================================================
# KOMPONEN 3: MODEL / "API" AI
# (di produksi sungguhan, blok ini yang biasanya diganti
#  dengan pemanggilan API seperti Gemini)
# =========================================================

FAQ_DATABASE = {
    "jadwal": "Bootcamp berlangsung setiap Sabtu, 15 sesi total, masing-masing 2 jam 30 menit.",
    "sertifikat": "Sertifikat kelulusan diberikan setelah menyelesaikan minimal 12 dari 15 sesi.",
    "tugas": "Setiap sesi punya coding task singkat yang dikerjakan langsung di kelas atau sebagai latihan mandiri.",
    "mentor": "Setiap sesi dipandu oleh satu mentor berpengalaman di bidang AI Engineering.",
    "biaya": "Untuk info biaya dan pendaftaran, silakan hubungi tim admin lewat email atau Slack.",
}

FALLBACK_ANSWER = (
    "Maaf, saya belum punya jawaban untuk pertanyaan itu. "
    "Coba tanyakan seputar: jadwal, sertifikat, tugas, mentor, atau biaya."
)


def cari_jawaban(pertanyaan_bersih: str) -> str:
    """
    Model rule-based sederhana: cocokkan kata kunci di pertanyaan
    dengan kata kunci di FAQ_DATABASE. Kalau ada yang cocok, kembalikan
    jawabannya. Kalau tidak ada yang cocok, kembalikan jawaban fallback.
    """
    for kata_kunci, jawaban in FAQ_DATABASE.items():
        if kata_kunci in pertanyaan_bersih:
            return jawaban
    return FALLBACK_ANSWER


# =========================================================
# KOMPONEN 2: APPLICATION LAYER
# (menerima input mentah, membersihkan/memproses,
#  mengoper ke "model", lalu meneruskan hasilnya)
# =========================================================

def application_layer(pertanyaan_mentah: str) -> str:
    # pra-proses sederhana: ubah ke huruf kecil supaya pencocokan
    # kata kunci tidak peduli besar/kecil huruf
    pertanyaan_bersih = pertanyaan_mentah.strip().lower()

    if not pertanyaan_bersih:
        return "Sepertinya pertanyaan Anda kosong — coba ketik ulang ya."

    jawaban = cari_jawaban(pertanyaan_bersih)
    return jawaban


# =========================================================
# KOMPONEN 1 & 4: PENGGUNA <-> KEMBALI KE PENGGUNA
# (loop utama: menerima input dari pengguna,
#  menampilkan jawaban yang sudah diproses)
# =========================================================

def main():
    print("=" * 50)
    print("FAQ Bot Bootcamp ReWork (rule-based demo)")
    print("Ketik 'keluar' untuk mengakhiri.")
    print("=" * 50)

    while True:
        pertanyaan = input("\nAnda: ")

        if pertanyaan.strip().lower() == "keluar":
            print("Bot: Sampai jumpa di sesi berikutnya!")
            break

        jawaban = application_layer(pertanyaan)
        print(f"Bot: {jawaban}")


if __name__ == "__main__":
    main()
