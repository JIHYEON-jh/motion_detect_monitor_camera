package com.monitor.detectproj;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;
import java.util.List;

public class LogActivity extends AppCompatActivity {
    //데이터 베이스
    private FirebaseDatabase database;
    DatabaseReference ref_log;


    private ListView listView; // 리스트 뷰

    List logList = new ArrayList<>();
    ArrayAdapter adapter; // 리스트뷰와 연결을 위한 어댑터

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_log);


        listView= (ListView)  findViewById(R.id.loglist);
        adapter = new ArrayAdapter<String>(this, R.layout.activity_listview, logList); // 리스트항목에 해당하는 xml인 activity_listview
        listView.setAdapter(adapter); // 리스트뷰에 어댑터 연결


        //파이어 베이스와 연결
        database = FirebaseDatabase.getInstance();

        // 파이어 베이스에서 레퍼런스를 가져옴
        ref_log = database.getReference("person_detect_log");

        ref_log.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {//데이터베이스의 값이 변경되거나 추가될 때 실행됨.
                for (DataSnapshot messageData : dataSnapshot.getChildren()) {
                    String str = messageData.child("date").getValue(String.class);
                    logList.add(str);
                }
                adapter.notifyDataSetChanged();
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                Log.w("TAG: ", "Failed to read value", databaseError.toException());
            }
        });
    }
}