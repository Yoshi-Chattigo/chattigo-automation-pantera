# Use the official Playwright Python image
# This image includes Python, Playwright, and the necessary browser binaries
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the browsers (Chromium is usually enough, but install all just in case or limit to chromium)
# The base image already has browsers, but sometimes we need to ensure they are linked correctly
RUN playwright install chromium

# Copy the rest of the application code
COPY . .

# Set environment variables (Defaults, can be overridden by Cloud Run)
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=True

# Command to run the bot
CMD ["python3", "bot.py"]
