FROM python:3.12-slim

# Install Tesseract + Khmer language pack
RUN apt update && apt install -y \
    tesseract-ocr \
    tesseract-ocr-khm \
    tesseract-ocr-eng \
    && apt clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
