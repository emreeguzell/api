from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import random

app = FastAPI()

# --- ARAYÜZ (Görsel aynı kalsın) ---
html_content = """
<!DOCTYPE html>
<html>
    <head>
        <title>Borsa Ajanı (Selenium Mode)</title>
        <style>
            body { background-color: #0d1117; color: #58a6ff; font-family: 'Consolas', monospace; text-align: center; padding-top: 50px; }
            h1 { color: #58a6ff; text-shadow: 0 0 10px #58a6ff; }
            .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #30363d; box-shadow: 0 0 20px #161b22; border-radius: 10px; background-color: #161b22; }
            input { padding: 12px; width: 60%; border-radius: 6px; border: 1px solid #30363d; background-color: #0d1117; color: #c9d1d9; font-size: 16px; outline: none; }
            button { padding: 12px 24px; background-color: #238636; color: #fff; border: none; cursor: pointer; font-weight: bold; border-radius: 6px; font-size: 16px; transition: 0.3s; }
            button:hover { background-color: #2ea043; }
            #sonuc { margin-top: 20px; font-size: 18px; text-align: left; background: #0d1117; padding: 20px; display: none; border-radius: 6px; border: 1px solid #30363d; }
            .loading { color: #f2cc60; display: none; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕵️ Borsa Ajanı (Selenium)</h1>
            <p>Google Korumalarını Aşma Modu</p>
            
            <input type="text" id="symbol" placeholder="Örn: THYAO, SASA">
            <button onclick="veriyiGetir()">SORGULA</button>
            
            <p id="loading" class="loading">📡 Gizli bağlantı kuruluyor... Google kandırılıyor...</p>
            
            <div id="sonuc"></div>
        </div>

        <script>
            async function veriyiGetir() {
                var symbol = document.getElementById("symbol").value.toUpperCase();
                var loading = document.getElementById("loading");
                var sonucDiv = document.getElementById("sonuc");
                
                if (!symbol) { alert("Lütfen bir kod gir!"); return; }

                loading.style.display = "block";
                sonucDiv.style.display = "none";
                sonucDiv.innerHTML = "";

                try {
                    const response = await fetch("/detay/" + symbol);
                    const data = await response.json();

                    let html = `
                        <p><strong>Şirket:</strong> ${data.baslik}</p>
                        <p><strong>Fiyat:</strong> <span style="color: #fff; font-size: 28px;">${data.fiyat}</span></p>
                        <p><strong>Değişim:</strong> ${data.degisim}</p>
                        <p><small>Durum: ${data.durum}</small></p>
                    `;
                    sonucDiv.innerHTML = html;
                    sonucDiv.style.display = "block";

                } catch (error) {
                    sonucDiv.innerHTML = "Hata oluştu: " + error;
                    sonucDiv.style.display = "block";
                } finally {
                    loading.style.display = "none";
                }
            }
        </script>
    </body>
</html>
"""

# --- GİZLİLİK MODU AYARLARI ---
def get_stock_details(symbol: str):
    chrome_options = Options()
    
    # 1. Headless (Yeni Mod) - Eski moda göre daha az yakalanır
    chrome_options.add_argument("--headless=new")
    
    # 2. Standart Ayarlar
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 3. KİMLİK GİZLEME (User-Agent)
    # Kendimizi Windows 10 kullanan gerçek bir Chrome gibi tanıtıyoruz
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 4. EN KRİTİK AYAR: Otomasyon bayrağını kapatma
    # Bu satır, Google'ın "Bu bir Selenium botu" demesini engeller
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Render mı Mac mi?
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
        
        # Sayfanın yüklenmesini biraz bekle (İnsan taklidi)
        time.sleep(random.uniform(1, 3))
        
        wait = WebDriverWait(driver, 10)
        
        # --- VERİ ÇEKME ---
        
        # FİYAT (Yedekli sistem)
        try:
            # En güncel Google Finance Class'ı
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".YMlKec.fxKbKc")))
            data["fiyat"] = element.text.replace("₺", "").strip()
        except:
            # Bulamazsa HTML'in derinliklerine in (Yedek Plan)
            try:
                element = driver.find_element(By.XPATH, "//*[@data-last-price]")
                data["fiyat"] = element.get_attribute("data-last-price")
            except:
                 data["fiyat"] = "Google Botu Yakaladi :("

        data["baslik"] = driver.title
        
        # DEĞİŞİM
        try:
            degisim = driver.find_element(By.CSS_SELECTOR, ".P2Luy") # Yüzdelik kutusu
            # Negatifse başka class olabilir, ikisini de dene
            if not degisim:
                 degisim = driver.find_element(By.CSS_SELECTOR, ".P2Luy.Ez2Ioe") # Kırmızı kutu
            data["degisim"] = degisim.text
        except:
            data["degisim"] = "%0.00"

        data["durum"] = "Basarili"
        
    except Exception as e:
        data["hata"] = str(e)
        data["durum"] = "Hata"
    finally:
        driver.quit()
    return data

@app.get("/", response_class=HTMLResponse)
def home():
    return html_content

@app.get("/detay/{symbol}")
def fetch_details(symbol: str):
    return get_stock_details(symbol)