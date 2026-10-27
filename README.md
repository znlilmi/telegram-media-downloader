# 📥 Telegram Media Downloader Bot (100% Gratis)

Bot Telegram untuk mengunduh video dan foto dari berbagai platform media sosial (**TikTok**, **Instagram Reels/Post**, **Twitter / X**, **YouTube Shorts**, **Facebook**, dll.) secara gratis tanpa watermark pihak ketiga berbayar.

---

## 🛠️ Persiapan

### 1. Dapatkan Token Bot Telegram
1. Buka aplikasi Telegram dan cari **`@BotFather`**.
2. Kirim perintah `/newbot`.
3. Masukkan nama bot kamu (misalnya: `MyMediaDownloaderBot`).
4. Masukkan username bot berakhiran `bot` (misalnya: `mymedia_downloader_bot`).
5. Kamu akan mendapatkan **HTTP API Token** (contoh: `7123456789:AAFlkBx....`).
6. Buka file `.env` di folder ini dan ganti `YOUR_TELEGRAM_BOT_TOKEN_HERE` dengan token tersebut:
   ```env
   BOT_TOKEN=7123456789:AAFlkBx....
   ```

---

## 🚀 Menjalankan di Laptop / Komputer Lokal

1. Buka terminal (PowerShell atau Command Prompt) di folder ini:
   ```powershell
   cd c:\laragon\www\telegram-media-downloader
   ```

2. (Opsional tapi disarankan) Buat virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install library yang dibutuhkan:
   ```powershell
   pip install -r requirements.txt
   ```

4. Jalankan bot:
   ```powershell
   python bot.py
   ```

5. Buka bot kamu di Telegram, ketik `/start`, lalu kirim tautan TikTok/Instagram/X/YouTube untuk mencoba mengunduh!

---

## 🌐 Menjalankan Online 24/7 Gratis (Tanpa Nyalakan Laptop)

Untuk menjalankan bot terus-menerus tanpa harus menyalakan komputer, kamu bisa menggunakan layanan cloud hosting gratis:

### Opsi 1: Render.com (Gratis & Mudah)
1. Buat akun di [Render.com](https://render.com) dan hubungkan akun GitHub kamu.
2. Unggah folder proyek ini ke repositori baru di GitHub (`git init`, `git add .`, `git commit -m "initial"`, `git push`).
3. Di Dashboard Render, klik **New +** -> **Background Worker**.
4. Hubungkan ke repositori GitHub proyek kamu.
5. Konfigurasi:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
6. Pada bagian **Environment Variables**, tambahkan:
   - Key: `BOT_TOKEN`
   - Value: `<token bot telegram kamu>`
7. Klik **Create Background Worker**. Bot kamu sekarang online 24 jam nonstop!

### Opsi 2: Koyeb atau Fly.io
- Prinsipnya sama, gunakan perintah `python bot.py` sebagai worker background service dan masukkan variable `BOT_TOKEN`.

---

## 📂 Struktur File

```
telegram-media-downloader/
├── bot.py             # Script utama bot Telegram
├── requirements.txt   # Daftar dependensi Python
├── Procfile           # Konfigurasi deployment cloud worker
├── .env.example       # Template konfigurasi environment
├── .env               # Tempat menyimpan token bot kamu
├── .gitignore         # File yang dikecualikan dari Git
└── README.md          # Panduan lengkap ini
```
