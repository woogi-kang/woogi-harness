# CIP prompt ownership

이 파일에는 prompt template을 두지 않습니다.

CIP mockup의 생성형 prompt는 vendored `.claude/skills/image-prompt/SKILL.md`
가 단독으로 작성합니다. Deliverable, brand evidence, source logo, physical
context, output ratio를 compiler 입력으로 전달하고 Gongnyang C8 routing을
사용합니다. 이 reference에서 prompt를 보강하거나 다른 model 문법을
추가하지 않습니다.

실행 경로:

```text
CIP brief → image-prompt(C8) → validator → Codex $imagegen → gpt-image-2
```
