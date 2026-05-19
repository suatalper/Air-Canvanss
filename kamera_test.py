"""
PSEUDO CODE :
BAŞLA
    Kamerayı ve MediaPipe el modelini başlat
    Boş bir çizim tuvali (canvas) oluştur
    Renkleri tanımla (Mavi, Yeşil, Kırmızı, Sarı)

    DÖNGÜ: Kamera açık olduğu sürece
        Kameradan bir kare oku ve aynala
        Ekrana renk ve temizle butonlarını çiz
        Karedeki elleri tespit et

        EĞER el tespit edildiyse:
            Parmak uçlarının (Landmark) koordinatlarını bul

            EĞER İşaret ve Orta parmak havadaysa (Seçim Modu):
                Çizimi duraklat
                EĞER parmaklar butonların üzerindeyse:
                    Rengi değiştir VEYA tuvali tamamen temizle

            EĞER Sadece İşaret parmağı havadaysa (Çizim Modu):
                Seçili renk ile parmak ucunun koordinatlarına çizgi çek

        Çizim tuvalindeki çizgileri ana görüntüye kopyala
        Görüntüyü ekrana yansıt

        EĞER 'q' tuşuna basılırsa DÖNGÜDEN ÇIK
BİTİR
"""

import sys

sys.dont_write_bytecode = True

import cv2
import numpy as np
import mediapipe as mp

# MediaPipe kurulumu
mp_eller = mp.solutions.hands
eller = mp_eller.Hands(
    max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7
)
mp_cizim = mp.solutions.drawing_utils

# Çizim tuvali (canvas)
cizim_tuvali = np.zeros((480, 640, 3), dtype=np.uint8)

# Renkler (BGR formatı)
renkler = [
    (255, 0, 0),  # Mavi
    (0, 255, 0),  # Yeşil
    (0, 0, 255),  # Kırmızı
    (0, 255, 255),  # Sarı
]
renk_indeksi = 0
firca_kalinligi = 5
xp, yp = 0, 0

# Kamera başlatma
kamera = cv2.VideoCapture(0)
kamera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Air Canvas başlatıldı. Çıkmak için 'q' tuşuna basın.")

while True:
    basarili_mi, kare = kamera.read()
    if not basarili_mi:
        break

    kare = cv2.flip(kare, 1)
    rgb_kare = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB)

    # Arayüz butonları
    cv2.rectangle(kare, (40, 1), (140, 65), (255, 255, 255), -1)
    cv2.putText(
        kare,
        "TEMIZLE",
        (49, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.rectangle(kare, (160, 1), (255, 65), renkler[0], -1)
    cv2.rectangle(kare, (275, 1), (370, 65), renkler[1], -1)
    cv2.rectangle(kare, (390, 1), (485, 65), renkler[2], -1)
    cv2.rectangle(kare, (505, 1), (600, 65), renkler[3], -1)

    sonuclar = eller.process(rgb_kare)

    if sonuclar.multi_hand_landmarks:
        for el_isaretleri in sonuclar.multi_hand_landmarks:
            mp_cizim.draw_landmarks(kare, el_isaretleri, mp_eller.HAND_CONNECTIONS)

            lmList = []
            for id, lm in enumerate(el_isaretleri.landmark):
                h, w, c = kare.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))

            if len(lmList) != 0:
                x1, y1 = lmList[8]  # İşaret parmağı ucu
                x2, y2 = lmList[12]  # Orta parmak ucu

                parmaklar_havada = []

                # Parmak durumu kontrolü (uç nokta, eklemden yukarıda mı?)
                if lmList[8][1] < lmList[6][1]:
                    parmaklar_havada.append(1)
                else:
                    parmaklar_havada.append(0)

                if lmList[12][1] < lmList[10][1]:
                    parmaklar_havada.append(1)
                else:
                    parmaklar_havada.append(0)

                # DURUM 1: Seçim Modu (İki parmak havada)
                if parmaklar_havada[0] == 1 and parmaklar_havada[1] == 1:
                    xp, yp = 0, 0
                    cv2.rectangle(
                        kare,
                        (x1, y1 - 25),
                        (x2, y2 + 25),
                        renkler[renk_indeksi],
                        cv2.FILLED,
                    )

                    if y1 < 65:
                        if 40 < x1 < 140:
                            cizim_tuvali = np.zeros((480, 640, 3), dtype=np.uint8)
                        elif 160 < x1 < 255:
                            renk_indeksi = 0
                        elif 275 < x1 < 370:
                            renk_indeksi = 1
                        elif 390 < x1 < 485:
                            renk_indeksi = 2
                        elif 505 < x1 < 600:
                            renk_indeksi = 3

                # DURUM 2: Çizim Modu (Sadece işaret parmağı havada)
                if parmaklar_havada[0] == 1 and parmaklar_havada[1] == 0:
                    cv2.circle(kare, (x1, y1), 15, renkler[renk_indeksi], cv2.FILLED)

                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    cv2.line(
                        cizim_tuvali,
                        (xp, yp),
                        (x1, y1),
                        renkler[renk_indeksi],
                        firca_kalinligi,
                    )
                    xp, yp = x1, y1

    # Çizimleri ana görüntüyle birleştirme (Maskeleme)
    gri_tuval = cv2.cvtColor(cizim_tuvali, cv2.COLOR_BGR2GRAY)
    _, maske = cv2.threshold(gri_tuval, 50, 255, cv2.THRESH_BINARY_INV)

    kare = cv2.bitwise_and(kare, kare, mask=maske)
    kare = cv2.bitwise_or(kare, cizim_tuvali)

    cv2.imshow("Air Canvas", kare)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

kamera.release()
cv2.destroyAllWindows()
