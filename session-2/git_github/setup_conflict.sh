#!/usr/bin/env bash
# Sesi 2 — Bagian 2.4: menyiapkan skenario MERGE CONFLICT untuk latihan.
# Jalankan skrip ini untuk membuat sebuah repo Git lokal yang PASTI menghasilkan
# conflict saat di-merge. Setelah itu, selesaikan conflict-nya (lihat README.md).
#
# Cara pakai:
#   bash setup_conflict.sh
#   cd konflik_demo
#   git merge feature-harga     # <-- di sini conflict akan muncul
#
# Catatan: pesan Git (logs/warning/error) sengaja dibiarkan dalam bahasa Inggris.

set -e

DIR="konflik_demo"
rm -rf "$DIR"
mkdir "$DIR"
cd "$DIR"

git init -q
git config user.name "Peserta Bootcamp"
git config user.email "peserta@rework.id"

# Commit awal di branch main
cat > produk.py <<'EOF'
# Data harga produk warung
harga = 25000
print("Harga produk:", harga)
EOF
git add produk.py
git commit -q -m "Initial commit: tambah produk.py"
git branch -M main   # pastikan branch utama bernama 'main'

# Buat branch feature yang mengubah baris yang sama
git checkout -q -b feature-harga
cat > produk.py <<'EOF'
# Data harga produk warung
harga = 30000
print("Harga produk:", harga)
EOF
git add produk.py
git commit -q -m "feature: naikkan harga jadi 30000"

# Kembali ke main dan ubah baris yang sama secara berbeda
git checkout -q main
cat > produk.py <<'EOF'
# Data harga produk warung
harga = 27000
print("Harga produk:", harga)
EOF
git add produk.py
git commit -q -m "main: sesuaikan harga jadi 27000"

echo ""
echo "Repo siap di folder '$DIR'."
echo "Sekarang jalankan:  cd $DIR && git merge feature-harga"
echo "Git akan melaporkan CONFLICT pada produk.py — itulah yang akan kita selesaikan."
