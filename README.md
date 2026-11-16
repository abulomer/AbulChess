# ♞ Satranç Pro (Portable)

Hem Linux dağıtımlarında hem de Python yüklü Windows bilgisayarlarda doğrudan çalışan, çok oyunculu, web tabanlı satranç uygulaması.

---

## 🚀 Başlatma

### 🐧 Linux / macOS
Terminalde tek komutla başlatın:
```bash
./satranc.sh
```
*(Gerekirse: `chmod +x satranc.sh`)*

### 🪟 Windows
Klasör içerisindeki **`satranc.bat`** dosyasına **çift tıklayın**.

---

## 📁 Proje Dosya Yapısı

Dış dizinde yalnızca başlatma dosyaları bulunur; Python kodları, motorlar ve görsel kaynaklar kendi özel klasörlerine toplanmıştır:

```text
Chess/
│
├── satranc.sh               # 🐧 Linux & macOS başlatıcı dosyası (tek tık)
├── satranc.bat              # 🪟 Windows başlatıcı dosyası (çift tık)
├── README.md                # 📄 Kullanım kılavuzu
│
├── server/                  # 🐍 Python Sunucu & Kodlar
│   ├── satranc.py           # Ana uygulama ve web sunucusu
│   ├── venv/                # Linux sanal ortamı
│   └── __pycache__/         # Bytecode önbelleği
│
├── engines/                 # ⚙️ Satranç & Ses Motorları
│   ├── stockfish-linux-x86-64-universal       # Linux Stockfish 19 motoru
│   ├── stockfish-windows-x86-64-universal.exe # Windows Stockfish 19 motoru
│   └── piper-turkish-tts/                     # Türkçe sesli koç sinir ağı
│       ├── model.onnx
│       └── config.json
│
└── assets/                  # 🎨 Görsel Kaynaklar
    ├── bot/                 # Bot avatarları ve seviye resimleri
    └── sprite/              # Taşlar ve arayüz simgeleri
```

---

## 💡 İsteğe Bağlı Özellikler

- **Satranç & Stockfish:** Standart kütüphanelerle çalışır, hiçbir ek paket gerekmez.
- **Sesli Koç Analizi (Piper TTS):** Windows'ta ilk açılışta kütüphane eksikse otomatik olarak `[E/H]` sorusu gelir; `E` seçilirse otomatik kurulur. İsteğe bağlı olarak elle de kurabilirsiniz:
  ```bash
  pip install piper-tts
  ```
