---
name: lilys-pattern
description: 유튜브 스크립트(또는 자막)를 입력받아 LilysAI 스타일로 요약 4종 + 확장 리포트 N종 + 추천질문 3개를 생성한다. 유튜브/영상 정리, 강의 요약, 스크립트 정리 요청 시 사용.
---

# LilysAI 패턴 재현 스킬

## 목적
LilysAI가 유튜브를 요약/확장하는 방식을 그대로 재현한다. 릴리에 접속하지 않고
스크립트 하나만으로 동일한 정리물(요약 4종, 확장 리포트, 추천질문)을 만든다.

## 핵심 원리 (관찰로 역설계함)
릴리의 모든 산출물은 내부적으로 다음 구조다.

    [스크립트 전문] + [해당 템플릿의 고정 프롬프트]  ->  LLM  ->  포맷된 결과물

- 릴리의 "나만의 템플릿 만들기"는 입력이 딱 2개(이름, 프롬프트)뿐이다.
- 즉 요약/확장은 전부 "프롬프트 한 벌"로 정의된다. 이 스킬은 그 프롬프트들을 templates 폴더에 담았다.

## 입력
- script : 유튜브 스크립트/자막 전문 (타임스탬프 있으면 더 좋음)
- (선택) video_url : 화면 그림 추출이 필요할 때

## 절차
1. 스크립트를 읽고 전체 맥락을 파악한다.
2. 요약 4종을 생성한다. 각각 summary_short / basic / long / easy 규칙을 따른다.
   - 4종은 정보량이 아니라 압축률과 말투만 다르다. 모두 스크립트 안에서만 생성.
   - 각 문장 끝에 근거 타임스탬프를 [mm:ss] 로 표기한다. (릴리의 [숫자] 인용과 동일 역할)
3. 확장 리포트를 요청받은 만큼 생성한다. (templates 폴더의 ext_ 파일 참고)
   - 기본 세트: 액션아이템, 인포그래픽(구조 텍스트), 플래시카드, 퀴즈
   - 추가 세트: 관련 배경지식, 반대 시각 조사 (웹검색 필요)
   - 커스텀: ext_custom 을 복제해 프롬프트만 교체
4. 매 산출물 끝에 추천질문 3개를 붙인다. (followup_questions 규칙)
5. (선택) 화면 그림 처리: 아래 화면 그림 섹션 참고.
6. 결과를 output 폴더에 마크다운으로 저장한다. (run.py 사용 시 자동)

## 검색(웹) 규칙 - 중요
- 스크립트 안에서 답할 수 있으면 절대 검색하지 않는다.
- 스크립트에 없는 새 외부 개념/고유명사가 처음 등장할 때만 웹검색 1회 수행.
- 그 뒤 후속 질문은 이미 확보한 자료 + 스크립트로 답한다.
- 웹검색은 관련 배경지식 / 반대 시각 조사 템플릿에서만 켠다.

## 화면 그림 (자막에 없고 화면에만 나오는 다이어그램)
- 텍스트 스크립트만으로는 복원 불가.
- run.py 가 장면 전환 프레임을 추출한 뒤 비전 모델로 화면 다이어그램을 텍스트로 설명시킨다.
- 새 삽화가 필요하면 Codex 이미지 2.0 스킬을 호출한다.

  <!-- Codex 이미지 2.0 스킬 호출부: 사용자가 나중에 직접 수정 -->
      # TODO: PC에 설치된 실제 스킬 이름/명령으로 교체할 것
      invoke_skill("codex-image-2.0", prompt="그릴 그림 설명", out="output/images/xxx.png")
  <!-- 여기까지 -->

## 출력 폴더 구조
    output/
      summary_short.md
      summary_basic.md
      summary_long.md
      summary_easy.md
      ext_각종.md
      followup.md
      images/   (화면 그림 처리 시)

## 템플릿 목록 (templates 폴더)
- summary_short.md / summary_basic.md / summary_long.md / summary_easy.md
- ext_action_items.md / ext_infographic.md / ext_flashcard.md / ext_quiz.md
- ext_background.md / ext_counterview.md (웹검색)
- ext_custom.md (커스텀)
- followup_questions.md
