FROM python:3.12-slim

# Install Tesseract + Khmer language pack
RUN apt update && apt install -y \
    tesseract-ocr \
    tesseract-ocr-khm \
    tesseract-ocr-eng \
    && apt clean

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run the bot with polling (no port required)
CMD ["python", "bot.py"]
