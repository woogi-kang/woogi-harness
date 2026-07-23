# Remotion Product UI Promotion Eval

제품 UI 영상이 실제 제품 출처와 분리된 합성 계약을 유지하는지 검사한다.

## 검증 항목

- 레퍼런스가 있으면 shot timing을 기록하고, 없으면 `not_provided`를 정직하게 기록한다.
- 캡처 출처는 Playwright 실앱, 제품 컴포넌트 fixture, 제품 golden renderer 중 하나다.
- viewport, DPR, locale, timezone, clock, readiness와 프레임 hash가 있다.
- 모든 scene은 `preset + durationInFrames + params + transition + camera`를 가진다.
- scene duration 합이 composition duration과 일치한다.

## 실행

```bash
bash .claude/evals/remotion-product-ui-promo/grader.sh
```

`cases/invalid`, `cases/malformed`, `cases/traversal`은 각각 계약 위반,
비객체 JSON 오염, project-root 탈출을 재현하며 모두 실패해야 한다.
