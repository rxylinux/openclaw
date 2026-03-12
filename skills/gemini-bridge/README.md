# 🌉 Gemini Bridge v1.0

Turn **Google Gemini** into a REST API + CLI tool. No API key needed.

## How it works

```
Your Terminal/Script → Chrome AppleScript + JS injection → gemini.google.com → Response extracted via DOM
```

## Quick Start

### 1. Setup Permissions

```bash
# macOS: Allow Google Chrome in Automation settings
# System Settings > Privacy & Security > Automation
# ✓ Allow "Google Chrome"
```

### 2. Login to Gemini

Open `https://gemini.google.com` in Chrome and sign in.

### 3. Start the Server

```bash
python3 scripts/gemini_bridge.py --port 19999
```

### 4. Send a Request

```bash
curl -X POST http://localhost:19999/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello Gemini","timeout":60}'
```

## Usage

### REST API

```bash
# Chat
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"Explain quantum tunneling","timeout":120}'

# New session
curl -X POST http://localhost:19999/new

# History
curl http://localhost:19999/history

# Health check
curl http://localhost:19999/health
```

### CLI

```bash
# Basic usage
bash scripts/gemini_chat.sh "What is AI?"

# With timeout
bash gemini_chat.sh "Analyze NVIDIA stock" --timeout 90

# With session
bash gemini_chat.sh "Continue previous topic" --session my-session
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Send prompt, wait for response |
| POST | `/new` | Start new conversation |
| GET | `/health` | Health check (Chrome URL, Gemini status) |
| GET | `/history` | Read current page conversation |

## Example Response

```json
{
  "status": "ok",
  "response": "AI (Artificial Intelligence) is the simulation of human intelligence...",
  "elapsed": 5.3
}
```

## Multi-Session Support

```bash
# Create a session for stock analysis
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"Analyze AAPL","session_id":"stocks"}'

# Continue in the same session
curl -X POST http://localhost:19999/chat \
  -d '{"prompt":"What about TSLA?","session_id":"stocks"}'
```

## Requirements

- macOS with Chrome
- Logged into [gemini.google.com](https://gemini.google.com)
- Chrome > Settings > Privacy & Security > Automation > Allow Google Chrome

## Key Insights

### Zero Permissions

Unlike v2 (which required Accessibility), v1 uses:
- ✅ AppleScript `do JavaScript` (no extra permissions)
- ✅ `document.execCommand('insertText')` (works with React/Vue)
- ✅ JS `button.click()` (no System Events needed)

### Response Stability Detection

```python
# Poll DOM until response stabilizes
if body != body_before and body == last:
    stable += 1
    if stable >= 3:  # 3 consecutive identical checks
        return response
```

## License

MIT
