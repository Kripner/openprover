# Bug: `labs-leanstral-2603` tool calling breaks with longer instructions

## Summary

Tool calling with `labs-leanstral-2603` on `/v1/conversations` silently stops working when the `instructions` field exceeds roughly 15 tokens. The model ignores both the tools and the user message, producing generic greetings instead.

Additionally, even with short instructions, tool calling is intermittent — it works reliably for extended periods, then stops working entirely for equally long periods, without any change in input.

## Minimal reproduction

Tool: `add(a: number, b: number)` — "Add two numbers."

User message: `"Call the add tool with a=2 and b=3."`

```python
import json, urllib.request

payload = {
    "model": "labs-leanstral-2603",
    "inputs": [{"role": "user", "content": "Call the add tool with a=2 and b=3."}],
    "instructions": "You have an add tool. Use it.",  # ← short: works
    # "instructions": "You are a helpful math assistant. Always use the add tool for arithmetic.",  # ← long: breaks
    "tools": [{
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        },
    }],
    "stream": False,
    "completion_args": {
        "temperature": 1.0, "max_tokens": 4096, "top_p": 1, "reasoning_effort": "high",
    },
}

req = urllib.request.Request(
    "https://api.mistral.ai/v1/conversations",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Bearer <KEY>"},
)
raw = json.loads(urllib.request.urlopen(req, timeout=120).read())
print(json.dumps(raw, indent=2))
```

Full repro script: [`repro_leanstral_tools.py`](./repro_leanstral_tools.py)

## Observed behavior

### Short instructions → tool call (when the API is in a working state)

With `instructions: "You have an add tool. Use it."` (29 chars), the response correctly contains a `function.call` entry:

```json
{
  "outputs": [
    {
      "type": "message.output",
      "role": "assistant",
      "content": [{"type": "thinking", "thinking": [{"type": "text", "text": "The user wants me to call the add tool with a=2 and b=3."}]}]
    },
    {
      "type": "function.call",
      "name": "add",
      "arguments": "{\"a\": 2, \"b\": 3}"
    }
  ]
}
```

### Long instructions → no tool call, generic output

With `instructions: "You are a helpful math assistant. Always use the add tool for arithmetic."` (73 chars), the tool call disappears. The model ignores the user message ("Call the add tool with a=2 and b=3") and outputs generic text:

```json
{
  "outputs": [
    {
      "type": "message.output",
      "role": "assistant",
      "content": "Got it! I'm here to help with math problems, calculations, and explanations."
    }
  ]
}
```

### The threshold is not purely character-based

The boundary depends on tokenization, not character count. Adding one word can flip the behavior:

| `instructions`                                                                      | len | tool call |
|-------------------------------------------------------------------------------------|-----|-----------|
| `"You have an add tool. Use it."`                                                   |  29 | ✓         |
| `"You are a helpful math assistant. Always use the add tool"`                       |  57 | ✓         |
| `"You are a helpful math assistant. Always use the add tool for arithmetic."`       |  73 | ✗         |

### Short instructions are also intermittent

Even with short instructions that normally work, we observe extended periods (minutes) where all requests fail identically, followed by periods where they all succeed. The transitions are not triggered by client behavior — identical requests flip en masse.

## Environment

- API endpoint: `https://api.mistral.ai/v1/conversations`
- Model: `labs-leanstral-2603`
- Date: 2026-04-17
- Tested with both `stream: true` and `stream: false`
- Tested with `reasoning_effort: "high"` and `"none"` — same behavior

## Impact

Any real application requires system prompts longer than ~15 tokens, making tool calling unusable for `labs-leanstral-2603`.
