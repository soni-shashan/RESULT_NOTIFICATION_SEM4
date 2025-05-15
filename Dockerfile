FROM python:3.12-slim

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxext6 \
    libgbm1 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxdamage1 \
    libxfixes3 \
    libxcb1 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install playwright browsers
RUN playwright install

RUN playwright install-deps


# Copy your app code
COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
