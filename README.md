# 컬리버 그룹 · CULIVER GROUP

바다에서 농장까지, 순환하는 내일을 기릅니다 — 컬리버 그룹 코퍼레이트 홈페이지.

Claude Design 익스포트(`culiver-group-main.dc.html`)에서 출발해, 홈 화면 하나짜리 랜딩페이지가 아니라 그룹소개·계열사 4곳·지속가능경영·뉴스룸·채용·문의로 이어지는 21개 페이지의 실제 코퍼레이트 사이트로 구현했습니다. 스마트 양식(컬리버), 수처리(에이엠피), 자원순환 소재(코발티브), 스마트팜·유통(수신제팜) 네 계열사를 하나의 순환 구조로 소개하는 한국어/영어 이중 언어 사이트입니다.

## 실행 방법

대부분의 페이지는 빌드 과정이 없는 정적 사이트입니다. 로컬에서 보려면 아무 정적 서버나 사용하면 됩니다:

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```

정적 페이지는 이걸로 충분합니다. 단, 뉴스룸(관리자 CRUD 포함)은 서버리스 API가 필요하므로 `/admin.html` 및 실시간 게시/삭제까지 로컬에서 확인하려면 `vercel dev`를 쓰세요 (아래 "뉴스룸 관리자" 절 참고). 페이지 문구(HTML)는 직접 수정하지 말고 `tools/build_pages.py`를 고친 뒤 `python3 tools/build_pages.py`로 다시 생성하세요 — 모든 페이지가 이 스크립트 하나에서 나옵니다.

## 구성

```
tools/build_pages.py    21개 정적 페이지를 생성하는 빌더 (헤더·푸터·계열사·채용공고 등 모든 콘텐츠의 단일 소스)
index.html               메인 홈
about.html                그룹소개 (비전·연혁·조직·CI)
business.html             사업영역 (4개 계열사 한눈에)
sustainability.html       지속가능경영 (ESG)
newsroom.html             뉴스룸 목록 (동적, /api/news에서 실시간 로드)
news.html                 뉴스 상세 템플릿 (?id=로 기사 지정, 동적)
news-1.html ~ news-6.html  구 URL 호환용 리다이렉트 스텁 → news.html?id=news-N
careers.html               채용 홈 + careers-{culiver,amp,cobaltive,susinje}.html 4개 상세
contact.html               문의 (Vercel 서버리스로 이메일 발송)
culiver-aqua.html / amp.html / cobaltive.html / susinje-farm.html   계열사 상세 4개
admin.html                뉴스룸 관리자 (로그인 + 게시/수정/삭제, robots: noindex)
assets/
  css/style.css           공개 사이트 전체 스타일
  css/admin.css           관리자 페이지 전용 스타일
  js/main.js              공개 사이트 데이터 + 인터랙션 + 뉴스 API 연동
  js/admin.js             관리자 대시보드 로직
  img/                    히어로 · 사업 카드 · 뉴스 이미지
api/
  contact.js              문의 폼 → Resend 이메일 발송
  news/index.js, news/[id].js   뉴스 CRUD API
  admin/login.js, logout.js, me.js   관리자 세션 인증
  _lib/kv.js, auth.js, news-store.js  공용 저장소·인증·데이터 모듈
