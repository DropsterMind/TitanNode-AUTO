```
 ________   __  __   _________  ______    _______   ______   _________  
/_______/\ /_/\/_/\ /________/\ /_____/\ /_______/\ /_____/\ /________/\ 
\::: _  \ \\:\ \:\ \\__.::.__\/\:::_ \ \\:\ _  \ \\:::_ \ \\__.::.__\/ 
 \::(_)  \ \\:\ \:\ \  \::\ \   \:\ \ \ \\::(_)  \/_\:\ \ \ \  \::\ \   
  \:: __  \ \\:\ \:\ \  \::\ \   \:\ \ \ \\::  _  \ \\:\ \ \ \  \::\ \  
   \:.\ \  \ \\:\_\:\ \  \::\ \   \:\_\ \ \\::(_)  \ \\:\_\ \ \  \::\ \ 
    \__\/\__\/ \_____\/   \__\/    \_____\/ \_______\/ \_____\/   \__\/
                     By: DropsterMind
```

# 🛠️ Titan Node AUTO BOT

Bot otomatis untuk menjalankan node **Titan** dengan dukungan multi-akun dan proksi.  
Dibuat untuk menyederhanakan proses farming poin secara efisien.

---

## ✨ Fitur

- 🤖 **Otomatisasi Penuh**  
  Login, pendaftaran node, dan pengiriman laporan pekerjaan (*heartbeat*) berjalan otomatis.

- 👥 **Dukungan Multi-Akun**  
  Jalankan beberapa akun Titan secara bersamaan dari satu mesin.

- 🌐 **Manajemen Proksi**
  - Gunakan proksi gratis yang diperbarui secara otomatis.
  - Gunakan proksi pribadi dari file `proxy.txt`.
  - Opsi untuk menjalankan tanpa proksi.
  - Rotasi proksi otomatis jika koneksi gagal.

- 🔄 **Token Auto-Refresh**  
  Bot akan memperbarui token akses secara otomatis sebelum kedaluwarsa.

- 🖥️ **Tampilan Log Modern**  
  Output terminal yang bersih, berwarna, dan mudah dibaca dengan simbol untuk setiap status (INFO, SUCCESS, ERROR).

- ⚙️ **Konfigurasi Mudah**  
  Cukup siapkan file `accounts.json` untuk data akun Anda.

---

## 📋 Prasyarat

- Python versi 3.8 atau lebih tinggi.
- Git

---

## 🚀 Instalasi & Konfigurasi

### 1. Clone Repositori

```bash
git clone https://github.com/DropsterMind/TitanNode-AUTO.git
cd TitanNode-AUTO
```

### 2. Instal Dependensi

```bash
pip install -r requirements.txt #or pip3 install -r requirements.txt
```

### 3. Konfigurasi Akun

Buat file baru bernama `accounts.json` di dalam direktori proyek, lalu isi dengan data akun Anda:

```json
[
  {
    "Email": "akun1@email.com",
    "Password": "password_akun_1"
  },
  {
    "Email": "akun2@email.com",
    "Password": "password_akun_2"
  }
]
```

Tambahkan objek akun sebanyak yang Anda butuhkan.

### 4. (Opsional) Konfigurasi Proksi Pribadi

Jika ingin menggunakan proksi pribadi (pilihan 2 saat menjalankan bot), buat file `proxy.txt` dan isi seperti ini:

```
http://user:pass@host:port
socks5://user:pass@host:port
ip:port
```

---

## ▶️ Cara Menjalankan Bot

Setelah semua konfigurasi selesai, jalankan bot dengan perintah:

```bash
python bot.py #or python3 bot.py
```

Saat pertama kali dijalankan, Anda akan diminta memilih mode proksi.

---

## 📝 File `requirements.txt`

Jika Anda belum memilikinya, buat file `requirements.txt` dengan isi:

```
aiohttp
aiohttp_socks
fake-useragent
colorama
pytz
```

---

## 📜 Disclaimer

Produk ini dibuat untuk **tujuan pendidikan**.  
Segala risiko yang timbul dari penggunaan bot ini menjadi **tanggung jawab pengguna sepenuhnya**.  
Gunakan dengan bijak.

---

## 💡 Kontribusi

Pull request, saran, dan masukan sangat dihargai!

---
