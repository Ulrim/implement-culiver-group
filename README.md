# 컬리버 그룹 · CULIVER GROUP

바다에서 농장까지, 순환하는 내일을 기릅니다 — 컬리버 그룹 코퍼레이트 홈페이지.

Claude Design 익스포트(`culiver-group-main.dc.html`)를 실제로 동작하는 정적 웹사이트로 구현한 것입니다. 스마트 양식(컬리버), 수처리(에이엠피), 자원순환 소재(코발티브), 스마트팜·유통(수신제팜) 네 계열사를 하나의 순환 구조로 소개하는 한국어/영어 이중 언어 원페이지 사이트입니다.

## 실행 방법

빌드 과정이 없는 순수 정적 사이트입니다. 로컬에서 보려면 아무 정적 서버나 사용하면 됩니다:

```bash
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```

`index.html`을 파일로 직접 열어도 대부분 동작하지만, 폰트 CDN 및 이미지 경로 안정성을 위해 로컬 서버 사용을 권장합니다.

## 구성

```
index.html              메인 원페이지 (13개 섹션)
culiver-aqua.html       컬리버   — 계열사 소개 (준비 중 플레이스홀더)
amp.html                에이엠피 — 계열사 소개 (준비 중 플레이스홀더)
cobaltive.html          코발티브 — 계열사 소개 (준비 중 플레이스홀더)
susinje-farm.html       수신제팜 — 계열사 소개 (준비 중 플레이스홀더)
assets/
  css/style.css         전체 스타일 (디자인의 인라인 스타일을 시맨틱 클래스로 정리)
  js/main.js            데이터 + 인터랙션 (원본 Claude Design 컴포넌트 로직 이식)
  img/                  히어로 · 사업 카드 · 뉴스 이미지 (11장, 디자인 번들에서 추출)
```

## 섹션

내비게이션(GNB) · 모바일 메뉴 · 히어로 · 통계 · 사업영역(Business) · 순환구조(The Loop) · 그룹소개(About) · 연혁(History) · 지속가능경영(ESG) · 뉴스룸(Newsroom) · 채용(Careers) · 문의(Contact) · 푸터.

## 인터랙션

- **언어 토글 (KO/EN)** — `data-lang` 속성으로 한/영 전환
- **스크롤 진행 바 + 활성 내비게이션 하이라이트**
- **숫자 카운터** — 통계 섹션이 화면에 들어오면 애니메이션
- **스크롤 리빌** — IntersectionObserver 기반 페이드인
- **순환구조(The Loop)** — 노드 클릭/호버로 각 사업의 역할 전환
- **연혁 타임라인** — 연도 버튼으로 상세 내용 전환
- **뉴스룸 필터** — 전체/보도자료/소식/채용 카테고리 필터
- **문의 폼** — 제출 시 접수 확인 화면 (프런트엔드 데모, 실제 전송 로직은 미연결)
- **모바일 햄버거 메뉴 · 맨 위로 버튼**

## 기술

- 순수 HTML / CSS / Vanilla JavaScript (프레임워크·빌드 도구 없음)
- **콘텐츠는 HTML에 정적으로 포함** — JS는 인터랙션만 담당하므로 JS가 없어도 전체 내용이 보이고 검색엔진에 노출됩니다(점진적 향상)
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

## 교체가 필요한 플레이스홀더

디자인에 포함된 예시 정보이므로 실제 정보로 교체하세요:

- 연락처: `contact@culiver.co.kr`, `000-0000-0000`
- 주소 / 사업자 정보 (Contact · Footer 섹션)
- 4개 계열사 상세 페이지 (현재 "준비 중" 플레이스홀더)
- 뉴스·채용 항목은 예시 데이터입니다 (`assets/js/main.js`의 `news`, `roles` 배열)
