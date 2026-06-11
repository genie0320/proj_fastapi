# =============================================================
#  Git Branch 전략 팀 가이드
#  Git Flow vs GitHub Flow — 우리 팀 선택과 운영 규칙
#  3인 협업 프로젝트 기준 | 2026년 6월
# =============================================================

def section_1_브랜치전략이란():
    """
    1. 브랜치 전략이란?
    ─────────────────────────────────────────────────────────
    여러 명의 개발자가 동시에 작업할 때, 서로의 코드에 영향을 주지
    않고 독립적으로 기능을 개발하고 안전하게 합치기 위한 브랜치 관리 규칙이다.

    팀이 코드베이스를 어떻게 '손 안대고 관리할 것인가'에 대한
    공식 입장 선언. 대표 전략: Git Flow vs GitHub Flow
    """
    pass


# =============================================================
#  2. Git Flow
# =============================================================

def section_2_git_flow():
    """
    빈센트 드라이센 제안 (2010년)
    복잡한 릴리즈 주기를 가진 프로젝트에 적합.
    5가지 브랜치를 역할에 따라 명확히 분리하여 운영한다.
    """
    pass


def section_2_1_git_flow_탄생배경():
    """
    2-1. 탄생 배경
    ─────────────────────────────────────────────────────────
    2010년 당시 스마트폰 앱이나 설치형 소프트웨어(CD, 패키지)처럼
    한 번 배포하면 되돌리기 어렵거나, 배포 주기가 몇 주~몇 달 단위로
    긴 제품이 주류였다.

    버전 관리(v1.0, v1.1 등)가 매우 중요했고, 출시 전에
    기획·QA·마케팅 일정을 맞춰 꼼꼼히 검증해야 했기에
    여러 브랜치를 촘촘하게 엮는 엄격한 구조가 필요했다.
    """
    pass


# 브랜치 구조 정의
GIT_FLOW_BRANCHES = {
    "main":         "실제 배포된 안정적인 코드",
    "develop":      "다음 버전을 위해 개발 중인 통합 브랜치",
    "feature/*":    "새로운 기능 개발 — develop에서 분기 후 복귀",
    "release/*":    "배포 전 최종 QA 및 버그 수정",
    "hotfix/*":     "운영 중 긴급 버그 수정 — main에서 직접 분기",
}

# 코드 흐름
GIT_FLOW_DIAGRAM = """
  main
   └── develop
         ├── feature/login       ← 기능 개발 (develop → feature → develop)
         ├── feature/signup      ← 기능 개발
         └── release/1.0.0       ← 배포 준비 (develop → release → main & develop)
                                    └── hotfix/bug  ← 긴급 수정 (main → hotfix → main & develop)
"""

GIT_FLOW_PROS = [
    "브랜치 역할이 명확하여 대규모 팀에서 관리가 용이",
    "릴리즈 버전 관리가 체계적 (v1.0, v2.0 태그 관리)",
    "인간 검증 프로세스가 촘촘하여 대형 배포 사고 방지",
]

GIT_FLOW_CONS = [
    "브랜치 수가 많아 복잡하고, 소규모 팀에는 오버엔지니어링이 될 수 있음",
    "장기 feature 브랜치가 쌓이면 '머지 지옥(Merge Hell)' 발생 위험",
    "배포 주기가 짧은 SaaS·웹 서비스 환경에는 구조가 너무 무거움",
]


# =============================================================
#  3. GitHub Flow
# =============================================================

def section_3_github_flow():
    """
    스콧 차콘 / GitHub 제안 (2011년)
    main 브랜치 하나를 중심으로 운영되는 단순하고 빠른 전략.
    상시 배포와 CI/CD가 잘 구축된 웹 서비스에 적합.
    """
    pass


def section_3_1_github_flow_탄생배경():
    """
    3-1. 탄생 배경
    ─────────────────────────────────────────────────────────
    GitHub은 전 세계 개발자가 매 초 코드를 수정·공유하는 SaaS 회사다.
    웹 서비스는 코드를 서버에 반영하는 즉시 사용자가 최신 버전을 쓰게 되므로,
    복잡한 릴리즈 절차보다 '기능 하나 완성하면 즉시 배포'하는 속도가 생명이었다.

    핵심 철학: "Fail Fast, Fix Fast" — 망가지면 바로 고쳐서 다시 밀어 넣는다.
    """
    pass


# 브랜치 구조 정의
GITHUB_FLOW_BRANCHES = {
    "main":       "항상 배포 가능한 상태를 유지하는 유일한 핵심 브랜치",
    "feature/*":  "기능 개발 또는 버그 수정 후 main에 PR로 병합. 이름이 명확해야 함",
}

# 코드 흐름
GITHUB_FLOW_STEPS = [
    "1. main에서 feature 브랜치 분기",
    "2. 기능 개발 후 커밋 & 푸시",
    "3. Pull Request(PR) 생성",
    "4. 팀원 코드 리뷰 (1인 이상 Approve 필수)",
    "5. main에 Merge",
    "6. 즉시 배포 (git pull or 자동 CD)",
]

