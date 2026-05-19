import sys
sys.dont_write_bytecode = True # pycache klasörünün oluşmasını engeller

import cv2
import numpy as np
import mediapipe as mp

# 1. MediaPipe el algılama modellerini başlatıyoruz
mp_eller = mp.solutions.hands
eller = mp_eller.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_cizim = mp.solutions.drawing_utils

# 2. Çizim yapılacak tuvali (canvas) hazırlıyoruz. Siyah bir arka plan olacak.
# Kameradan gelen görüntüyle aynı boyutta olmalı (genelde 480x640).
cizim_tuvali = np.zeros((480, 640, 3), dtype=np.uint8)

# 3. Renk tanımlamaları (B, G, R) formatında (OpenCV ters kullanır)
renkler = [
    (255, 0, 0),    # Mavi
    (0, 255, 0),    # Yeşil
    (0, 0, 255),    # Kırmızı
    (0, 255, 255)   # Sarı
]
renk_indeksi = 0 # Başlangıçta Mavi seçili olsun

# 4. Fırça ayarları
firca_kalinligi = 5
xp, yp = 0, 0 # Bir önceki x ve y noktaları (çizgiyi kopuk değil pürüzsüz çekmek için)

# 5. Kamerayı başlatıyoruz
kamera = cv2.VideoCapture(0)
# Kamera çözünürlüğünü 640x480 olarak sabitliyoruz (tuval boyutuyla eşleşmesi kritik)
kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Air Canvas başlatıldı. Uygulamayı kapatmak için video ekranındayken 'q' tuşuna basın.")

