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

Online oyunda rakibin sırası sırasında varsayılan olarak bir ön hamleyi sıraya alabilirsiniz. Ayarlar'daki **Çoklu ön hamle** seçeneğini açarak en fazla 5 hamleyi sıraya alın. Her rakip hamlesinden sonra sıradaki ön hamle hâlâ geçerliyse otomatik oynanır; geçersiz hâle gelirse kuyruk iptal edilir. Ön hamleleri sıraya alırken taşlar tahtadaki yerlerinde kalır. Çoklu ön hamleyi kapatırsanız varsa yalnızca sıradaki ilk hamle korunur. Kare vurgulamayı **Ön hamle karelerini vurgula** seçeneğinden bağımsız olarak açıp kapatabilirsiniz.

### 🪟 Windows
Klasör içerisindeki **`satranc.bat`** dosyasına **çift tıklayın**.

---

## 📁 Proje Dosya Yapısı

Dizinler uygulamanın sunucu, Android istemcisi, motor ve görsel kaynaklarını ayırır:

```text
AbulChess/
│
├── .github/
│   └── workflows/
│       └── android-apk.yml       # Android APK derleme iş akışı
│
├── android/                      # Android istemcisi ve Gradle yapılandırması
│   ├── app/src/main/
│   │   ├── AndroidManifest.xml
│   │   └── java/com/abulomer/abulchess/
│   │       └── MainActivity.kt
│   ├── gradle/wrapper/           # Gradle Wrapper dosyaları
│   ├── app/build.gradle.kts
│   ├── build.gradle.kts
│   ├── gradle.properties
│   ├── gradlew
│   ├── gradlew.bat
│   └── settings.gradle.kts
│
├── assets/
│   ├── bot/                      # Bot avatarları ve seviye görselleri
│   └── sprite/                   # Taşlar ve arayüz görselleri
│
├── engines/
│   ├── piper-turkish-tts/        # Türkçe sesli koç modeli ve yapılandırması
│   │   ├── config.json
│   │   └── model.onnx
│   ├── stockfish-linux-x86-64-universal
│   └── stockfish-windows-x86-64-universal.exe
│
├── server/
│   └── satranc.py                # Python sunucusu ve web uygulaması
│
├── satranc.sh                    # Linux / macOS başlatıcısı
└── README.md
```

---

## 💡 İsteğe Bağlı Özellikler

- **Satranç & Stockfish:** Standart kütüphanelerle çalışır, hiçbir ek paket gerekmez.
- **Sesli Koç Analizi (Piper TTS):** Windows'ta ilk açılışta kütüphane eksikse otomatik olarak `[E/H]` sorusu gelir; `E` seçilirse otomatik kurulur. İsteğe bağlı olarak elle de kurabilirsiniz:
  ```bash
  pip install piper-tts
  ```
