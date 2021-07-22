import sys
import cv2 as cv
import numpy as np
import json
import pyrebase


#기본 프로그램 구성 : 이미지 origin과 after 이미지 비교해서 그 차이가 크면 움직임이 있었다고 보기

video = cv.VideoCapture(2)
def motion_video():
    # 파이어베이스 연동과 db오픈
    with open("auth.json") as f :
        config = json.load(f)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()


    if not video.isOpened():
        print('비디오 open 실패!')
        sys.exit()

    #origin 이미지 확보
    suc,origin_img = video.read()
    #이미지 가지고 와서 처리하는데, 빠른 처리를 위해 그레이스케일로 변경함.
    origin_img = cv.cvtColor(origin_img, cv.COLOR_BGR2GRAY)
    #노이즈 제거(흐릿한 이미지를 만듦으로써)// 두 번째 인자는 커널 크기.(주로, 0,0  5,5  21,21을 쓰는듯)
    origin_img = cv.GaussianBlur(origin_img, (21, 21), 1.0) # 가까운 픽셀은 높은 가중치를 멀리있는 픽셀은 낮은 가중치를 줌으로써 필터결과 퀄리티를 높임.


    while True:
        success, frame = video.read()

        if not success:
            break
        else:
            users = db.child("motion").get()
            for x in users.each():
                # print(x.key(), x.val())
                if x.val() == "true":  # 야간모드의 경우
                    print("야간모드")
                    frame = np.clip(frame * 2.0, 0, 255).astype('uint8') #밝기를 높여 새로운 이미지 생성



            next_frame= cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            next_frame=cv.GaussianBlur(next_frame, (21, 21), 1.0)

            # 이전 origin 이미지와 현재 이미지를 비교한다.
            compare_value= cv.absdiff(origin_img,next_frame)

            #비교한 값의 임계값 처리
            #=> 비교값이 50을 넘기면 255(흰색)로 아니라면 0(검정)으로 지정함.
            # 비교값, 감도(임계값), 지정하는 값, type=cv2.THRESH_BINARY(픽셀 값이 임계값을 넘으면 value로 지정하고, 넘지 못하면 0으로 지정)
            thresh = cv.threshold(compare_value, 50, 255,cv.THRESH_BINARY)[1] # 여기 값이 튜플이기에 1 지정 안 하면 에러남.

            # threshhold로 얻은 값을 극대화하기 위해 dilate 사용.(하얀 부분을 확장)
            thresh_after_dilate = cv.dilate(thresh, (3,3),iterations=2) # (1,1)(3,3)(5,5)가 있는데, (3,3)이 제일 적당한 듯.

            #레이블링을 사용하여 객체들 끼리 구분하고, 각 객체에 번호를 매기고 위치와 크기 정보를 추출한다.
            cnt, labels, stats, centroid = cv.connectedComponentsWithStats(thresh_after_dilate)# findContours를 써도 무방함.

            obj_area_sum = 0

            for j in range(1, cnt):
                x, y, w, h, obj_area = stats[j] #x,y,가로,세로,객체 넓이(픽셀수)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2) # 이 직사각형들이 감지되는 객체들인데, 이것들의 합으로 감도설정

                obj_area_sum= obj_area_sum+obj_area


            if obj_area_sum > 50 : # 변한 area 들의 합이 50보다 크면
                signin = {"stat": "true"}
                db.child("motion_detect").set(signin)

                print("움직임 감지")

            else :
                signin = {"stat": "false"}
                db.child("motion_detect").set(signin)

                print("움직임 미감지")



            origin_img = next_frame.copy() # 기존 이미지로 나중에 들어온 이미지로 바꾼다.

            # 이 부분이 없으면 웹브라우저에 내 영상이 뜨지 않음.
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'

                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    video.release()
    cv.destroyAllWindows()