GITHUB_FLOW_DIAGRAM = """
  main ──────────────────────────────────────► (항상 배포 가능)
         └── feature/user-api ──► PR ──► Merge
"""

GITHUB_FLOW_PROS = [
    "구조가 단순하여 소규모 팀이나 빠른 배포 환경에 최적",
    "PR 기반 코드 리뷰가 자연스럽게 이루어짐",
    "병목이 없어 비즈니스 피드백 속도가 극대화",
]

GITHUB_FLOW_CONS = [
    "자동화 테스트 커버리지가 낮으면 결함 코드가 main에 바로 반영될 위험",
    "릴리즈 버전 관리가 명확하지 않아 대규모 프로젝트 관리에 한계",
]


# =============================================================
#  4. Git Flow vs GitHub Flow 비교표
# =============================================================

COMPARISON_TABLE = [
    # (비교 항목, Git Flow, GitHub Flow)
    ("브랜치 수",      "5개 (main, develop, feature, release, hotfix)", "2개 (main, feature/*)"),
    ("복잡도",         "높음",                                           "낮음"),
    ("배포 주기",      "정기 릴리즈 (주간·월간)",                        "상시 배포 (하루 수회)"),
    ("적합한 팀",      "중·대규모",                                      "소규모 (3인 이하)"),
    ("CI/CD 친화성",   "보통",                                           "높음"),
    ("출신 배경",      "패키지·설치형 소프트웨어 (2010)",                 "SaaS·웹 서비스 (2011)"),
    ("핵심 철학",      "완벽히 검증된 버전을 정기 출시",                  "기능 완성 즉시 빠르게 배포"),
]


# =============================================================
#  5. 우리 팀의 선택: GitHub Flow
# =============================================================

TEAM_CHOICE = "GitHub Flow"

TEAM_CHOICE_REASON = """
팀원 3명의 소규모 협업 프로젝트이며, 빠른 피드백과 수시 업데이트가 핵심입니다.
Git Flow를 도입하면 코드 짜는 시간보다 브랜치 옮기고 머지 꼬인 것 푸는 데
더 많은 시간이 소요됩니다.
통제 비용이 개발 비용을 초과하지 않도록 GitHub Flow의 단순함을 선택합니다.
"""

# 의사결정 매트릭스
DECISION_MATRIX = [
    # (기준, Git Flow 채택, GitHub Flow 채택)
    ("배포 주기",    "정기 배포 (주 1회 이상)",              "상시 배포 가능"),
    ("인프라 환경",  "개발계·검증계·운영계 분리",             "컨테이너 기반 동적 환경"),
    ("자동화 수준",  "CI/CD 없거나 불완전",                  "CI/CD 파이프라인 + 높은 테스트 커버리지"),
    ("팀 규모/역량", "중·대규모, QA·기획·개발 역할 분리",    "소규모 정예, DevOps 지향"),
]


# =============================================================
#  6. 브랜치 네이밍 규칙
# =============================================================

BRANCH_NAMING_RULES = {
    "feature/{기능명}":   "새로운 기능 개발          ex) feature/user-api",
    "hotfix/{내용}":      "긴급 버그 수정            ex) hotfix/login-error",
    "docs/{문서명}":      "문서 작성 및 수정          ex) docs/team-rules",
    "refactor/{내용}":    "코드 리팩토링             ex) refactor/auth-module",
}


# =============================================================
#  7. 커밋 메시지 규칙
#  형식: {타입}: {내용}
#  타입은 영문 소문자, 내용은 한국어 또는 영문 가능
# =============================================================

COMMIT_TYPES = {
    "feat":     ("새로운 기능 추가",        "feat: 로그인 기능 구현"),
    "fix":      ("버그 수정",               "fix: 토큰 만료 오류 수정"),
    "docs":     ("문서 작성·수정",          "docs: README 업데이트"),
    "refactor": ("코드 리팩토링",           "refactor: auth 모듈 분리"),
    "chore":    ("기타 설정 변경",          "chore: .gitignore 추가"),
    "test":     ("테스트 코드 추가·수정",   "test: 로그인 유닛 테스트 추가"),
}


# =============================================================
#  8. CI/CD 없는 팀을 위한 수동 파이프라인
# =============================================================

MANUAL_PIPELINE = """
  [작업자] 브랜치 생성 및 기능 개발
     ⬇
  [수동 검증] 로컬 PC에서 빌드 및 정상 작동 최종 확인 (필수)
     ⬇
  [GitHub] main 브랜치로 Pull Request(PR) 생성
     ⬇
  [동료 리뷰] 협력자 1인 이상 코드 리뷰 후 Approve
     ⬇
  [소유자 병합] 최종 확인 후 main에 Merge
     ⬇
  [수동 배포] main 코드를 서버에 반영 (git pull 등)
"""

PR_CHECKLIST = [
    "로컬 환경에서 에러 없이 정상 빌드·구동 확인",
    "이번 수정으로 영향받는 다른 기능 명시 (없으면 '없음')",
    "DB 스키마 변경 여부 명시",
    "환경 변수(.env) 하드코딩 없음 확인",
]

