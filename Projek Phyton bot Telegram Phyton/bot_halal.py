import os
import json
import io
import pytesseract
from PIL import Image
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. SERVER WEB (KEEP-ALIVE UNTUK RENDER) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Halal Monitor is Running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- 2. LOAD DATABASE EKSTERNAL ---
def load_db():
    try:
        with open('database_zat.json', 'r') as f:
            data = json.load(f)
            return data.get("haram", {}), data.get("kritis", {})
    except Exception as e:
        print(f"Gagal memuat database: {e}")
        return {}, {}

DB_HARAM, DB_KRITIS = load_db()

# --- 3. LOGIKA ANALISIS ---
def analisis_halal(teks):
    teks = teks.lower()
    merah, kuning = [], []

    for k, v in DB_HARAM.items():
        if k in teks: merah.append(f"🔴 *{k.upper()}*: {v}")
    for k, v in DB_KRITIS.items():
        if k in teks: kuning.append(f"🟡 *{k.upper()}*: {v}")

    if not merah and not kuning:
        return "✅ *AMAN*: Tidak ditemukan zat mencurigakan berdasarkan database kami."

    respon = "🔍 *HASIL ANALISIS KANDUNGAN:*\n\n"
    if merah:
        respon += "🚫 *KATEGORI MERAH (HARAM):*\n" + "\n".join(merah) + "\n\n"
    if kuning:
        respon += "⚠️ *KATEGORI KUNING (KRITIS):*\n" + "\n".join(kuning) + "\n"
        respon += "\n_Saran: Cek logo Halal resmi atau tanyakan pada produsen._"
    return respon

# --- 4. HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim komposisi (teks) atau foto label produk untuk cek kehalalan.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hasil = analisis_halal(update.message.text)
    await update.message.reply_text(hasil, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sedang memproses gambar... 🔍")
    try:
        # Path Tesseract otomatis (Windows vs Linux)
        if os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        else:
            pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

        file = await update.message.photo[-1].get_file()
        img_bytes = await file.download_as_bytearray()
        text_ocr = pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes)), lang='ind+eng')
        
        hasil = analisis_halal(text_ocr)
        await update.message.reply_text(hasil, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Gagal membaca gambar: {e}")

# --- 5. MAIN RUNNER ---
if __name__ == '__main__':
    TOKEN = '8500299562:AAF1zgo01wLDB5gIqa7BJ3jQuE5inpCoWrM'
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Jalankan Server Web (Keep-Alive)
    keep_alive()

    print("Bot Halal Aktif & Web Server Berjalan...")
    application.run_polling(drop_pending_updates=True)