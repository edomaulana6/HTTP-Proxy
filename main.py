import telebot, os, time, threading

# Data harus akurat: Ambil TOKEN dari Environment Variable Koyeb
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# RESET MEMORY: Hapus file sampah video setiap 1 menit secara otomatis
def auto_clean():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(f)
                    print(f"Pembersihan: {f} berhasil dihapus dari memori.")
                except:
                    pass

# Jalankan cleaner di background agar bot tetap responsif
threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: True)
def handle_download(m):
    url = m.text
    if not url.startswith("http"):
        return

    bot.reply_to(m, "Sabar, pesanan video sedang diproses...")
    
    # Simpan dengan nama unik berdasarkan ID chat agar tidak tertukar
    file_output = f"video_{m.chat.id}.mp4"
    
    try:
        # Perintah yt-dlp yang paling stabil
        os.system(f'yt-dlp -f "best" --no-cookies -o "{file_output}" "{url}"')
        
        if os.path.exists(file_output):
            with open(file_output, "rb") as video:
                bot.send_video(m.chat.id, video)
            os.remove(file_output) # Hapus langsung setelah terkirim
        else:
            bot.reply_to(m, "Gagal mengunduh video. Link tidak valid atau server tujuan sibuk.")
    except Exception as e:
        bot.reply_to(m, f"Error sistem: {e}")

print("Bot Telegram Aktif & Sistem Cleaner Berjalan...")
bot.infinity_polling()
