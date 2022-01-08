import io
import socket
import struct
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
 
# socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# read model
facenet = cv2.dnn.readNet('models/deploy.prototxt', 'models/res10_300x300_ssd_iter_140000.caffemodel')
model = load_model('models/mask_detector.model')
 
server_socket, server_addr = server_socket.accept()
connection_Image = server_socket.makefile('rb')

try:
    while True:
        image_len = struct.unpack('<L', connection_Image.read(struct.calcsize('<L')))[0]
        if not image_len:  # 이미지 크기 0일경우 멈춤
            break

        image_stream = io.BytesIO()
        image_stream.write(connection_Image.read(image_len))

        image_stream.seek(0)
        img = Image.open(image_stream)
        #img.show()
        
        # JPEG -> JPG 변환 필요
        img = img.save("./imgs/face.jpg")
        img = cv2.imread('imgs/face.jpg')
        
        # detecting part
        h, w = (640, 480)

        blob = cv2.dnn.blobFromImage(img, scalefactor=1., size=(300, 300), mean=(104., 177., 123.))
        facenet.setInput(blob)
        dets = facenet.forward() # 얼굴 검출
        
        faces = []
        for i in range(dets.shape[2]):
            confidence = dets[0, 0, i, 2]
            if confidence < 0.5:
                continue

            x1 = int(dets[0, 0, i, 3] * w)
            y1 = int(dets[0, 0, i, 4] * h)
            x2 = int(dets[0, 0, i, 5] * w)
            y2 = int(dets[0, 0, i, 6] * h)
            
            face = img[y1:y2, x1:x2]
            faces.append(face)


        # 검출 여부 확인 후 클라이언트로 전송
        if len(faces) is 0:
            msg = 'Nobody'
        else:
            face = faces[0]
            face_input = cv2.resize(face, dsize=(224, 224))
            face_input = cv2.cvtColor(face_input, cv2.COLOR_BGR2RGB)
            face_input = preprocess_input(face_input)
            face_input = np.expand_dims(face_input, axis=0)
                
            mask, nomask = model.predict(face_input).squeeze()
            result = mask*100
            print(result)

            if (mask*100) > 80:
                print('Verified. You can come in!')
                msg = 'OK'
            else:
                print('not allowed')
                msg = 'NO'
        image_stream.seek(0)
        image_stream.truncate(0)
        server_socket.send(msg.encode())  # 전송

finally:
    connection_Image.close()
    server_socket.close()
