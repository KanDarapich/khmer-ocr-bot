import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Read token from environment variable
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("BOT_TOKEN environment variable missing.")

# Tesseract path inside Docker
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image and I will extract Khmer/English text.")

async def ocr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "image.jpg"
    await file.download_to_drive(file_path)

    try:
        text = pytesseract.image_to_string(Image.open(file_path), lang="khm+eng")
        if text.strip():
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("No text found.")
    except Exception as e:
        await update.message.reply_text(f"OCR error: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.PHOTO, ocr_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
