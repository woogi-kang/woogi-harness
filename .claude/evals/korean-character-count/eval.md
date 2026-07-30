# Korean Character Count Eval

결정론적 한국어 글자 수 계약이 Unicode 조합형 자모, emoji, 공백, 여러 줄바꿈, UTF-8 byte, NEIS 호환 byte에서 흔들리지 않는지 검사한다.

## 실행

```bash
node --test .claude/evals/korean-character-count/test_korean_character_count.js
```

## Hard gates

- `Intl.Segmenter` grapheme 수와 공백 제외 grapheme 수가 fixture와 일치한다.
- `CRLF`, `CR`, `LF`, `U+2028`, `U+2029`를 각각 한 번의 줄바꿈으로 처리한다.
- 기본 profile은 실제 UTF-8 byte를 반환한다.
- `neis` profile은 한글 grapheme 3B, ASCII 1B, 줄바꿈 2B 계약을 적용한다.
- `--text`, `--file`, `--stdin` 중 하나만 허용한다.
- CLI JSON 결과가 모듈 함수 결과와 일치한다.

제출처가 별도 계산 규칙을 제공하면 이 평가를 근거로 억지로 `default` 또는 `neis`에 맞추지 않는다. 새 profile과 fixture를 추가한다.
