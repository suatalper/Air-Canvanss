import cv2
import mediapipe as mp

kamera = cv2.VideoCapture(0)

print("İçerideki Köstebeğin Adresi:", mp.__file__)

mp_eller = mp.solutions.hands
eller = mp_eller.Hands()
mp_cizim = mp.solutions.drawing_utils

while True :
    basarli_mi , kare = kamera.read()
    kare = cv2.flip(kare,1)
    rgb_kare = cv2.cvtColor(kare,cv2.COLOR_BGR2RGB)
    sonuclar = eller.process(rgb_kare)
    print(sonuclar.multi_hand_landmarks)
    yukseklik , genislik ,renk_kanalleri = kare.shape
    merkez_x = genislik // 2
    merkez_y = yukseklik // 2
    cv2.circle(kare ,(merkez_x,merkez_y),50,(0,0,255),2)
    cv2.imshow("Air Canvans Projesi",kare)

    if cv2.waitKey(1) & 0xFF == ord('q'): # İşletim sisteminden gelen karmaşık klavye sinyallerini temizleyip, sadece basılan tuşun saf (8-bit) değerini almak için maskeleme yapar.
        break

kamera.release()
cv2.destroyAllWindows()