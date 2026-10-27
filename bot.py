import os
import sys
import glob
import logging
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv

# Pastikan output terminal mendukung UTF-8 di Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from telegram import Update
from telegram.constants import ChatAction
from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# Load file .env
load_dotenv()

# Logging konfigurasi
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Konfigurasi Token & Folder
BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Batas maksimal kirim via bot Telegram standar (50 MB)
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Regex untuk mendeteksi link/URL
URL_REGEX = re.compile(
    r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"https?:\/\/[^\s]+)"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk perintah /start"""
    user_name = update.effective_user.first_name if update.effective_user else "Teman"
    welcome_text = (
        f"👋 Halo *{user_name}*!\n\n"
        "Saya adalah bot pengunduh media gratis (100% Free).\n\n"
        "✨ *Dukungan Platform:*\n"
        "• TikTok (tanpa watermark)\n"
        "• Instagram (Reels, Post, Story)\n"
        "• Twitter / X\n"
        "• YouTube Shorts & Video\n"
        "• Facebook, Pinterest, Reddit, dll.\n\n"
        "🚀 *Cara Pakai:*\n"
        "Cukup salin dan kirimkan tautan/link video atau foto ke sini!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk perintah /help"""
    help_text = (
        "📖 *Panduan Bantuan:*\n\n"
        "1. Salin tautan dari aplikasi (TikTok, IG, X, YT, dll).\n"
        "2. Tempel dan kirim tautan ke obrolan ini.\n"
        "3. Tunggu beberapa detik, bot akan mengunduh dan mengirimkan medianya ke kamu.\n\n"
        "⚠️ *Catatan:*\n"
        "- Batas maksimal file bot Telegram adalah 50MB.\n"
        "- Pastikan akun pemilik video tidak dikunci (private)."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


def download_media_sync(url: str, output_prefix: str) -> list[str]:
    """
    Fungsi sinkron untuk download media menggunakan yt-dlp.
    Dijalankan di thread terpisah agar tidak memblokir event loop async.
    """
    outtmpl = str(DOWNLOAD_DIR / f"{output_prefix}_%(autonumber)s.%(ext)s")
    
    ydl_opts = {
        "outtmpl": outtmpl,
        # Pilih format terbaik yang ukurannya masuk akal (mp4/webm/foto)
        "format": "best[filesize<50M]/bestvideo[filesize<40M]+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        # Menghindari blokir atau format aneh
        "nocheckcertificate": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Cari semua file yang baru saja didownload dengan prefix ini
    pattern = str(DOWNLOAD_DIR / f"{output_prefix}_*")
    downloaded_files = glob.glob(pattern)
    return downloaded_files


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pesan masuk yang berisi URL"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    match = URL_REGEX.search(text)
    if not match:
        await update.message.reply_text(
            "⚠️ Mohon kirimkan tautan URL yang valid (contoh: link TikTok, Instagram, Twitter/X, atau YouTube)."
        )
        return

    url = match.group(0)
    chat_id = update.effective_chat.id
    status_msg = await update.message.reply_text("🔍 Sedang memproses dan mengunduh media...")

    # Buat ID unik untuk penamaan file download sementara
    unique_id = f"{chat_id}_{update.message.message_id}"
    downloaded_files = []

    try:
        # Kirim indikator typing
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        # Jalankan yt-dlp di executor background thread agar bot tetap responsif
        downloaded_files = await asyncio.to_thread(download_media_sync, url, unique_id)

        if not downloaded_files:
            await status_msg.edit_text(
                "❌ Gagal mengunduh media dari tautan tersebut.\n"
                "Kemungkinan tautan bersifat privat, telah dihapus, atau format tidak didukung."
            )
            return

        # Update status saat siap kirim
        await status_msg.edit_text("📤 Mengunggah media ke Telegram...")

        for file_path in downloaded_files:
            file_size = os.path.getsize(file_path)
            
            # Cek limit ukuran Telegram Bot (50MB)
            if file_size > MAX_FILE_SIZE_BYTES:
                await update.message.reply_text(
                    f"⚠️ Ukuran file ({file_size / (1024*1024):.1f} MB) melebihi batas maksimal 50 MB Telegram Bot."
                )
                continue

            file_ext = Path(file_path).suffix.lower()

            if file_ext in [".mp4", ".mov", ".mkv", ".webm"]:
                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
                with open(file_path, "rb") as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption="✅ Berhasil diunduh!",
                        supports_streaming=True,
                        read_timeout=300,
                        write_timeout=300,
                    )
            elif file_ext in [".jpg", ".jpeg", ".png", ".webp"]:
                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                with open(file_path, "rb") as photo_file:
                    await update.message.reply_photo(
                        photo=photo_file,
                        caption="✅ Berhasil diunduh!",
                        read_timeout=120,
                        write_timeout=120,
                    )
            elif file_ext in [".mp3", ".m4a", ".wav", ".aac"]:
                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                with open(file_path, "rb") as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        caption="✅ Berhasil diunduh!",
                        read_timeout=300,
                        write_timeout=300,
                    )
            else:
                # Format lainnya kirim sebagai dokumen
                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
                with open(file_path, "rb") as doc_file:
                    await update.message.reply_document(
                        document=doc_file,
                        caption="✅ Berhasil diunduh!",
                        read_timeout=300,
                        write_timeout=300,
                    )

        # Hapus pesan status jika pengiriman berhasil
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error handling URL {url}: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Terjadi kesalahan saat memproses media:\n`{str(e)[:200]}`",
            parse_mode="Markdown",
        )
    finally:
        # Pembersihan file sementara agar penyimpanan tidak penuh
        for f in downloaded_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as err:
                logger.warning(f"Gagal menghapus file sementara {f}: {err}")


def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("\n" + "=" * 60)
        print("❌ ERROR: BOT_TOKEN belum diset di file .env!")
        print("1. Buka file .env")
        print("2. Masukkan token bot yang didapatkan dari @BotFather di Telegram")
        print("   Contoh: BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("=" * 60 + "\n")
        return

    print("🤖 Memulai Bot Telegram Media Downloader...")
    # Timeout 300 detik (5 menit) agar upload file video besar ke Telegram tidak timed out
    request_config = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=300.0,
        write_timeout=300.0,
        pool_timeout=60.0,
    )
    app = ApplicationBuilder().token(BOT_TOKEN).request(request_config).build()

    # Daftarkan handler
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot siap! Menunggu pesan masuk...")
    app.run_polling()


if __name__ == "__main__":
    main()
