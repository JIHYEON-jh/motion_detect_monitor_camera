from flask import Flask, render_template,Response

import motion_detect
import video_detect



app = Flask(__name__)

@app.route('/video_feed_web') # motion 감지.
def video_feed_web():
    return Response(motion_detect.motion_video(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed') # 사람 감지
def video_feed():
    return Response(video_detect.gen_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/') #기본 현재 루트 홈페이지 실행시 아래에 함수가 실행이 됨.
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8000", threaded=True)