from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

app = FastAPI()

def get_stock_details(symbol: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") # Docker için hayat kurtarıcı ayar!
    
    # Render sunucusunda mıyız yoksa senin Mac'inde miyiz?
    # Eğer Render'daysak Chromium'u kullan, değilse senin Chrome'unu.
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        # Senin bilgisayarın için (Mac)
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    data = {}
    try:
        url = f"https://www.google.com/finance/quote/{symbol}:BIST"
        driver.get(url)
        
        # Basit veri çekme (Başlık)
        data["baslik"] = driver.title
        data["url"] = driver.current_url
        data["durum"] = "Basarili"
        
    except Exception as e:
        data["hata"] = str(e)
    finally:
        driver.quit()
    return data

@app.get("/")
def home():
    return {"mesaj": "Borsa API (Chromium Versiyon)"}

@app.get("/detay/{symbol}")
def fetch_details(symbol: str):
    return get_stock_details(symbol)