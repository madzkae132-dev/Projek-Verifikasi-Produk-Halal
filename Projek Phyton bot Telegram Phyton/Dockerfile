# Use official Python image
FROM python:3.11-slim

# Install Tesseract OCR and system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ind \
    libgl1-mesa-glx \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run the bot
CMD ["python", "bot_halal.py"]