GITHUB_ACTIONS_STEPS = [
    "GitHub 리포지토리 상단 Actions 탭 진입",
    "프로젝트 언어(Python, Node.js 등)에 맞는 기본 템플릿 선택",
    "Configure 버튼 클릭 후 저장 — PR 생성 시 자동으로 빌드 검사 실행",
]

SAFETY_TIP = (
    "main 브랜치 설정 → Branch protection rules에서 "
    "'Require a pull request before merging'을 반드시 활성화할 것. "
    "이것 하나만으로도 직접 push를 막고 최소한의 코드 리뷰를 강제할 수 있다."
)


# =============================================================
#  9. 결론 및 요약
# =============================================================

CONCLUSION = """
두 전략의 차이는 결국
'변경 사항을 검증하고 상용 환경에 전달하는 신뢰도 모델(Trust Model)을
어떻게 설계했는가'의 차이다.

- Git Flow    : 인간의 실수를 여러 겹의 브랜치(develop, release)로 방어.
                안전하지만 머지 지옥이 SPOF.

- GitHub Flow : 단계를 없애고 자동화(CI/CD)와 PR 코드 리뷰에 집중.
                빠르지만 자동화 테스트가 부실하면 main이 쉽게 무너짐.

[ 우리 팀의 최적해 ]
GitHub Flow의 단순함을 가져가되, CI/CD가 없는 현 상황에서는
'동료 1인 이상 Approve 후 머지'라는 인간적 통제 장치(Harness)를 규칙으로 운영한다.
인프라 공사에 리소스를 빼앗기기보다 비즈니스 로직과 제품 자체에 집중하는 것이
현 단계에서 가장 현명한 전략이다.
"""


# =============================================================
#  실행 시 전체 가이드 출력
# =============================================================

def print_guide():
    SEP = "=" * 60

    print(SEP)
    print("  Git Branch 전략 팀 가이드")
    print("  Git Flow vs GitHub Flow | 3인 협업 프로젝트")
    print(SEP)

    print("\n[ 2. Git Flow 브랜치 구조 ]")
    for branch, desc in GIT_FLOW_BRANCHES.items():
        print(f"  {branch:<18} : {desc}")

    print("\n[ Git Flow 흐름 ]")
    print(GIT_FLOW_DIAGRAM)

    print("  장점:")
    for p in GIT_FLOW_PROS:
        print(f"    ✔ {p}")
    print("  단점:")
    for c in GIT_FLOW_CONS:
        print(f"    ✘ {c}")

    print(f"\n{SEP}")
    print("\n[ 3. GitHub Flow 브랜치 구조 ]")
    for branch, desc in GITHUB_FLOW_BRANCHES.items():
        print(f"  {branch:<18} : {desc}")

    print("\n[ GitHub Flow 흐름 ]")
    for step in GITHUB_FLOW_STEPS:
        print(f"  {step}")
    print(GITHUB_FLOW_DIAGRAM)

    print("  장점:")
    for p in GITHUB_FLOW_PROS:
        print(f"    ✔ {p}")
    print("  단점:")
    for c in GITHUB_FLOW_CONS:
        print(f"    ✘ {c}")

    print(f"\n{SEP}")
    print("\n[ 4. 비교표 ]")
    print(f"  {'항목':<16} {'Git Flow':<38} {'GitHub Flow'}")
    print("  " + "-" * 80)
    for item, git, github in COMPARISON_TABLE:
        print(f"  {item:<16} {git:<38} {github}")

    print(f"\n{SEP}")
    print(f"\n[ 5. 우리 팀 선택: {TEAM_CHOICE} ]")
    print(TEAM_CHOICE_REASON)

    print("  의사결정 매트릭스:")
    for criteria, git, github in DECISION_MATRIX:
        print(f"  {criteria:<14} | Git Flow: {git}")
        print(f"  {'':14} | GitHub Flow: {github}")

    print(f"\n{SEP}")
    print("\n[ 6. 브랜치 네이밍 규칙 ]")
    for pattern, desc in BRANCH_NAMING_RULES.items():
        print(f"  {pattern:<26} → {desc}")

    print(f"\n{SEP}")
    print("\n[ 7. 커밋 메시지 규칙 ]  형식: 타입: 내용")
    for type_, (desc, example) in COMMIT_TYPES.items():
        print(f"  {type_:<12} | {desc:<20} | ex) {example}")

    print(f"\n{SEP}")
    print("\n[ 8. 수동 파이프라인 ]")
    print(MANUAL_PIPELINE)
    print("  PR 체크리스트:")
    for item in PR_CHECKLIST:
        print(f"    [ ] {item}")
    print(f"\n  💡 핵심 안전장치: {SAFETY_TIP}")

    print(f"\n{SEP}")
    print("\n[ 9. 결론 ]")
    print(CONCLUSION)
    print(SEP)


if __name__ == "__main__":
    print_guide()
