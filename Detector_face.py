import tensorflow as tf
import numpy as np
import cv2
rate = 15  # 모자이크에 사용할 축소 비율(1/rate)


resize_and_crop = tf.keras.Sequential([
    tf.keras.layers.experimental.preprocessing.RandomCrop(height=224, width=224),
    tf.keras.layers.experimental.preprocessing.Rescaling(1./255)
])

face_detector_model = cv2.dnn.readNet(
    'models/face_mask_recognition.prototxt',
    'models/face_mask_recognition.caffemodel'
)

detector = cv2.VideoCapture(0)

while detector.isOpened():
    ret, image = detector.read()
    if not ret:
        break

    height, width = image.shape[:2]

    blob = cv2.dnn.blobFromImage(image, scalefactor=1., size=(300, 300), mean=(104., 177., 123.))
    face_detector_model.setInput(blob)
    face_locations = face_detector_model.forward()

    result_image = image.copy()

    for i in range(face_locations.shape[2]):
        confidence = face_locations[0, 0, i, 2]
        if confidence < 0.5:
            continue

        left = int(face_locations[0, 0, i, 3] * width)
        top = int(face_locations[0, 0, i, 4] * height)
        right = int(face_locations[0, 0, i, 5] * width)
        bottom = int(face_locations[0, 0, i, 6] * height)

        face_image = image[top:bottom, left:right]
        face_image = cv2.resize(face_image, dsize=(224, 224))
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

        rc_face_image = resize_and_crop(np.array([face_image]))

        color = (0, 255, 0)

        cv2.rectangle(
            result_image,
            pt1=(left, top),
            pt2=(right, bottom),
            thickness=2,
            color=color,
            lineType=cv2.LINE_AA
        )

    cv2.imshow('result', result_image)
    if cv2.waitKey(1) == ord('q'):
        break

detector.release()
