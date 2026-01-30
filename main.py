from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # <-- Bunu eklemeyi unutma!
import os

app = FastAPI()

def get_stock_details(symbol: str):
    # --- AYARLAR ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Türkçe karakter sorunu olmasın diye dili İngilizce yapalım
    chrome_options.add_argument("--lang=en-US")
    
    # Render'da mıyız, Mac'te miyiz kontrolü
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        # Senin bilgisayarın (Mac)
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    data = {}
    
    try:
        # BIST ekleyerek tam arama yapıyoruz
        url = f"https://www.google.com/finance/quote/{symbol}:BIST"
        driver.get(url)
        
        # --- VERİ KAZIMA (SCRAPING) KISMI ---
        
        # 1. Başlık
        data["baslik"] = driver.title

        # 2. Fiyat (Google Finance'in meşhur class'ı: YMlKec fxKbKc)
        try:
            fiyat_element = driver.find_element(By.CSS_SELECTOR, ".YMlKec.fxKbKc")
            data["fiyat"] = fiyat_element.text.replace("₺", "").strip() # TL simgesini temizle
        except:
            data["fiyat"] = "Bulunamadı"

        # 3. Yüzdelik Değişim (Yeşil/Kırmızı kutu)
        try:
            # Class isimleri bazen değişir ama genelde budur
            degisim_element = driver.find_element(By.CSS_SELECTOR, ".P2Luy") 
            # Artı mı eksi mi olduğunu anlamak için class rengine bakılabilir ama şimdilik metni alalım
            data["degisim"] = degisim_element.text
        except:
            data["degisim"] = "%0.00"

        data["url"] = driver.current_url
        data["durum"] = "Basarili"
        
    except Exception as e:
        data["hata"] = str(e)
        data["durum"] = "Hata Olustu"
    finally:
        driver.quit()
    return data

@app.get("/")
def home():
    return {"mesaj": "Borsa API v2 - Fiyatlar Eklendi! /detay/THYAO adresine git."}

@app.get("/detay/{symbol}")
def fetch_details(symbol: str):
    return get_stock_details(symbol)