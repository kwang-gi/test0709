"""
lilys-pattern-skill run.py

유튜브 스크립트를 입력받아 LilysAI 패턴(요약 4종 + 확장 리포트 + 추천질문 3개)으로
정리된 결과물을 output/ 폴더에 생성하기 위한 실행 스크립트.

이 스크립트는 실제 LLM 호출 로직은 포함하지 않는다 (환경마다 API가 다르므로).
대신 templates/ 폴더의 프롬프트들을 읽어서, 스크립트와 함께 정리된 "작업 지시서"를
만들어 Claude / Claude Code 등에게 전달하기 쉬운 형태로 준비해준다.

사용법:
    python run.py --input script.txt --outdir ./output
    python run.py --input script.txt --outdir ./output --frames video.mp4
"""

import argparse
import os
import glob


def load_templates(skill_dir):
    """templates 폴더의 모든 .md 프롬프트 파일을 읽어 dict로 반환"""
    templates = {}
    pattern = os.path.join(skill_dir, "templates", "*.md")
    for path in glob.glob(pattern):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            templates[name] = f.read()
    return templates


def build_job_list(templates, include_search=False):
    """실행할 작업 목록 구성. 기본 세트 + 옵션 세트"""
    base = ["summary_short", "summary_basic", "summary_long", "summary_easy",
            "ext_action_items", "ext_infographic", "ext_flashcard", "ext_quiz"]
    search_based = ["ext_background", "ext_counterview"]
    jobs = [t for t in base if t in templates]
    if include_search:
        jobs += [t for t in search_based if t in templates]
    return jobs


def extract_frames(video_path, out_dir, interval_sec=5):
    """
    (선택) 화면 전환 프레임 추출. ffmpeg 필요.
    스크립트에 없는, 화면에만 나오는 다이어그램을 캡처하기 위함.
    추출된 프레임은 이후 비전 모델에게 넘겨 텍스트 설명을 받는다.
    """
    os.makedirs(out_dir, exist_ok=True)
    cmd = (
        f'ffmpeg -i "{video_path}" -vf "select=\'gt(scene,0.4)\',showinfo" '
        f'-vsync vfr "{out_dir}/frame_%04d.png"'
    )
    print("[run.py] 프레임 추출 명령 (직접 실행 필요):")
    print("  " + cmd)
    return cmd


def generate_image_with_codex(prompt, out_path):
    """
    새 삽화가 필요할 때 Codex 이미지 2.0 스킬을 호출하는 자리.
    TODO: 사용자 PC에 설치된 실제 스킬 이름/명령으로 교체할 것.
    """
    print(f"[run.py] TODO: invoke_skill(\"codex-image-2.0\", prompt={prompt!r}, out={out_path!r})")


def main():
    parser = argparse.ArgumentParser(description="LilysAI 패턴 재현 스킬 실행기")
    parser.add_argument("--input", required=True, help="스크립트 텍스트 파일 경로")
    parser.add_argument("--outdir", default="./output", help="결과물 저장 폴더")
    parser.add_argument("--search", action="store_true", help="웹검색 기반 확장(배경지식/반대시각)도 포함")
    parser.add_argument("--frames", default=None, help="화면 그림 추출용 영상 파일 경로 (선택)")
    args = parser.parse_args()

    skill_dir = os.path.dirname(os.path.abspath(__file__))
    with open(args.input, "r", encoding="utf-8") as f:
        script_text = f.read()

    templates = load_templates(skill_dir)
    jobs = build_job_list(templates, include_search=args.search)

    os.makedirs(args.outdir, exist_ok=True)

    print(f"[run.py] 스크립트 길이: {len(script_text)}자")
    print(f"[run.py] 실행할 작업: {jobs}")
    print("[run.py] 각 작업의 프롬프트를 스크립트와 함께 LLM(Claude 등)에게 전달하세요.")

    # 작업 지시서를 하나의 파일로 정리 (사람이 Claude Code에 붙여넣기 쉽게)
    manifest_path = os.path.join(args.outdir, "_job_manifest.md")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("# LilysAI 패턴 실행 지시서\n\n")
        f.write("아래 각 작업의 프롬프트를 스크립트 전문과 함께 LLM에 전달해서, ")
        f.write("나온 결과를 파일명대로 저장하세요.\n\n")
        for job in jobs:
            f.write(f"## {job}\n")
            f.write(templates[job])
            f.write("\n\n---\n\n")
        f.write("## followup_questions\n")
        if "followup_questions" in templates:
            f.write(templates["followup_questions"])

    print(f"[run.py] 작업 지시서 생성 완료: {manifest_path}")

    if args.frames:
        frames_dir = os.path.join(args.outdir, "images")
        extract_frames(args.frames, frames_dir)


if __name__ == "__main__":
    main()
