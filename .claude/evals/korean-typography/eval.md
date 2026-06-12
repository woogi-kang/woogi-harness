# Korean Typography Quality Eval

한국어 중심 결과물의 font, word breaking, wrapping, role consistency를 검증한다.

## 사용 방법

```bash
bash .claude/evals/korean-typography/grader.sh .claude/evals/korean-typography/cases/good-korean-landing.json /path/to/output.html
```

## 기대 품질

- 한국어 문맥에는 `word-break: keep-all`과 `overflow-wrap`가 있어야 한다.
- code/pre/terminal 문맥에는 별도 wrapping 및 monospace fallback이 있어야 한다.
- Pretendard, Nanum, Noto Sans KR, Apple SD Gothic Neo 등 한글 지원 font marker가 있어야 한다.
- 폰트 역할은 body/heading/code 중심으로 안정적이어야 한다.
