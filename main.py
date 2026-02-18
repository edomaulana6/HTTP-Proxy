import telebot
import os
import time
import threading
import subprocess
import re

def clean_string(text):
    """Menghapus karakter tak terlihat, spasi liar, dan simbol aneh."""
    if not text:
        return ""
    # Menghapus karakter kontrol (non-printable) dan spasi di ujung
    cleaned = "".join(char for char in text if char.isprintable())
    # Hanya ambil karakter alphanumeric dan simbol yang valid untuk token Telegram (angka, huruf, titik dua, underscore, dash)
    cleaned = re.sub(r'[^a-zA-Z0-9:_-]', '', cleaned)
    return cleaned.strip()

# --- EKSTRAKSI & PEMBERSIHAN TOKEN ---
# Mengambil dari Environment Variable Koyeb
RAW_TOKEN = os.getenv("TOKEN", "")
TOKEN = clean_string(RAW_TOKEN)

# --- VALIDASI & DIAGNOSTIK ---
if not TOKEN:
    print("❌ ERROR: Variabel TOKEN kosong di Koyeb! Cek tab Environment Variables.")
    exit(1)

if ":" not in TOKEN:
    print(f"❌ ERROR: Token tidak valid (Tidak ada ':'). Isi yang terbaca: {TOKEN[:5]}***")
    exit(1)

try:
    bot = telebot.TeleBot(TOKEN)
    user_info = bot.get_me()
    print(f"✅ LOGIN SUKSES: @{user_info.username} siap digunakan!")
except Exception as e:
    print(f"❌ KREDENSIAL SALAH: {e}")
    exit(1)

# --- FITUR RESET MEMORY (HAPUS FILE SETIAP 60 DETIK) ---
def memory_reset_manager():
    while True:
        time.sleep(60)
        current_files = os.listdir(".")
        for file in current_files:
            # Hapus file video yang berawalan 'v_'
            if file.startswith("v_") and file.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(file)
                    print(f"🗑️ Memory Reset: {file} dihapus otomatis.")
                except:
                    pass

threading.Thread(target=memory_reset_manager, daemon=True).start()

# --- HANDLER DOWNLOAD ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_download(m):
    msg = bot.reply_to(m, "⏳ Memproses link, mohon tunggu...")
    # Nama file unik menggunakan ID chat dan timestamp
    output_name = f"v_{m.chat.id}_{int(time.time())}.mp4"
    
    try:
        # Perintah yt-dlp yang sudah dioptimasi
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]',
            '--no-playlist',
            '-o', output_name,
            m.text
        ]
        
        # Eksekusi download
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_name):
            with open(output_name, "rb") as video:
                bot.send_video(m.chat.id, video, caption="✨ Berhasil diunduh!")
            os.remove(output_name) # Hapus langsung setelah terkirim
        else:
            bot.edit_message_text(f"❌ Gagal unduh. Log: {result.stderr[:50]}", m.chat.id, msg.message_id)
            
    except Exception as e:
        bot.reply_to(m, f"⚠️ Masalah teknis: {e}")
