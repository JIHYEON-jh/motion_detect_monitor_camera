# motion_detect_monitor_camera




개요 : 실시간으로 모션과 객체 감시카메라로부터 데이터를 받아 back-end에서 처리 후 사용자의 핸드폰으로 알람을 받을 수 있도록 하는 어플리케이션.


프로그램 실행 순서
1. main.py 로 서버 실행시켜 둠.
2. motion_detect.py 와 video_detect.py 를 위해 내장 카메라와 외부 카메라 두 개를 준비시킨다.
3. MainActivity.java 을 이용해 핸드폰에 앱을 실행시킨다.


프로그램 작동
1. 두 개의 카메라는 각각 모션 감지와 객체 감지를 진행한다.
2. 만약, 화면에 객체로 지정된 ‘사람’이 사라지면 그에 대한 알람을 보내게 된다.
3. 또, 다른 것으로는 ‘사람’ 객체는 있으나, 그 사람의 움직임이 지정된 감도 이상으로 나타나지 않는다면 위기로 판단해 알림을 보낸다.



민감 데이터 => 파이어베이스를 위해 따로 채워 넣어야 하는 부분
- Android\app\build\generated\res\google-services\debug\values\values.xml
- Android\app\google-services.json
- Android\app\src\main\java\com\monitor\detectproj\MainActivity.java

- Python\auth.json
