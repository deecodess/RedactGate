# Context Classifier Prompt v1

Classify only the provided candidate windows. Do not infer from text outside the window.

Return structured JSON:

```json
{
  "items": [
    {
      "span": "candidate span text",
      "type": "PERSON_NAME",
      "sensitive": true,
      "confidence": 0.96,
      "reason": "Appears after an explicit customer label."
    }
  ]
}
```

Allowed types:

- `PERSON_NAME`
- `ADDRESS`
- `IDENTIFIER`

Use `sensitive=false` when the span is clearly benign technical context.

