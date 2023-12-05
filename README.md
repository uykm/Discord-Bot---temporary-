리그오브레전드 P.S Bot <img src="https://i.ibb.co/4f1nw7T/P-S.webp" width="35px" height="35px" title="px(픽셀) 크기 설정" alt="P.S"></img>
=
프로젝트 참여자
-
|학과|학번|이름|
|---|---|---|
|컴퓨터공학과|20101246|신민규|

프로젝트 동기 & 설명
-
전 세계 게임들 중 가장 많은 유저 수를 지닌 게임들 중 하나이며 저도 오랫동안 즐기고 있는 **리그 오브 레전드(League of Legend)** 게임이 이렇게나 오래 인기를 끌 수 있었던 이유는 타 AOS 게임보다 진입 장벽은 낮췄다는 점에 있습니다. 그렇다고 해도, 10년이 넘는 시간 동안 축적된 데이터와 매번 업데이트 되는 패치내용으로 인해 알아야 할 것이 적다고 할 수 없고, 랭크를 높이기 위해선 더더욱이 그러한 사항을 인지하고 있어야 합니다. 그렇기 때문에, 챔피언 빌드를 알려주는 사이트인 [OP.GG](https://www.op.gg/champions) 나 게임의 메타와 공략을 알려주는 유튜브 [프로 관전러 P.S](https://www.youtube.com/@ProfessionalSpectator) 같은 것들이 자연스럽게 롤의 인기도에 비례하는 인기를 누리게 된 것입니다. 따라서, 저는 이 **프로 관전러 P.S**를 모티브로 한 디스코드 봇을 만들게 되었습니다.   
> 개발자 레퍼런스에서 "애플리케이션을 사고 팔고 누구나 만들 수 있는 개발 환경과 오픈 소스를 제공해줬던 것처럼 Chatgpt 같은 Open AI를 누구나 만들어보고 자신에게 맞는 '맞춤형 챗GPT'를 만들어볼 수 있는 시대가 올 것이다." 라고 했다는 이야기를 듣고, Open Source Software 텀프로젝트로 '맞춤형 챗GPT' 같은 나에게 필요한 인공지능 봇을 만들어보고 싶다는 생각도 있었습니다.
</br>

### ● 왜 디스코드 봇인가?
</br>

* 디스코드 플랫폼에서 인공지능 봇을 쉽게 만들어볼 수 있도록 기능을 제공해주기 때문에, 저 같이 인공지능 봇을 만들어본 경험이 없는 사람은 디스코드 봇을 만들어 보는 것도 괜찮겠다는 생각이 들었습니다.

</br>

* **롤**과 **디스코드**는 뗄레야 뗄 수 없는 관계인데, 이 점을 이용해서 재작년 Open Source Software 수업에서 어떤 팀이 롤 관련 서비스를 해주는 [꿀벌봇](https://github.com/NyaNyak/discord-beebot/tree/main)이라는 봇을 만든 것을 보고 아이디어가 되게 괜찮다고 생각했습니다. 하지만, 2년 전에 만들어진 만큼 **최신 업데이트 내용을 반영하지 못하고 있고**, 최근 바뀐 닉네임 형식이 로직에 반영되지 않았다는 점과 마찬가지로 그러한 변경사항을 아직 반영하지 못한 웹 사이트인 [your.gg](https://your.gg/ko/kr/home)에서 데이터를 얻어온다는 점에서 문제가 있었습니다. 앞서 말한 문제를 Riot API를 이용해 고치고 롤을 10년 넘게 하면서 얻은 경험들을 기반으로 **새로운 기능**을 추가해보고 싶다는 생각이 들었습니다.

</br>

프로젝트 후기
-
```
* 
* Riot API rate limits로 인한 429 error 발생
```

</br>

P.S 봇 사용법 (사용자)
-
### ● 
1. 
2. [P.S 봇 초대 링크](https://discord.com/api/oauth2/authorize?client_id=1179801477712195696&permissions=8&scope=bot)를 통해 P.S 봇을 사용하고 싶은 서버로 초대합니다.</br> (단, 해당 서버에 대한 '관리자 권한'이 있어야만 초대 가능합니다.)
3. 

</br>

### ● P.S 봇 명령어
</br>

* !전적검색 닉네임#태그 (ex. !전적검색 민규#TAG)
> 해당 유저의 정보를 확인해볼 수 있습니다.
</br>

* !인게임분석 닉네임#태그 (ex. !인게임분석 민규#TAG)
> 해당 게임에서 누구와 게임을 풀어나가야 할지, 적팀에서 누구를 조심해야 할지를 승률에 기반해서 알려줍니다.

</br>

P.S 봇 사용법 (개발자)
-
1) 디스코드 사용자 설정(톱니바퀴) > 고급 > 개발자 모드 ON

2) 파이썬 초기 개발 환경을 세팅합니다. </br> (콘솔 창에 *pip intall discord*를 입력해 dicord 패키지를 설치해줘야 하는데, *pip*가 설치가 돼있어야 합니다.)

3) 로컬 리포지터리로 **git clone** 합니다.

4) [디스코드 개발자 포털](https://discord.com/developers/applications)로 접속한 후, 우측 상단 [New Application]을 클릭합니다.

5) 좌측 Bot 탭으로 이동한 하여 [Add Bot]을 클릭한 다음, 아래처럼 Intents 관련 설정을 모두 ON으로 바꿔줍니다. (무조건)
![image](https://github.com/uykm/P.Sbot-Discord/assets/98581610/3d846094-2cd4-46ae-ac1b-9a967d91668b)

6) OAuth2 탭 -> URL Generater 에서 Scopes - bot 체크, Bot Permissions - Administrator 를 체크 해주면 URL이 생성됩니다.

7) 이 URL은 봇을 서버에 초대할 때 사용됩니다. URL로 접속하여 서버에 봇을 초대해 줍니다.

8) 다시 Bot 탭으로 돌아와 token 을 카피 해준 후, 이를 로컬 레포지토리 내에 token 파일 (확장자 없는 텍스트 파일)로 붙여넣어 줍니다.

9) main.py 를 실행시키면 봇이 온라인으로 전환되며 정상적으로 작동할 것입니다

</br>

사용한 API
-
### Riot API
* https://developer.riotgames.com/apis (API 명세서)

</br>

참고 자료
-

</br>

* [Tistory - 김윤웅](https://yunwoong.tistory.com/212)
> 디스코드 봇 초기 세팅을 할 때 참고했습니다.

</br>

* [Tistory - Nerdy](https://whiplash-bd.tistory.com/42)
> Riot API 명세서에 대한 설명을 참고했습니다.

</br>

* [GitHub - NyaNyak](https://github.com/NyaNyak/discord-beebot)
> 1. 코드 구조를 참고했습니다.  
> 2. 챔피언 이름(한글/영어) 딕셔너리 파일(chamDB.py)을 그대로 가져와서 몇 가지 챔피언을 추가했습니다.  
> 3. 전적 검색 결과를 표현하는 UI 디자인 코드(search.py)를 사용했습니다.

</br>

License
-
이 오픈소스는 [MIT License](https://github.com/uykm/P.Sbot-Discord/blob/main/LICENSE)를 기반으로 하고 있습니다.


