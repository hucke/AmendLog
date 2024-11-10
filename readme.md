기능
1. 커널로그에서 ddk 로그를 추출해서 저장
2. ddk 로그를 분석
    - chain, object의 lifetime 분석
    - stream의 lifetime 분석, preview용인지 reprocessing용인지
    - scenario index 및 tune id 분석

사용법

구현 설명

    먼저 log 파일에서 null 문자 같은 것을 제거.
