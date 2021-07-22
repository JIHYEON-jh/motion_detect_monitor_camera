package com.monitor.detectproj;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.TextView;
import android.widget.ToggleButton;


import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class MainActivity extends AppCompatActivity {
    //데이터 베이스
    private FirebaseDatabase database;
    //데이터베이스의 정보
    DatabaseReference ref_person;
    DatabaseReference ref_motion;
    DatabaseReference night_Database;


    // 내부에서 사용할 상태 변수로 실시간으로 db로부터 확인하여 상태를 변경한다.
    String stat_of_person="false";
    String stat_of_motion;

    TextView person_alarm;
    TextView motion_alarm;

    //Switch night_switch;
    ToggleButton nightBtn;

    // Button log
    Button logBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 야간모드 스위치
        nightBtn = findViewById(R.id.nightBtn);

        // 로그 버튼
        logBtn = findViewById(R.id.logBtn);

        // 감지에 대한 각각의 textview
        person_alarm = (TextView)findViewById(R.id.alarmView_person);
        motion_alarm = (TextView)findViewById(R.id.alarmView_motion);

        // 웹캠 보여주기 => WebSettings를 얻어와서 이것이 자바 스크립트를 사용할수 있도록 만든 후 url 연결
        WebView webView = (WebView)findViewById(R.id.webcam_view);
        webView.setWebViewClient(new WebViewClient());

        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);

        // 연결 url ==> 해당하는 ip 주소를 입력
        webView.loadUrl("");



        //파이어 베이스와 연결
        database = FirebaseDatabase.getInstance();

        // 파이어 베이스에서 레퍼런스를 가져옴
        ref_person = database.getReference("person_detect");
        ref_person.addValueEventListener(new ValueEventListener(){

            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) { // 해당 경로의 값이 변경되면 실행함.
                String msg2 = null;
                for (DataSnapshot messageData : snapshot.getChildren()) {
                    stat_of_person = messageData.getValue().toString();
                }
                if(stat_of_person.equals("false"))
                    person_alarm.setText("사람이 없어요!");
                else
                    person_alarm.setText(" ");

            }
            @Override
            public void onCancelled(@NonNull DatabaseError error) {
            }
        });

        ref_motion = database.getReference("motion_detect");
        ref_motion.addValueEventListener(new ValueEventListener(){

            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                String msg2 = null;
                for (DataSnapshot messageData : snapshot.getChildren()) {
                    stat_of_motion = messageData.getValue().toString();
                }
                if(stat_of_person.equals("true") && stat_of_motion.equals("false")) //사람은 있지만 움직임이 없는 경우
                    motion_alarm.setText("움직임이 감지되지 않고 있습니다");
                else
                    motion_alarm.setText("");

            }
            @Override
            public void onCancelled(@NonNull DatabaseError error) {
            }
        });


        // 야간모드 리스너
        night_Database = database.getReference();
        nightBtn.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View view) {
                StringBuilder result = new StringBuilder();
                result.append(nightBtn.getText());
                if (result.toString().equals("ON")){ //야간모드가 켜져있을 경우
                    night_Database.child("motion").child("night_mode").setValue("true");
                    night_Database.child("person").child("night_mode").setValue("true");
                } else {
                    night_Database.child("motion").child("night_mode").setValue("false");
                    night_Database.child("person").child("night_mode").setValue("false");
                }
            }

        });

        // 로그 확인 버튼
        logBtn.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this, LogActivity.class);
                startActivity(intent);
            }
        });
    }
}