# Gryannote 개발 요청 및 변경 이력

Branch: `claude/gryannote-dev-server-badnxp`

---

## 1. Docker 개발 환경 구축

**요청**: 개발 서버를 Docker 기반으로 구성하여 `61.37.46.114:7860`에서 접근 가능하게 할 것

**변경사항**:
- `Dockerfile.dev`: Python 3.11-slim, Node.js 22, ffmpeg, libsndfile1 기반 빌드
- `docker-compose.yml`: 포트 7860, `GRADIO_SERVER_NAME=0.0.0.0` 설정
- Gradio 5.19.0 핀 버전, 프론트엔드 템플릿 빌드 환경 구성
- `gradio_client` boolean schema 패치 및 `@gradio/preview` TypeScript import type 패치

**관련 파일**: `Dockerfile.dev`, `docker-compose.yml`, `patches/`

---

## 2. GPU 지원

**요청**: 5개의 GPU 카드 중 다섯 번째(4번)를 사용하여 백엔드를 GPU 모드로 실행할 것

**변경사항**:
- CUDA 12.1 기반 PyTorch/torchaudio 설치
- `docker-compose.yml`에 NVIDIA GPU device 4 설정 (`device_ids: ['4']`)
- `NVIDIA_VISIBLE_DEVICES=4` 환경변수

**관련 파일**: `Dockerfile.dev`, `docker-compose.yml`

---

## 3. 파이프라인 오류 수정

**요청**: 파이프라인 실행 시 발생하는 오류들 수정

**변경사항**:
- `use_auth_token` → `token` 파라미터 변경 (pyannote 3.x 호환)
- `DiarizeOutput` 래퍼에서 `.speaker_diarization` 속성 추출
- `apply_pipeline`에서 오디오 타입 가드 추가 (두 번째 실행 시 오류 방지)

**관련 파일**: `gryannote/pipeline/backend/`, `demo/app.py`

---

## 4. RTTM 파일 처리 개선

### 4.1 인코딩 처리
**요청**: EUC-KR/CP949 인코딩 RTTM 파일 업로드 시 `UnicodeDecodeError` 수정

**변경사항**: `_ensure_utf8()` 함수로 자동 인코딩 감지 및 UTF-8 변환

### 4.2 URI 공백 오류
**요청**: RTTM 저장 시 URI 공백으로 인한 파싱 오류 수정

**변경사항**: `_write_rttm`에서 URI 공백을 언더스코어로 대체

### 4.3 URI 불일치 경고
**요청**: h11 프로토콜 오류 유발 및 대화창 닫히지 않는 문제 수정

**변경사항**: `gr.Warning()` → `warnings.warn()`, prefix 기반 비교로 변경

### 4.4 저장 기능
**요청**: 다운로드 화살표(↓)를 직관적인 것으로 교체하고 단축키 추가

**변경사항**: Save 버튼(SVG 아이콘 + "Save" 텍스트), `Ctrl+S` / `Cmd+S` 단축키

### 4.5 미리보기 성능
**요청**: RTTM 로딩 시 브라우저 "대기/벗어나기" 대화창 문제 해결

**변경사항**: 무한 fetch 반복 제거, 반응형 상태 기반 재작성, `cache: "no-store"`, 200줄 제한, 편집 시 실시간 갱신

**관련 파일**: `gryannote/rttm/backend/gryannote_rttm/rttm.py`, `gryannote/rttm/frontend/shared/FilePreview.svelte`

---

## 5. 선택 구간 재생

**요청**: 마킹된 영역만 재생하는 기능 추가

**변경사항**:
- `Shift + Space`: 선택 구간만 재생 (시작~끝점 도달 시 자동 정지)
- `playActiveRegion()` 함수 추가
- Play 버튼 UI 추가 (미선택 시 비활성화)

**관련 파일**: `gryannote/audio/frontend/player/RegionsControl.svelte`

---

## 6. 키보드 단축키 개선

### 6.1 Alt+Arrow 브라우저 충돌 방지
**요청**: `Alt+Left/Right`가 Chrome 브라우저 뒤로/앞으로 이동 대신 끝점 편집으로 동작하도록

**변경사항**: `e.altKey` 시 `e.preventDefault()` 추가

### 6.2 Arrow 키 구간 이동 수정
**요청**: Right 버튼이 웨이브폼 스크롤 대신 선택 구간의 시작점을 이동시켜야 함

