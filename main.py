from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # <-- YENİ: Element bulmak için gerekli
from webdriver_manager.chrome import ChromeDriverManager
import time

app = FastAPI()

def get_stock_details(symbol: str):
    # --- AYARLAR ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # Google'ın bizi robot sanıp engellememesi için tarayıcı dilini İngilizce yapıyoruz
    chrome_options.add_argument("--lang=en-US") 
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    
    data = {} # Verileri saklayacağımız sepet

    try:
        url = f"https://www.google.com/finance/quote/{symbol}:BIST"
        driver.get(url)
        
        # Sayfanın yüklenmesini bekle (İnternet hızına göre artırılabilir)
        time.sleep(2) 

        # --- VERİ ÇEKME OPERASYONU ---
        
        # 1. Şirket Adı (h1 etiketi içindeki yazı)
        try:
            name_element = driver.find_element(By.CSS_SELECTOR, "div.zzDege")
            data["sirket_adi"] = name_element.text
        except:
            data["sirket_adi"] = "Bulunamadı"

        # 2. Güncel Fiyat (Genelde 'YMlKec fxKbKc' class'ı kullanılır)
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, ".YMlKec.fxKbKc")
            data["fiyat"] = price_element.text
        except:
            data["fiyat"] = "0.00"

        # 3. Yüzdelik Değişim (Yeşil veya kırmızı kutucuk)
        try:
            # XPath ile daha hassas arama yapıyoruz
            change_element = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div[4]/div/div/div/div[1]/div/div/div[1]/div/div/div[2]/div/span/div/div')
            # Google bazen artı/eksi işaretini ayrı tutar, basitçe text'i alalım
            data["degisim"] = change_element.text
        except:
            # Eğer yukarıdaki uzun yol çalışmazsa, basit class ile deneyelim
            try:
                simple_change = driver.find_element(By.CSS_SELECTOR, ".P2Luy") # Alternatif class
                data["degisim"] = simple_change.text
            except:
                data["degisim"] = "%0.00"

        # 4. Meta Bilgiler
        data["sembol"] = symbol
        data["kaynak"] = "Google Finance"
        data["durum"] = "Başarılı"

    except Exception as e:
        data["hata"] = str(e)
        data["durum"] = "Başarısız"
        
    finally:
        driver.quit()
    return data

@app.get("/")
def home():
    return {"mesaj": "Gelişmiş Borsa API'sine Hoşgeldin."}

@app.get("/detay/{symbol}")
def fetch_details(symbol: str):
    return get_stock_details(symbol)