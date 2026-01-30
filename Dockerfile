# 1. Tam sürüm Python kullanıyoruz (Hata riskini azaltır)
FROM python:3.9

# 2. Sistemi güncelle ve gerekli aracı (wget) kur
RUN apt-get update && apt-get install -y wget

# 3. Google Chrome'u DOĞRUDAN indir
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 4. İndirilen dosyayı kur (apt-get eksik parçaları otomatik tamamlar)
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# 5. İndirdiğimiz kurulum dosyasını temizle (yer kaplamasın)
RUN rm google-chrome-stable_current_amd64.deb

# --- Standart Ayarlar ---
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]