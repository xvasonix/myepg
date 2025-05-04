#### MYEPG
1.
    1. <strong>ALive PlexProxy 연동 기능 추가</strong> (2025-05-05 기능 추가, 데브닉스)
2. 
    1. <strong>ALive m3uall tag-name 사용 : ON</strong> (2024-01-30 기능 추가)
        * alive m3uall 의 채널정보(tvg-name)를 사용해 EPG 생성
            <br>
            채널 정보 가져올 서비스 제공자 우선순위 : ['WAVVE', 'TVING', 'SPOTV', 'KT', 'LG', 'SK', 'DAUM', 'NAVER']
            <br><br>

    2. <strong>ALive m3uall tag-name 사용 : OFF</strong> (기존 기능)
        * 원하는 소스 선택 
        <br><br>

3. 설정 저장 
4. 즉시 실행 or 1회 실행
5. 테스트 마쳤으면 스케쥴링 설정 하고 api 입력 
  
<br><br>

---

#### 오라클 환경에서 WAVVE 관련된 서비스는 사용이 불가합니다. (Proxy로 우회시 가능)
* 오라클 환경에서는 [WAVVE 요청 차단] ON
* 오라클 환경에서 Proxy URL 을 설정했다면 : [WAVVE 요청 차단] OFF 
    * WAVVE 관련 Proxy URL 설정은 support_site플러그인의 WAVVE 탭에서 설정'
  
<br><br>

---
    
#### 사용된 패키지
  * [https://github.com/epg2xml/epg2xml](https://github.com/epg2xml/epg2xml)