while True:
    basarili_mi, kare = kamera.read()
    if not basarili_mi:
        break

    # Kameradan gelen görüntüyü ayna gibi ters çeviriyoruz ki sağ-sol karışmasın
    kare = cv2.flip(kare, 1)
    
    # MediaPipe RGB formatında çalıştığı için BGR'den RGB'ye çeviriyoruz
    rgb_kare = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB)
    
    # -----------------------------------------------------
    # EKRANA BUTONLARI ÇİZELİM (Sunumda hoca buraları çok sevecektir)
    # Temizle Butonu
    cv2.rectangle(kare, (40, 1), (140, 65), (255, 255, 255), -1)
    cv2.putText(kare, "TEMIZLE", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Renk Butonları (Koordinatlar elle ayarlandı)
    cv2.rectangle(kare, (160, 1), (255, 65), renkler[0], -1) # Mavi Buton
    cv2.rectangle(kare, (275, 1), (370, 65), renkler[1], -1) # Yeşil Buton
    cv2.rectangle(kare, (390, 1), (485, 65), renkler[2], -1) # Kırmızı Buton
    cv2.rectangle(kare, (505, 1), (600, 65), renkler[3], -1) # Sarı Buton
    # -----------------------------------------------------

    # El algılama işlemini yap
    sonuclar = eller.process(rgb_kare)

    # Eğer ekranda bir el tespit edildiyse
    if sonuclar.multi_hand_landmarks:
        for el_isaretleri in sonuclar.multi_hand_landmarks:
            
            # Seçili renk butonlarda belli olsun diye elin iskeletini çizebiliriz (isteğe bağlı)
            mp_cizim.draw_landmarks(kare, el_isaretleri, mp_eller.HAND_CONNECTIONS)
            
            # Tüm parmak uçlarının (landmark) koordinatlarını (x, y) piksel olarak listeye alalım
            lmList = []
            for id, lm in enumerate(el_isaretleri.landmark):
                h, w, c = kare.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))

            if len(lmList) != 0:
                # İşaret parmağının ucu (Landmark 8)
                x1, y1 = lmList[8]
                # Orta parmağının ucu (Landmark 12)
                x2, y2 = lmList[12]

                # Hangi parmaklar havada kontrol edelim
                parmaklar_havada = []
                
                # Sınıf sunumu için en basit mantık: 
                # Parmağın ucu (örn: 8), altındaki eklemden (örn: 6) daha YUKARIDAYSA (y değeri daha küçükse) parmak açıktır.
                
                # İşaret parmağı (8 numara, 6 numaranın üstünde mi?)
                if lmList[8][1] < lmList[6][1]:
                    parmaklar_havada.append(1) # İşaret havada
                else:
                    parmaklar_havada.append(0) # İşaret kapalı
                    
                # Orta parmak (12 numara, 10 numaranın üstünde mi?)
                if lmList[12][1] < lmList[10][1]:
                    parmaklar_havada.append(1) # Orta havada
                else:
                    parmaklar_havada.append(0) # Orta kapalı

                # -----------------------------------------------------
                # 1. DURUM: Hem İşaret hem Orta Parmak Havada -> SEÇİM MODU (Çizim durur)
                if parmaklar_havada[0] == 1 and parmaklar_havada[1] == 1:
                    xp, yp = 0, 0 # Çizgiyi kes (bir sonraki çizimde eskiye bağlanmasın diye sıfırlıyoruz)
                    
                    # Ekranda seçim yapıldığını göstermek için parmakların arasına bir dikdörtgen çizelim
                    cv2.rectangle(kare, (x1, y1 - 25), (x2, y2 + 25), renkler[renk_indeksi], cv2.FILLED)
                    
                    # Menü bölgesinde (y < 65) geziniyorsak butonlara tıklanmış sayılır
                    if y1 < 65:
                        if 40 < x1 < 140:   # Temizle Butonunun sınırları
                            cizim_tuvali = np.zeros((480, 640, 3), dtype=np.uint8) # Tuvali siyahla sıfırla
                        elif 160 < x1 < 255: # Mavi
                            renk_indeksi = 0
                        elif 275 < x1 < 370: # Yeşil
                            renk_indeksi = 1
                        elif 390 < x1 < 485: # Kırmızı
                            renk_indeksi = 2
                        elif 505 < x1 < 600: # Sarı
                            renk_indeksi = 3

                # -----------------------------------------------------
                # 2. DURUM: Sadece İşaret Parmağı Havada -> ÇİZİM MODU
                if parmaklar_havada[0] == 1 and parmaklar_havada[1] == 0:
                    # Nereyi çizdiğimizi görmek için işaret parmağının ucuna küçük bir daire koyalım
                    cv2.circle(kare, (x1, y1), 15, renkler[renk_indeksi], cv2.FILLED)
                    
                    # Eğer çizime yeni başlıyorsak (xp ve yp sıfırsa), bulunduğumuz noktadan başla
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1
                        
                    # Önceki nokta ile şu anki nokta arasına kalın bir çizgi çek (pürüzsüz görünüm için)
                    # Görüntüye değil, görünmez siyah tuvalimize çiziyoruz ki kalıcı olsun!
                    cv2.line(cizim_tuvali, (xp, yp), (x1, y1), renkler[renk_indeksi], firca_kalinligi)
                    
                    # Güncel noktayı, bir sonraki adımın "önceki noktası" olarak kaydet
                    xp, yp = x1, y1

    # -----------------------------------------------------
    # GÖRÜNTÜLERİ BİRLEŞTİRME (Maskeleme İşlemi)
    # Arka planda çizdiğimiz çizgileri (cizim_tuvali) asıl kamera görüntüsünün üzerine bindirme
    gri_tuval = cv2.cvtColor(cizim_tuvali, cv2.COLOR_BGR2GRAY)
    _, maske = cv2.threshold(gri_tuval, 50, 255, cv2.THRESH_BINARY_INV) # Çizim yapılan yerleri siyah, diğer yerleri beyaz yapar
    
    kare = cv2.bitwise_and(kare, kare, mask=maske) # Asıl görüntüde çizim yapılan yerlerin altını boşaltır
    kare = cv2.bitwise_or(kare, cizim_tuvali)      # Çizim tuvalindeki renkli çizgileri o boşluklara yerleştirir

    # Ekranda sonucu göster
    cv2.imshow("Air Canvas - Sinif Sunumu", kare)

    # 'q' tuşuna basılırsa döngüyü kır ve çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamerayı serbest bırak ve pencereleri kapat
kamera.release()
cv2.destroyAllWindows()