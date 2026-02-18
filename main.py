import telebot
import os
import time
import threading
import subprocess

print("🔄 MEMULAI SISTEM...")

# --- LANGKAH 1: AMBIL DATA DARI KOYEB ---
# Kita ambil mentah-mentah apa yang dikasih Koyeb
RAW_TOKEN = os.environ.get("TOKEN", "KOSONG")

# Bersihkan jika ada spasi tidak sengaja
TOKEN = RAW_TOKEN.strip().replace('"', '').replace("'", "")

# --- LANGKAH 2: DIAGNOSA MENDALAM (LOGIC GUARD) ---
# Jika token kosong atau tidak ada titik dua (:), kita JANGAN matikan aplikasi.
# Kita tahan aplikasinya agar Anda bisa baca log.
if TOKEN == "KOSONG" or ":" not in TOKEN:
    print("\n" + "="*40)
    print("❌ GAGAL STARTUP - DIAGNOSA MASALAH:")
    print("="*40)
    
    if TOKEN == "KOSONG":
        print("1. PENYEBAB: Variabel 'TOKEN' tidak ditemukan sama sekali.")
        print("2. ARTINYA: Anda belum mengatur Environment Variable di Dashboard Koyeb.")
        print("3. SOLUSI: Buka Koyeb -> Settings -> Environment Variables.")
        print("   Buat Key: TOKEN")
        print("   Isi Value: 123456:ABC-Def... (Token BotFather)")
    else:
        print(f"1. PENYEBAB: Token ditemukan tapi format hancur.")
        print(f"2. YANG DIBACA SISTEM: {TOKEN[:5]}... (Format Salah)")
        print("3. SOLUSI: Cek apakah Anda salah paste atau ada karakter aneh.")
    
    print("="*40)
    print("⚠️ APLIKASI AKAN MASUK MODE TIDUR (STANDBY).")
    print("👉 Silakan perbaiki di Dashboard Koyeb lalu klik 'Redeploy'.")
    print("👉 Log ini tidak akan hilang karena aplikasi tidak akan restart.")
    print("="*40 + "\n")
    
    # INFINITE LOOP: Tahan aplikasi agar tetap hidup (Status: Healthy)
    # Ini mencegah Error 'Application exited with code 1'
    while True:
        time.sleep(60)

# --- LANGKAH 3: JIKA LOLOS DIAGNOSA, JALANKAN BOT ---
try:
    bot = telebot.TeleBot(TOKEN)
    me = bot.get_me()
    print(f"✅ SUKSES! Bot @{me.username} berhasil login.")
except Exception as e:
    print(f"❌ TOKEN DITOLAK TELEGRAM: {e}")
    # Tahan juga kalau error di sini
    while True: time.sleep(60)

# --- LANGKAH 4: FITUR PEMBERSIH & DOWNLOADER ---
def auto_clean():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.startswith("vid_") and f.endswith(".mp4"):
                try: os.remove(f)
                except: pass

threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_download(m):
    # Logika download standar
    temp_msg = bot.reply_to(m, "⏳ Proses...")
    filename = f"vid_{m.chat.id}_{int(time.time())}.mp4"
    try:
        subprocess.run(['yt-dlp', '-f', 'mp4', '--no-playlist', '-o', filename, m.text], check=True, timeout=300)
        with open(filename, 'rb') as v:
            bot.send_video(m.chat.id, v, caption="✅ Done")
        os.remove(filename)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", m.chat.id, temp_msg.message_id)

print("🚀 BOT SIAP MELAYANI!")
bot.infinity_polling()
