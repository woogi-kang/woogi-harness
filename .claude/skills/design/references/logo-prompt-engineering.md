# Logo prompt ownership

이 파일에는 prompt template을 두지 않습니다.

Logo/brand mark/app icon의 생성형 prompt는 vendored
`.claude/skills/image-prompt/SKILL.md`가 단독으로 작성합니다. Logo discovery
결과는 brand name, audience, visual evidence, palette, required copy 형태로
compiler에 전달합니다. 이 reference에서 suffix, negative prompt, style keyword,
model별 문법을 추가하지 않습니다.

실행 경로:

```text
logo brief → image-prompt(C8/C9) → validator → Codex $imagegen → gpt-image-2
```
