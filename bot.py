import os
import logging
from io import BytesIO

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from PIL import Image
import pytesseract

# ---------- BASIC SETUP ----------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # we'll use env var for safety

if not BOT_TOKEN:
    # For local testing only, you can hardcode temporarily:
    # BOT_TOKEN = "123456:ABC......."
    raise RuntimeError("BOT_TOKEN environment variable is not set!")


# If Tesseract is not on PATH, set this on Windows (LOCAL ONLY):
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# For Docker/railway deployment:
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Khmer Tesseract config
KHMER_CONFIG = r"--oem 3 --psm 6 -l khm"


# ---------- HANDLERS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply when user sends /start."""
    await update.message.reply_text(
        "សួស្តី! 👋\n"
        "Send me a picture that contains Khmer text and I’ll try to read it."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Just send me an image with Khmer text.\n"
        "I will try to extract the text using OCR."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle images sent by the user."""
    if not update.message or not update.message.photo:
        return

    # Get highest-resolution version of the photo
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Download to memory
    bio = BytesIO()
    await file.download_to_memory(out=bio)
    bio.seek(0)

    # Open image
    try:
        image = Image.open(bio)
    except Exception as e:
        logging.exception("Failed to open image")
        await update.message.reply_text(f"❌ Could not open image: {e}")
        return

    # Run OCR
    try:
        text = pytesseract.image_to_string(image, config=KHMER_CONFIG)
        text = text.strip()
        if not text:
            text = "I could not detect any readable Khmer text in that image 😔"
    except Exception as e:
        logging.exception("OCR failed")
        text = f"❌ OCR failed: {e}"

    # Send back the result
    await update.message.reply_text(text)


# ---------- MAIN ----------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # This is simple, blocking, and handles its own event loop internally.
    logging.info("Bot starting with polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
