const { Telegraf } = require('telegraf');
const { GoogleGenerativeAI } = require("@google/generative-ai");
const fs = require('fs');
const path = require('path');

// --- KONFIGURASI ---
const bot = new Telegraf(process.env.BOT_TOKEN);
const genAI = new GoogleGenerativeAI(process.env.GEMINI_KEY);

// Menggunakan Gemini 3 Flash Terbaru
const model = genAI.getGenerativeModel({ 
    model: "gemini-3-flash-preview",
    systemInstruction: "Kamu adalah asisten bot Telegram yang sangat pintar, to the point, dan sopan."
});

// Database Memori (In-Memory)
let chatMemory = {};

// --- SISTEM MAINTENANCE OTOMATIS ---

// Reset Memori Setiap 24 Jam agar RAM Koyeb tidak bengkak
setInterval(() => {
    chatMemory = {};
    console.log("[SYSTEM] Memory Reset Berhasil (24 Jam).");
}, 86400000);

// Hapus File Sampah per 1 Menit
setInterval(() => {
    const tmpDir = './tmp';
    if (fs.existsSync(tmpDir)) {
        fs.readdir(tmpDir, (err, files) => {
            if (err) return;
            files.forEach(file => fs.unlink(path.join(tmpDir, file), () => {}));
        });
    }
}, 60000);

// --- PERINTAH BOT ---

bot.start((ctx) => {
    ctx.reply('Halo! Bot ini menggunakan Gemini 3 Flash (Versi Terbaru 2026).\n\nKetik apa saja untuk bertanya.\nKetik /reset untuk hapus memori.');
});

// Fitur Reset Manual
bot.command('reset', (ctx) => {
    chatMemory[ctx.from.id] = [];
    ctx.reply('✅ Memori percakapan Anda telah direset ke 0.');
});

// Handling Chat AI
bot.on('text', async (ctx) => {
    const userId = ctx.from.id;
    const text = ctx.message.text;

    if (text.startsWith('/')) return;

    try {
        await ctx.sendChatAction('typing');

        if (!chatMemory[userId]) chatMemory[userId] = [];
        
        const chat = model.startChat({ 
            history: chatMemory[userId],
            generationConfig: { maxOutputTokens: 2000 }
        });

        const result = await chat.sendMessage(text);
        const response = await result.response;
        const resultText = response.text();

        // Simpan ke memori (Maksimal 10 history agar efisien)
        chatMemory[userId].push({ role: "user", parts: [{ text }] });
        chatMemory[userId].push({ role: "model", parts: [{ text: resultText }] });
        if (chatMemory[userId].length > 10) chatMemory[userId].shift();

        ctx.reply(resultText, { parse_mode: 'Markdown' });
    } catch (err) {
        console.error(err);
        ctx.reply('⚠️ Terjadi kesalahan pada API Gemini 3. Pastikan API Key benar.');
    }
});

bot.launch();
console.log('Gemini 3 Flash Bot is running...');
