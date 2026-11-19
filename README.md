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

### 📱 Android

GitHub Releases bölümündeki **`AbulChess.apk`** dosyasını indirip Android cihazınıza kurun. İlk açılışta, sunucuyu çalıştıran bilgisayardaki `Yerel ağ` adresini girin (ör. `http://192.168.1.10:8765`). İki cihaz da aynı Wi-Fi ağına bağlı olmalı ve bilgisayardaki güvenlik duvarı bu porta izin vermelidir. Bilgisayar sunucuyu çalıştırmaya devam eder; APK mevcut yerel ağdaki 2 oyunculu oda sistemine istemci olarak bağlanır.

### ♟ Çoklu ön hamle

Online oyunda rakibin sırası sırasında varsayılan olarak bir ön hamleyi sıraya alabilirsiniz. Ayarlar'daki **Çoklu ön hamle** seçeneğini açarak en fazla 5 hamleyi sıraya alabilirsiniz; sıra size geldiğinde hamleler sırayla otomatik oynanır. Taşlar tahtadaki yerlerinde kalır. Ön hamle karelerinin vurgulanmasını **Ön hamle karelerini vurgula** seçeneğinden ayrıca açıp kapatabilirsiniz. Rakibin hamlesi sıradaki hamleyi geçersiz kılarsa kuyruk iptal edilir.

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
