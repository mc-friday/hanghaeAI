## AWS 할당량 증가 요청

## 1. AWS EC2 Instance 생성

---

### 1.1 AWS 가입 및 할당량 증가 요청

1. [aws.amazon.com](http://aws.amazon.com)에 접속한 후, 오른쪽 위의 버튼을 눌러 콘솔로 이동합니다. 만약 로그인을 요구한다면, 회원 가입을 진행한 뒤 로그인하시면 됩니다.
    
    ![AWS 로그인 페이지](sandbox:/mnt/data/스크린샷_2025-02-02_오후_4.54.31.png)
    
2. 오른쪽 위의 리전을 선택하는 메뉴를 눌러 리전을 **“아시아 태평양 (서울)”**로 변경해줍니다.
    
    ![AWS 리전 변경](sandbox:/mnt/data/스크린샷_2025-02-02_오후_4.54.44.png)
    
3. 왼쪽 위의 검색 창에서 **“Service Quotas”**를 검색한 후 해당 메뉴에 들어갑니다.
    
    ![Service Quotas 검색](sandbox:/mnt/data/aws3.jpeg)
    
4. 가운데 대시보드에서 “**Amazon EC2**”를 선택합니다.
    
    ![EC2 선택](sandbox:/mnt/data/aws4.png)
    
5. 가운데 검색창에서 “Demand G”를 검색하여 선택한 후, 오른쪽의 “계정 수준에서 증가 요청”을 누릅니다.
    
    ![할당량 증가 요청](sandbox:/mnt/data/aws5.png)
    
6. “**할당량 값 증가**”에 숫자 8을 입력한 후, “**요청**”을 누릅니다.
    
    ![할당량 증가 값 입력](sandbox:/mnt/data/aws6.png)
    
7. 하루 정도가 지나면 할당량 증가 요청이 승인되었다는 메일이 날라옵니다. ***할당량은 리전별로 조절 할 수 있으니, 반드시 리전을 확인해 주세요!***

### 1.2 GPU instance 할당받기

1. 할당량 증가 요청을 할 때와 똑같이 AWS 콘솔에 들어간 후, 리전을 “**아시아 태평양 (서울)**”로 변경합니다.

2. 검색 창에서 “**EC2**”를 검색한 후 해당 메뉴에 들어갑니다.
    
    ![EC2 검색](sandbox:/mnt/data/aws7.png)
    
3. 가운데 “**인스턴스 시작**” 버튼을 누릅니다.
    
    ![인스턴스 시작](sandbox:/mnt/data/aws8.png)
    
4. OS를 Ubuntu 24.04로 설정해줍니다.
    
    ![Ubuntu 선택](sandbox:/mnt/data/aws9.png)
    
5. 인스턴스 유형에서 “**g4dn**”을 검색한 후 “**g4dn.xlarge**”를 선택합니다(비용을 고려하여 다른 종류의 g4dn 인스턴스를 사용하셔도 좋습니다).
    - (비용 참고)
        
        ![인스턴스 유형 선택](sandbox:/mnt/data/aws10.png)
    
6. “**키 페어(로그인)**” 메뉴에서 먼저 “**키 페어 생성**”을 눌러 키를 다운로드 받은 후, 그 키를 선택해줍시다. 다운로드 받은 키는 `~/.ssh` 폴더에 옮겨둡니다.
    
    ![키 페어 생성](sandbox:/mnt/data/aws11.png)
    
7. HTTP와 HTTPS 연결을 허용해줍니다.
    
    ![HTTP/HTTPS 연결 허용](sandbox:/mnt/data/aws12.png)
    
8. 스토리지 구성에서 용량을 최소 100GB로 설정하고, 오른쪽의 “**인스턴스 시작**”을 눌러줍니다.
    
    ![스토리지 설정](sandbox:/mnt/data/aws13.png)
    
9. 다시 EC2 메뉴로 돌아와, “**인스턴스**”를 눌러줍시다.
    
    ![EC2 인스턴스 보기](sandbox:/mnt/data/aws14.png)
    
10. 생성된 인스턴스를 선택한 후, 아래의 “**퍼블릭 IPv4 주소**”를 복사합니다.
    
    ![퍼블릭 IP 확인](sandbox:/mnt/data/aws15.png)
    
11. 터미널에 `ssh -i ~/.ssh/<키 이름>.pem ubuntu@<퍼블릭 IPv4주소>` 를 입력하면 생성한 인스턴스에 접근할 수 있습니다.

### 1.3 인스턴스 중지

1. EC2 메뉴로 들어갑니다.
    
    ![EC2 메뉴](sandbox:/mnt/data/aws16.png)
    
2. 인스턴스를 눌러줍니다.
    
    ![인스턴스 목록](sandbox:/mnt/data/aws17.png)
    
3. 중지하고자 하는 인스턴스를 누른 뒤, 상태를 중지로 바꿔줍니다.
    
    ![인스턴스 중지](sandbox:/mnt/data/aws18.png)

---

이제 AWS EC2 인스턴스 할당량 증가 요청과 GPU 인스턴스 생성이 완료되었습니다! ✅

