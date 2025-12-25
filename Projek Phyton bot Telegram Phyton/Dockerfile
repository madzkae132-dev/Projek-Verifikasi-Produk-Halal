# Gunakan image Python resmi
FROM python:3.11-slim

# Instal Tesseract OCR dan dependensi sistem
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ind \
    libgl1-mesa-glx \
    && apt-get clean

# Set folder kerja
WORKDIR /app

# Copy file requirements dan instal library Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file projek ke dalam container
COPY . .

# Jalankan bot
CMD ["python", "bot_halal.py"]