```

## 인터랙션

- **언어 토글 (KO/EN)** — `data-lang` 속성으로 한/영 전환, `localStorage`로 유지
- **스크롤 진행 바 · 스크롤 리빌(IntersectionObserver)**
- **숫자 카운터** — 통계 섹션 진입 시 애니메이션
- **순환구조(The Loop)** — 노드 클릭/호버로 각 사업의 역할 전환
- **연혁 타임라인** — 연도 버튼으로 상세 내용 전환
- **뉴스룸** — `/api/news`에서 실시간 로드, 전체/보도자료/소식/채용 필터, 상세 페이지 이전글/다음글 페이저
- **문의 폼** — 실제 이메일 발송 (Resend), 언어별 placeholder·채용 지원 자동 프리필
- **관리자 대시보드** — 로그인 후 뉴스 작성/수정/삭제/게시·임시저장 전환
- **모바일 햄버거 메뉴 · 맨 위로 버튼**

## 기술

- 정적 페이지는 순수 HTML / CSS / Vanilla JavaScript (프레임워크·빌드 도구 없음), `tools/build_pages.py`(파이썬)로 생성
- 뉴스룸만 예외적으로 동적입니다 — Vercel 서버리스 함수 + KV(Redis 호환) 저장소로 관리자 CRUD를 지원하며, 자세한 내용과 절충점은 "뉴스룸 관리자" 절 참고
- **정적 페이지는 콘텐츠가 HTML에 그대로 포함** — JS 없이도 보이고 검색엔진에 노출됩니다(점진적 향상). 뉴스룸/뉴스 상세만 JS로 최신 데이터를 불러오며, 이 페이지들의 JS 미지원 폴백은 최초 배포 시점의 예시 6개 기사로 제한됩니다
- 폰트: Pretendard Variable, Noto Serif KR (CDN)
- 반응형 (모바일 ~ 데스크톱), `prefers-reduced-motion` 대응

## 배포 (Vercel)

Vercel로 배포합니다. 정적 사이트라 빌드 단계가 없으며 `vercel.json`으로 자산 캐시 헤더만 지정합니다. 비공개 레포도 Vercel 무료(Hobby) 티어에서 배포됩니다.

**최초 1회 설정**
1. [vercel.com](https://vercel.com)에 GitHub 계정으로 로그인
2. **Add New… → Project → `Ulrim/implement-culiver-group` Import**
3. Framework Preset은 **Other**(자동 감지), Build/Output 설정은 비워 둠 → **Deploy**

이후에는 `main` 브랜치에 푸시될 때마다 Vercel이 자동으로 재배포합니다(프리뷰 배포는 다른 브랜치·PR에도 생성).

## 문의 폼 (동적)

문의 폼은 Vercel 서버리스 함수 `api/contact.js`가 처리하며, [Resend](https://resend.com)로 이메일을 발송합니다. 별도 프레임워크 없이 정적 사이트 + 함수 하나로 동작합니다.

**설정 (Vercel → Project → Settings → Environment Variables)**

| 변수 | 필수 | 설명 |
|------|------|------|
| `RESEND_API_KEY` | ✅ | Resend 대시보드에서 발급한 API 키 (`re_...`) |
| `CONTACT_TO_EMAIL` | ✅ | 문의를 수신할 이메일 주소 |
| `CONTACT_FROM_EMAIL` | 선택 | 발신 주소. 도메인 인증 필요. 미설정 시 테스트용 `onboarding@resend.dev` 사용 |

1. [resend.com](https://resend.com) 가입 → API Key 생성 → `RESEND_API_KEY`에 입력
2. 수신 주소를 `CONTACT_TO_EMAIL`에 입력
3. (권장) 회사 도메인을 Resend에 인증한 뒤 `CONTACT_FROM_EMAIL`을 `CULIVER GROUP <noreply@culiver.co.kr>` 형식으로 설정
4. 환경 변수 저장 후 재배포

**동작 / 보안**
- 프런트엔드는 `/api/contact`로 JSON POST → 성공 시 접수 화면, 실패 시 오류 메시지 표시
- 허니팟(`_gotcha`) 필드로 기본 봇 차단, 서버에서 입력 길이 제한·검증
- 키가 없으면 함수가 안전하게 오류를 반환(메일은 발송되지 않음)

> 스팸이 많아지면 rate limiting(예: Vercel KV/Upstash)이나 캡차(Turnstile) 추가를 권장합니다.

## 뉴스룸 관리자 (동적, DB 연동)

뉴스룸은 더 이상 빌드 시점 정적 데이터가 아닙니다. `admin.html`에서 로그인해 기사를 작성·수정·삭제·게시/임시저장할 수 있고, 변경 사항은 `newsroom.html` · 홈 화면 미리보기 · 기사 상세 페이지(`news.html?id=...`)에 즉시 반영됩니다.

**구성**
- `admin.html` + `assets/js/admin.js` — 로그인 및 CRUD 대시보드 (내부 도구용 페이지, `robots: noindex`)
- `api/news/*`, `api/admin/*` — 서버리스 API (외부 npm 패키지 없이 Vercel KV REST API를 `fetch`로 직접 호출)
- `api/_lib/news-store.js` — 기사 스키마·검증·시드 데이터(최초 배포 시 자동으로 6개 예시 기사로 채워짐)
- `assets/js/main.js`의 `setupNews()` / `setupArticle()` — 공개 페이지에서 `/api/news`를 호출해 목록·상세를 그려냄. **JS가 없는 환경에서는** 빌드 시점에 박제된 예시 6개 기사만 보이는 정적 폴백으로 동작합니다(관리자가 이후에 수정·삭제·추가한 내용은 반영되지 않음 — 동적 CMS와 무빌드 정적 폴백을 동시에 만족시키는 절충입니다).

**설정 (필수 — 이 단계 없이는 관리자 페이지가 동작하지 않습니다)**

1. **Vercel → Project → Storage → Create Database**에서 KV(Redis 호환) 스토어를 만들고 **Connect to Project**로 연결하세요. 연결하면 `KV_REST_API_URL`, `KV_REST_API_TOKEN` 환경 변수가 프로젝트에 자동으로 추가됩니다. (Vercel의 스토리지 메뉴 구성은 종종 바뀌므로, "KV"라는 이름이 안 보이면 Upstash for Redis 등 Redis 호환 Marketplace 통합을 사용해도 됩니다 — 이 프로젝트는 `KV_REST_API_URL`/`KV_REST_API_TOKEN`이라는 이름의 REST 엔드포인트/토큰만 있으면 됩니다.)
2. **Settings → Environment Variables**에 아래 두 값을 추가하세요:

   | 변수 | 필수 | 설명 |
   |------|------|------|
   | `ADMIN_PASSWORD` | ✅ | `/admin.html` 로그인 비밀번호 (관리자 1명 기준 — 다중 계정 없음) |
   | `ADMIN_SESSION_SECRET` | ✅ | 로그인 세션 서명용 무작위 문자열. 터미널에서 `openssl rand -hex 32`로 생성해 붙여넣으세요 |

3. 저장 후 재배포 → `/admin.html`에서 비밀번호로 로그인.

**로컬 테스트**

KV 환경 변수 없이 로컬에서 실행하면(`vercel dev`) 메모리 저장소로 자동 대체되어 관리자 UI를 바로 테스트할 수 있습니다 — 단, 서버가 재시작되면 초기화되므로 실제 운영에는 반드시 위 1단계로 KV를 연결해야 합니다.

## 페이지별 문구 변경 시트

개발자가 아니어도 사이트 문구를 검토·수정할 수 있도록, 모든 페이지의 한글/영문 문구를 페이지별 탭으로 정리한 엑셀 파일을 제공합니다: **`content/copy-editing-sheet.xlsx`**.

- 탭 구성: `안내`(사용법) · `공통(헤더·푸터·메뉴)` · 나머지 16개는 페이지별 탭
- 각 행: 원문(한글/영문) + 비워 둔 "새 문구" 칸 — 바꾸고 싶은 행만 채우면 됨
- 뉴스룸 기사는 이 표가 아니라 `/admin.html`에서 직접 관리합니다 (위 절 참고)

**재생성 방법** (내용을 실제로 바꾼 뒤 시트를 새로 뽑고 싶을 때):

```bash
pip install -r tools/requirements-dev.txt   # 최초 1회 (beautifulsoup4, openpyxl)
python3 tools/build_pages.py                # HTML을 먼저 최신 상태로
python3 tools/generate_copy_sheet.py        # content/copy-editing-sheet.xlsx 갱신
```

이 스크립트는 이미 만들어진 HTML에서 문구를 뽑아내기만 합니다 — 채워진 시트를 다시 사이트에 반영하려면 `tools/build_pages.py`의 해당 문자열을 직접 고친 뒤 다시 빌드해야 합니다(자동 반영 기능은 아직 없음).

## 교체가 필요한 플레이스홀더

디자인에 포함된 예시 정보이므로 실제 정보로 교체하세요:

- 연락처: `contact@culiver.co.kr`, `000-0000-0000`
- 주소 / 사업자 정보 (Contact · Footer 섹션)
- 4개 계열사 상세 페이지 (현재 "준비 중" 플레이스홀더)
- 채용 공고는 예시 데이터입니다 (`tools/build_pages.py`의 `ROLES` 배열 — 빌드 시점 정적 콘텐츠)
- 뉴스룸 시드 기사 6건은 `/admin.html`에서 바로 수정·삭제하거나 새 기사로 교체하세요 (위 "뉴스룸 관리자" 절 참고)
