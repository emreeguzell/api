from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = FastAPI()

# --- 1. KISIM: ARAYÜZ (HTML + CSS + JS) ---
# Burası sitenin görüntüsüdür. Python içinde HTML yazıyoruz.
html_content = """
<!DOCTYPE html>
<html>
    <head>
        <title>Borsa Ajanı v1.0</title>
        <style>
            body { background-color: #1e1e1e; color: #00ff41; font-family: 'Courier New', monospace; text-align: center; padding-top: 50px; }
            h1 { text-shadow: 0 0 10px #00ff41; }
            .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #00ff41; box-shadow: 0 0 20px #00ff41; border-radius: 10px; }
            input { padding: 10px; width: 60%; border-radius: 5px; border: none; font-size: 16px; }
            button { padding: 10px 20px; background-color: #00ff41; color: #000; border: none; cursor: pointer; font-weight: bold; border-radius: 5px; font-size: 16px; }
            button:hover { background-color: #fff; }
            #sonuc { margin-top: 20px; font-size: 18px; text-align: left; background: #000; padding: 15px; display: none; border-radius: 5px; }
            .loading { color: yellow; display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 Borsa Ajanı</h1>
            <p>Hisse kodunu gir ve ajanları gönder.</p>
            
            <input type="text" id="symbol" placeholder="Örn: THYAO, SASA, GARAN">
            <button onclick="veriyiGetir()">SORGULA</button>
            
            <p id="loading" class="loading">📡 Uydu bağlantısı kuruluyor... Veriler çekiliyor...</p>
            
            <div id="sonuc"></div>
        </div>

        <script>
            async function veriyiGetir() {
                var symbol = document.getElementById("symbol").value.toUpperCase();
                var loading = document.getElementById("loading");
                var sonucDiv = document.getElementById("sonuc");
                
                if (!symbol) { alert("Lütfen bir kod gir!"); return; }

                // Yükleniyor yazısını göster
                loading.style.display = "block";
                sonucDiv.style.display = "none";
                sonucDiv.innerHTML = "";

                try {
                    // Bizim yazdığımız API'ye istek at
                    const response = await fetch("/detay/" + symbol);
                    const data = await response.json();

                    // Sonucu ekrana yaz
                    let html = `
                        <p><strong>Şirket:</strong> ${data.baslik}</p>
                        <p><strong>Fiyat:</strong> <span style="color: #fff; font-size: 24px;">${data.fiyat} ₺</span></p>
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

# --- 2. KISIM: ROBOT (BACKEND) ---
def get_stock_details(symbol: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=en-US")
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
        wait = WebDriverWait(driver, 10)
        
        # Fiyat çekme (Güncellediğimiz sağlam yöntem)
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".YMlKec.fxKbKc")))
            data["fiyat"] = element.text.replace("₺", "").strip()
        except:
            data["fiyat"] = "Bulunamadı"

        data["baslik"] = driver.title
        
        try:
            degisim = driver.find_element(By.CSS_SELECTOR, ".P2Luy")
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

# --- 3. KISIM: BAĞLANTI NOKTALARI (ENDPOINTS) ---

@app.get("/", response_class=HTMLResponse)
def home():
    return html_content

@app.get("/detay/{symbol}")
def fetch_details(symbol: str):
    return get_stock_details(symbol)