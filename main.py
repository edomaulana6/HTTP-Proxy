import telebot
import os
import time
import threading
import subprocess

# --- PENGATURAN TOKEN ---
# Masukkan token Anda di antara tanda kutip di bawah ini
# Contoh: TOKEN = "1234567890:ABCdefghIJKLmnoPQR"
TOKEN = "MASUKKAN_TOKEN_DISINI" 

# Jika ingin tetap pakai Environment Variable Koyeb, aktifkan baris di bawah ini:
# TOKEN = os.getenv("TOKEN", TOKEN)

try:
    bot = telebot.TeleBot(TOKEN)
    print(f"LOG: Mencoba koneksi...")
    # Langsung tes koneksi
    bot_user = bot.get_me()
    print(f"✅ BERHASIL: Bot @{bot_user.username} aktif!")
except Exception as e:
    print(f"❌ ERROR: Token tidak valid atau jaringan bermasalah: {e}")
    # Berhenti agar tidak loop restart di Koyeb
    exit(1)

# --- SISTEM PEMBERSIHAN (RESET MEMORY) ---
def auto_delete_files():
    """Menghapus file video setiap 1 menit agar storage tidak penuh"""
    while True:
        time.sleep(60)
        folder = "."
        for file in os.listdir(folder):
            if file.startswith("vid_") and file.endswith(".mp4"):
                try:
                    os.remove(os.path.join(folder, file))
                    print(f"🗑️ Cleaned: {file}")
                except:
                    pass

# Jalankan cleaner di latar belakang
threading.Thread(target=auto_delete_files, daemon=True).start()

# --- HANDLER DOWNLOAD ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def download_video(m):
    status = bot.reply_to(m, "⏳ Sedang memproses... mohon tunggu.")
    
    # Nama file unik berdasarkan ID Chat dan waktu
    file_output = f"vid_{m.chat.id}_{int(time.time())}.mp4"
    
    try:
        # Perintah download (yt-dlp)
        # --no-check-certificate digunakan agar lebih lancar di server
        cmd = [
            'yt-dlp',
            '-f', 'mp4',
            '--no-check-certificate',
            '-o', file_output,
            m.text
        ]
        
        # Proses download
        subprocess.run(cmd, check=True, timeout=180) # Timeout 3 menit
        
        if os.path.exists(file_output):
            with open(file_output, "rb") as video:
                bot.send_video(m.chat.id, video, caption="✅ Video berhasil dikirim!")
            # Hapus segera setelah berhasil kirim
            os.remove(file_output)
            bot.delete_message(m.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ Gagal: Video tidak ditemukan setelah download.", m.chat.id, status.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ Terjadi kesalahan: {str(e)}", m.chat.id, status.message_id)

print("🚀 Bot sedang berjalan (Infinity Polling)...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