**변경사항**: `activeRegion` 설정 시 `e.preventDefault()` 호출

**관련 파일**: `gryannote/audio/frontend/player/RegionsControl.svelte`

---

## 7. 웨이브폼 자동 스크롤

**요청**: 동영상의 타임정보를 쫓아오지 않는 문제 해결

**변경사항**: `autoScroll: true`, `autoCenter: true` 설정 추가

**관련 파일**: `gryannote/audio/frontend/Index.svelte`

---

## 8. 동영상 표시 및 동기화

### 8.1 크기 조정
**요청**: 동영상 크기가 너무 크다 → 1/8로 축소 → 너무 작으니 2배로

**변경사항**: `width: 100%` → `12.5%` → `25%`, 중앙 정렬

### 8.2 웨이브폼 동기화
**요청**: 웨이브폼 타임 슬롯에 맞게 동영상이 재생되어야 함

**변경사항**:
- AudioPlayer에서 Play 이벤트 전에 `timeupdate` dispatch (위치 동기화 선행)
- 탐색(seek) 시 `timeupdate` 이벤트로 `video.currentTime` 자동 동기화

**관련 파일**: `gryannote/audio/frontend/player/VideoPlayer.svelte`, `gryannote/audio/frontend/player/AudioPlayer.svelte`, `gryannote/audio/frontend/interactive/InteractiveAudioLabeling.svelte`

---

## 9. RTTM 미리보기 실시간 갱신

**요청**: 어노테이션 구간의 시작점/끝점을 화살표 키 또는 드래그로 편집할 때, RTTM 파일 미리보기가 실시간으로 갱신되어야 함

**변경사항**:
- URL/size 비교 기반 fetch 트리거를 version 기반으로 교체 (같은 URL에 내용이 변경되는 경우 감지)
- 150ms 디바운스로 빈번한 편집 시 과도한 fetch 방지
- `cache: "no-store"` 유지하여 브라우저 캐시 우회

**관련 파일**: `gryannote/rttm/frontend/shared/FilePreview.svelte`

---

## 10. Reset 버튼 좀비상태 수정

**요청**: 반시계 방향 원화살표(Reset) 버튼 클릭 시 UI가 먹통(좀비상태)이 되는 문제 수정

**원인 분석**:
- 글로벌 `click` 이벤트 리스너가 모드 활성 시 모든 클릭의 포커스를 강탈
- `document.getElementById()` null 참조로 TypeError 발생 가능
- `onDestroy`에서 글로벌 이벤트 리스너 미해제 → 컴포넌트 재생성 시 중복 핸들러 쌓임
- `$: waveform.on("ready")` reactive statement로 이벤트 중복 등록

**변경사항**:
- 글로벌 `keydown`/`click` 리스너를 named function으로 분리, `onDestroy`에서 해제
- `setMode()`와 글로벌 클릭 핸들러에 null 체크 추가
- `resetRegions()`에 `initialAnnotations` guard 및 `setMode("")` 호출 추가
- `waveformEventsInitialized` guard로 이벤트 중복 등록 방지

**관련 파일**: `gryannote/audio/frontend/player/RegionsControl.svelte`

---

## 키보드 단축키 요약

| 단축키 | 동작 |
|--------|------|
| `Space` | 재생/일시정지 |
| `Shift + Space` | 선택 구간만 재생 |
| `Enter` | 현재 위치에 어노테이션 생성 |
| `Shift + Enter` | 어노테이션 분할 |
| `A`, `B`, `C`, ... `Z` | 활성 레이블 설정 / 선택 구간 레이블 변경 |
| `Left` / `Right` | 선택 구간 시작점 편집 또는 타임커서 이동 |
| `Shift + Left/Right` | 빠른 이동 |
| `Alt + Left/Right` | 선택 구간 끝점 편집 |
| `Shift + Alt + Left/Right` | 끝점 빠른 편집 |
| `Tab` / `Shift + Tab` | 다음/이전 어노테이션 선택 |
| `Delete` | 선택 구간 삭제 후 다음 선택 |
| `Backspace` | 선택 구간 삭제 후 이전 선택 |
| `Escape` | 선택 해제 |
| `Up` / `Down` | 줌 인/아웃 |
| `Ctrl + S` | RTTM 파일 저장 |
| `F2` | 활성 레이블 설정 |
