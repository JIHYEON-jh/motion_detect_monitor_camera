import cv2

import numpy as np
import datetime


camera = cv2.VideoCapture(0) #노트북 내장 웹캠

import json
import pyrebase


# 파이어 베이스 연동 준비
with open("auth.json") as f :
    config = json.load(f)
firebase = pyrebase.initialize_app(config)
db = firebase.database()




#yolo 알고리즘 로드하기
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg") # 네트워크를 메모리에 로드함.
classes = [] # 클래스 로드하기 위한 리스트

with open("coco.names","r") as f : # 데이터셋에서 분류하는 클래스 이름 얻어오기.
    classes = [line.strip() for line in f.readlines()] 


# 출력 레이어를 얻음으로써 물체 감지.
layer_name = net.getLayerNames() # yolo의 layer들의 이름을 받아옴.
output_Layers = [layer_name[i[0]-1] for i in net.getUnconnectedOutLayers()] # 출력 레이어의 인덱스를 가져옴.




# 사람이 감지된 시간에 대한 정보
detect_time = []
# 사람 감지가 안 된 시간
person_undetect_state=[]
#미감지 알림을 db에 보냈는지 상태.
send_flag_db = []

# 사람 감지 상태 리스트에 값 추가하고 리턴하는 함수
def detect_state_change(flag):

    if flag == 1:  # is_or_not_flag 값을 받아와서 그 사람이 있다고 인지가 되면
        person_undetect_state.clear()  # 다시 얼굴이 나타난 것이기에 리스트를 초기화함.
        send_flag_db.clear() # 로그 기록을 보낸 flag 리스트를 리셋함.
        return 0

    else:  # 사람이 감지가 안 되면 그 시간을 사람 미감지 상태 리스트에 적어둠.
        person_undetect_state.append(datetime.datetime.now())  # 현재 시간을 추가함.

        if (len(person_undetect_state) > 1):  # 리스트에 감지된 값이 1개 보다 큰 경우에는 시간차이 확인 가능
            first_differ_last = person_undetect_state[-1] - person_undetect_state[0]  # 마지막으로 감지된 시간과 최초로 감지된 시간의 차이.
            if (first_differ_last.seconds >= 5):  # 그 차이가 5보다 크거나 같으면 알림.
                if len(send_flag_db)==0 :
                    # 해당하는 시간을 로그로서 기록해둔다.
                    date_string = person_undetect_state[0].strftime('%Y-%m-%d-%H-%M-%S')
                    data = {"date":date_string}
                    db.child("person_detect_log").push(data)

                    #현재 사람이 없음을 db에 표시
                    print("사람이 없어요!!!!")
                    signin = {"stat": "false"}
                    db.child("person_detect").set(signin)

                    send_flag_db.append("보낸 적 있음.")
                    return

# main 코드에서 직접 부를 함수
def gen_frames():
    while True:
        ret, frame = camera.read()

        if not ret:
            break

        else:
            img = cv2.resize(frame, None, fx=0.4, fy=0.4)

            # 야간 모드인지 확인 후 밝기 조절.
            users = db.child("person").get()
            for x in users.each():
                if x.val() == "true":#야간모드의 경우
                    print("야간모드")
                    img = np.clip(img * 2.0, 0, 255).astype('uint8') #밝기를 높여 새로운 이미지 생성


            # blob형태로 바뀐 객체가 아닌 원본 img에 대한 height,width,채널값을 저장.
            height, width, channels = img.shape

            # 객체 감지
            blob = cv2.dnn.blobFromImage(img, 1 / 255, (320, 320), (0, 0, 0), True, crop=False)  # blob객체로 만들기 위해 사용

            net.setInput(blob)  # 만들어진 blob객체를 네트워크에 집어넣는다.
            out_result = net.forward(output_Layers) #순방향으로 네트워크 실행.


            # 이미지에서 검출된 객체에 대한 정보를 따로 저장할 리스트 준비
            boxes = []  # 직사각형 영역
            class_ides = [] # 해당하는 객체의 id
            confidences = []

            for out in out_result:
                for detection in out:
                    scores = detection[5:]  # 5번 이후부터가 각 클래스에 대한 가능성 값.
                    class_name = np.argmax(scores)  # 가능성 값들 중 가장 큰 것을 찾아서 해당하는 객체로 정의.
                    confidence = scores[class_name]  # 예측한 확률(confidence)을 얻어옴.

                    # 신뢰도는 0부터 1 사이의 값으로 나오는데, 일단 0.5이상이면 ok라고 정함.
                    if confidence > 0.5:
                        # 지금 정규화된 상태이기에 각각 원래의 img로부터의 너비와 높이를 곱함.
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)  # 객체에 대한 width와 height
                        h = int(detection[3] * height)


                        # 직사각형으로 객체 표시하기(각각 x,y는 객체의 왼쪽 상단의 좌표.)
                        x = int(center_x - w / 2)  # 객체의 너비를 반 나눈 것을 중앙x좌표에서 빼면 그 값이 나옴.
                        y = int(center_y - h / 2)


                        boxes.append([x, y, w, h])  # 직사각형 표시를 위한 변수들
                        confidences.append(float(confidence))
                        class_ides.append(class_name)

                # 박스가 여러 겹으로 겹쳐지지 않도록 노이즈 제거가 필요.
                noise_index = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)  # 제거할 대상들, 확률 , 점수임계값 , nms 임계값

                num_object_detect = len(boxes)  # 감지 가능한 박스의 개수

                is_or_not_flag = 0  # 사람이 있는지 없는지 표시하기 위한 flag(없는 상태 0으로 시작)
                for i in range(num_object_detect):  # 감지한 박스의 개수만큼 돌림.
                    if i in noise_index:  # noise_index에 있는 것들만 출력하도록 함.

                        if class_ides[i] == 0:  # classes의 0번 인덱스 값은 person.
                            print("사람이 있습니다.")
                            signin = {"stat": "true"}
                            db.child("person_detect").set(signin)

                            is_or_not_flag = 1  # 해당 프레임에 사람이 감지가 되었음.

                # 사람감지상태 리스트를 flag를 통해 변경함.
                detect_state_change(is_or_not_flag)



            # 이 부분이 없으면 웹브라우저에 내 영상이 뜨지 않음.
            ret, buffer = cv2.imencode('.jpg', img) #인코딩
            img = buffer.tobytes()

            yield (b'--frame\r\n'

                   b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
