import telebot
import os
import time
import threading
import subprocess

# --- KUNCI UTAMA: PENGECEKAN SEDERHANA & BERSIH ---
# Ambil dari Environment Variable 'TOKEN' di Koyeb
# .strip() akan menghapus spasi atau enter yang tidak sengaja terbawa
TOKEN = os.getenv("TOKEN", "").strip()

# Validasi langsung: Jika kosong atau tidak ada titik dua, matikan sistem.
if not TOKEN or ":" not in TOKEN:
    print("❌ ERROR: TOKEN KOSONG ATAU FORMAT SALAH!")
    print("Pastikan di Koyeb sudah ada Env Var: TOKEN")
    os._exit(1) # Paksa keluar agar Koyeb memberikan log yang jelas

# Langsung buat objek bot tanpa try-except yang ribet di awal
# Ini memastikan jika token salah, errornya jelas di log (Invalid Token)
bot = telebot.TeleBot(TOKEN)
print(f"✅ LOG: Mencoba menjalankan Bot...")

# --- RESET MEMORY (HAPUS FILE TIAP 1 MENIT) ---
def auto_clean():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.startswith("vid_") and f.endswith(".mp4"):
                try:
                    os.remove(f)
                except:
                    pass

threading.Thread(target=auto_clean, daemon=True).start()

# --- HANDLER DOWNLOAD ---
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_download(m):
    # Nama file unik agar tidak bentrok antar user
    filename = f"vid_{m.chat.id}_{int(time.time())}.mp4"
    bot.reply_to(m, "⏳ Sedang diproses...")
    
    try:
        # Perintah yt-dlp paling dasar & stabil
        # --no-playlist: jangan download satu album
        # -f mp4: pastikan format mp4 agar bisa diputar di HP
        subprocess.run(['yt-dlp', '-f', 'best[ext=mp4]', '--no-playlist', '-o', filename, m.text], check=True)
        
        if os.path.exists(filename):
            with open(filename, "rb") as v:
                bot.send_video(m.chat.id, v, caption="✅ Berhasil!")
            os.remove(filename) # Langsung hapus setelah terkirim
        else:
            bot.send_message(m.chat.id, "❌ Video gagal diproses.")
    except Exception as e:
        bot.send_message(m.chat.id, f"⚠️ Masalah: {str(e)}")

# Jalankan Bot
print("🚀 BOT AKTIF!")
bot.infinity_polling()
