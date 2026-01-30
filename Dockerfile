# 1. Python'un hafif sürümü
FROM python:3.9-slim

# 2. Gerekli araçlar
RUN apt-get update && apt-get install -y wget gnupg2 unzip

# 3. Google Chrome Kurulumu (Mac/Linux uyumlu komut)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# 4. Çalışma alanı
WORKDIR /app

# 5. Dosyaları kopyala
COPY . .

# 6. Kütüphaneleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# 7. Başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]