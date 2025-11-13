import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Adjust Tesseract path if needed
# e.g. pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Example command handler
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image containing text (Khmer or English) and I'll convert it to text.")

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get image
    photo_file = await update.message.photo[-1].get_file()
    local_path = "temp.jpg"
    await photo_file.download_to_drive(local_path)

    # OCR with both Khmer and English
    text = pytesseract.image_to_string(Image.open(local_path), lang='khm+eng')

    if text.strip():
        await update.message.reply_text(f"📖 Recognized text:\n\n{text}")
    else:
        await update.message.reply_text("❌ No readable text found in the image.")
    os.remove(local_path)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))

    print("✅ Bot is starting...")
    app.run_polling()  # simpler polling—no webhooks

if __name__ == "__main__":
    main()
