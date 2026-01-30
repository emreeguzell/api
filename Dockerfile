# 1. Python'un temel sürümü
FROM python:3.9

# 2. Sistemi güncelle ve Chromium'u (Tarayıcı) + Sürücüsünü kur
# Google'dan indirmek yerine, Linux'un kendi deposundan alıyoruz (Çok daha güvenli)
RUN apt-get update && apt-get install -y chromium chromium-driver

# 3. Kütüphaneleri yükle
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]