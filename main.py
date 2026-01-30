from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = FastAPI()

def get_stock_details(symbol: str):
    # --- AYARLAR ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=en-US")
    # Kendimizi gerçek bir Chrome tarayıcısı gibi gösterelim (Anti-Bot önlemi)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    data = {}
    
    try:
        url = f"https://www.google.com/finance/quote/{symbol}:BIST"
        driver.get(url)
        
        # Elementin yüklenmesi için maksimum 10 saniye bekle
        wait = WebDriverWait(driver, 10)
        
        # --- VERİ KAZIMA (3 FARKLI YÖNTEM) ---
        
        # 1. Başlık
        data["baslik"] = driver.title

        # 2. Fiyatı Bulma (Yedekli Sistem)
        fiyat = "Bulunamadı"
        
        # Yöntem A: En yaygın sınıf (.YMlKec)
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".YMlKec")))
            fiyat = element.text
        except:
            # Yöntem B: Alternatif sınıf (.fxKbKc)
            try:
                element = driver.find_element(By.CSS_SELECTOR, ".fxKbKc")
                fiyat = element.text
            except:
                # Yöntem C: Sayfadaki en büyük yazı tipi (XPath)
                try:
                    element = driver.find_element(By.XPATH, "//div[contains(@class, 'YMlKec')]")
                    fiyat = element.text
                except:
                    pass
        
        # Temizlik: TL simgesini ve boşlukları temizle
        data["fiyat"] = fiyat.replace("₺", "").replace("TL", "").strip()

        # 3. Değişim Oranı
        try:
            degisim_element = driver.find_element(By.CSS_SELECTOR, ".P2Luy")
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
    return {"mesaj": "Borsa API v3 - Guclendirilmis Versiyon"}

@app.get("/detay/{symbol}")
def fetch_details(symbol: str):
    return get_stock_details(symbol)