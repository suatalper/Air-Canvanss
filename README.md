# Air Canvas (Havada Çizim) Projesi 🎨

Bu proje, bilgisayar kamerası (webcam) kullanılarak havadaki el hareketleriyle ekrana çizim yapılmasını sağlayan bir Bilgisayarlı Görü (Computer Vision) uygulamasıdır. **OpenCV** ve **MediaPipe** kütüphaneleri kullanılarak geliştirilmiştir.

## Özellikler ✨
- **Gerçek Zamanlı El Takibi**: MediaPipe sayesinde elin 21 eklem noktası çok yüksek doğrulukla tespit edilir.
- **Çizim Modu**: Sadece **işaret parmağınızı** kaldırarak havada özgürce çizim yapabilirsiniz.
- **Seçim Modu (Renk/Temizle)**: Çizimi duraklatmak veya renk değiştirmek için **işaret ve orta parmağınızı** birlikte havaya kaldırın. İki parmağınız havadayken ekranın üst kısmındaki butonlara dokunarak rengi değiştirebilir veya ekranı temizleyebilirsiniz.
- **Sanal Tuval (Canvas Masking)**: Çizimler, görüntü üzerine doğrudan değil görünmez bir tuval üzerine işlenir. Bu sayede eller hareket ettikçe çizimler sabit kalır ve kamerayla mükemmel şekilde bütünleşir.

## Gereksinimler 🛠️
Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki Python kütüphanelerinin yüklü olması gerekmektedir:
- `opencv-python` (Görüntü işleme ve kamera kontrolleri)
- `mediapipe` (Google'ın yapay zeka destekli el tanıma modeli)
- `numpy` (Sanal tuval matris işlemleri)

Kurulum komutu:
```bash
pip install opencv-python mediapipe numpy
```

## Nasıl Çalıştırılır? 🚀
Projenin bulunduğu dizinde komut satırını açın ve aşağıdaki komutu çalıştırın:
```bash
python kamera_test.py
```
Program çalıştığında kameranız açılacaktır. 
- Çıkmak için video ekranı seçiliyken klavyeden **`q`** tuşuna basmanız yeterlidir.

## Algoritma Mantığı (Pseudo Code) 🧠
Projenin temel çalışma algoritması şu şekildedir:
1. Kamera başlatılır ve sonsuz bir döngüye girilir.
2. Ekrana butonlar (Renkler ve Temizle) çizilir.
3. El tespit edilirse parmakların hangi konumda (açık/kapalı) olduğuna bakılır.
4. **Eğer iki parmak havadaysa**: Çizim durur. Kullanıcı menüden seçim yapabilir.
5. **Eğer tek parmak havadaysa**: Önceki nokta ile parmağın yeni noktası arasına çizgi çekilir.
6. Görüntüler matris maskeleme (bitwise operations) yöntemiyle üst üste bindirilir ve ekrana yansıtılır.
