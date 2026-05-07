import cv2
from mtcnn import MTCNN

frontal_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
profile_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

mtcnn_detector = MTCNN()


##########################################
# Live camera function with MTCNN and Haar
##########################################

def live_camera():
    capture = cv2.VideoCapture(0)

    if not capture.isOpened():
        print("Error: Could not access the camera")
        return

    # Set resolution
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Press any key to exit live camera...")

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eq = cv2.equalizeHist(gray)
        gauss = cv2.GaussianBlur(frame, (15, 15), 0)
        bilat = cv2.bilateralFilter(frame, 9, 75, 75)

        # Sobel
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobelx = cv2.convertScaleAbs(sobelx)
        sobely = cv2.convertScaleAbs(sobely)
        sobel_combined = cv2.addWeighted(sobelx, 0.5, sobely, 0.5, 0)

        # Canny
        canny = cv2.Canny(gray, 100, 200)

        # Threshold
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

        # Haar Face Detection
        faces_frontal = frontal_face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        faces_profile = profile_face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        for (x, y, w, h) in faces_frontal:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
        for (x, y, w, h) in faces_profile:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        # MTCNN Face Detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mtcnn_detector.detect_faces(rgb_frame)

        for res in results:
            x, y, w, h = res['box']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # green box
            for point in res['keypoints'].values():
                cv2.circle(frame, point, 2, (0, 0, 255), -1)

        # Display all windows
        cv2.imshow("Original + Face Detection", frame)
        cv2.imshow("Grayscale", gray)
        cv2.imshow("Equalized", eq)
        cv2.imshow("Gaussian Blur", gauss)
        cv2.imshow("Bilateral Filter", bilat)
        cv2.imshow("Sobel X", sobelx)
        cv2.imshow("Sobel Y", sobely)
        cv2.imshow("Sobel Combined", sobel_combined)
        cv2.imshow("Canny", canny)
        cv2.imshow("Thresholded", thresh)

        if cv2.waitKey(1) != -1:
            break

    capture.release()
    cv2.destroyAllWindows()


####################################
# Face detection using Haar cascades
####################################

def detect_faces_on_image(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: {img_path} not found.")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces_frontal = frontal_face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    faces_profile = profile_face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    for (x, y, w, h) in faces_frontal:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
    for (x, y, w, h) in faces_profile:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)

    print(f"[Haar] Frontal faces detected: {len(faces_frontal)}")
    print(f"[Haar] Profile faces detected: {len(faces_profile)}")

    cv2.imshow(f"Haar Face Detection: {img_path}", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


############################
# Face detection using MTCNN
############################

def mtcnn_face_detection(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: {img_path} not found.")
        return

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = mtcnn_detector.detect_faces(rgb_img)

    for res in results:
        x, y, w, h = res['box']
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        for point in res['keypoints'].values():
            cv2.circle(img, point, 2, (0, 0, 255), -1)

    print(f"[MTCNN] Faces detected: {len(results)}")

    cv2.imshow(f"MTCNN Face Detection: {img_path}", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == "__main__":

    # 1. Live camera with MTCNN and Haar
    live_camera()

    # 2. Haar cascades on static image
    detect_faces_on_image("oscar.jpg")

    # 3. MTCNN on static image
    mtcnn_face_detection("oscar.jpg")
