import os
import logging

from PIL import Image
import pytesseract

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------- logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- configuration ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Tesseract path inside Railway Docker container
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Use Khmer + English
OCR_LANG = "khm+eng"


# ---------- handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me an image with Khmer or English text and I’ll try to read it."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Just send a photo that contains text. I’ll reply with the recognized text."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()

    local_path = "input.jpg"
    await file.download_to_drive(local_path)

    try:
        image = Image.open(local_path)

        text = pytesseract.image_to_string(image, lang=OCR_LANG)
        text = text.strip()

        if text:
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("I couldn’t detect any text in that image.")
    except Exception as e:
        logger.exception("OCR failed")
        await update.message.reply_text(f"❌ OCR failed: {e}")
    finally:
        try:
            os.remove(local_path)
        except FileNotFoundError:
            pass


# ---------- main ----------
def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Starting bot with polling on Railway...")
    app.run_polling()


if __name__ == "__main__":
    main()
