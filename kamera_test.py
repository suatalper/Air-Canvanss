import cv2

kamera = cv2.VideoCapture(0)
while True :
    basarli_mi , kare = kamera.read()
    cv2.imshow("Air Canvans Projesi",kare)

    if cv2.waitKey(1) & 0xFF == ord('q'): # İşletim sisteminden gelen karmaşık klavye sinyallerini temizleyip, sadece basılan tuşun saf (8-bit) değerini almak için maskeleme yapar.
        break
kamera.release()
cv2.destroyAllWindows()