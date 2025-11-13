import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from PIL import Image
import pytesseract

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Read bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Path to tesseract inside Railway container
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# OCR languages
OCR_LANG = "khm+eng"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "សួស្តី! 👋\n"
        "Send me a picture that contains Khmer text and I’ll try to read it."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()

        local_path = "photo.jpg"
        await file.download_to_drive(local_path)

        img = Image.open(local_path)
        text = pytesseract.image_to_string(img, lang=OCR_LANG).strip()

        if text:
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("I could not detect any text in that image.")
        
        os.remove(local_path)

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        await update.message.reply_text("OCR failed. Make sure the image is clear.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is now running with polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
