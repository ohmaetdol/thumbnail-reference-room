# 썸네일 비교실

YouTube 레퍼런스 주소 4개와 우리 썸네일·제목을 함께 비교하는 한국어 도구입니다.

- 공개 영상 URL → 제목·썸네일·채널 자동 조회
- 우리 이미지 업로드와 제목 입력
- 다섯 썸네일 동일 크기 비교 및 168px 가독성 확인
- 참고 메모, 이미지 포함 JSON 작업 저장·불러오기

## 사용

https://ohmaetdol.github.io/thumbnail-reference-room/

설치와 로그인, API 키가 필요하지 않습니다. 주소 붙여넣기 또는 일괄 불러오기로 시작하세요. 이미지·제목·메모는 해당 브라우저에 저장됩니다. 기기를 바꿀 때는 작업 저장 JSON 파일을 옮겨 불러오세요.

## 데이터

정적 HTML/JS 도구입니다. 공개 영상 메타데이터는 브라우저에서 YouTube oEmbed로 조회합니다. 우리 이미지·제목·메모를 서버나 외부 모델에 전송하지 않습니다. 이미지 원본은 수정하지 않으며 브라우저 미리보기로 저장합니다. 다운로드한 JSON에는 이미지가 포함됩니다.

비공개·삭제·제한 영상이나 네트워크 제한에서는 자동 조회가 실패할 수 있습니다. CTR 예측이나 영상 본문 자동 분석 도구는 아닙니다.

## 개발

외부 패키지 없이 `python3 -m http.server 8643`으로 로컬 미리보기를 열 수 있습니다. GitHub Pages에서 main 브랜치 루트를 게시합니다.

독립 제작. 배치 비교 아이디어 참고: https://github.com/0xelitesystem/youtube-thumbnail-tester

## 조회수·댓글 수 자동 조회

새 YouTube 주소를 입력하면 전용 조회 서버에서 공개 조회수·댓글 수를 자동으로 가져옵니다. 별도의 키 입력이 필요하지 않습니다. 조회 서버는 최대 1시간 캐시를 사용하며 카드에 실제 수집 시각을 표시합니다. 비공개·삭제·제한 영상이나 YouTube 차단 등으로 실패할 수 있으며 미확인 값은 0으로 표시하지 않습니다. 서버 오류 시 기존 7개 참고 영상에는 저장된 확인값으로 대체할 수 있습니다.

공개 API: https://thumbnail-stats.srv2094495.hstgr.cloud/api/stats?id=VIDEO_ID

서버는 11자리 영상 ID만 받아 공개 통계 메타데이터를 수집합니다. 임의 URL, 영상·오디오·댓글 본문, 계정 정보를 수집하지 않습니다. 요청 빈도·동시성·타임아웃·리소스를 제한하고 HTTPS를 사용합니다. 우리 이미지·제목·메모는 조회 서버에 전송하지 않습니다. 선택형 공식 YouTube Data API 키 연결도 유지하며 키는 탭 메모리에서만 사용합니다.

server/app.py와 server/Dockerfile은 별도 조회 서비스 소스입니다. 기존 Hermes 서비스와 분리된 컨테이너로 운영하며 캐시로 수집 빈도를 제한합니다. YouTube 페이지 변경 시 유지보수가 필요할 수 있습니다.

기본 저장 통계 갱신: 설치된 yt-dlp로 `python3 scripts/refresh_stats.py`. 테스트: `node --test scripts/stats.test.mjs`.

공식 통계 항목: https://developers.google.com/youtube/v3/docs/videos
