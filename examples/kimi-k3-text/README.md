# Kimi text migration fixture

## Python environment

For this tutorial we pin the OpenAI Python SDK to 3.26.0 as a safe, stable baseline; remember that this package itself requires Python 3.10 or newer, so ensure your base environment meets that threshold before proceeding.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
```

## Offline verification

```bash
python verify_offline.py
```

## API key and endpoint

You must have an API key on the platform you intend to use, with billing available there. A consumer Kimi membership price does not define the cost of this API call.

Your key and endpoint must belong to the same regional platform. Set `MOONSHOT_BASE_URL` to one endpoint only, not both.

```bash
export MOONSHOT_API_KEY="your-api-key"
# Global platform
export MOONSHOT_BASE_URL="https://api.moonshot.ai/v1"

# China platform: replace the endpoint assignment above with this alternative.
# export MOONSHOT_BASE_URL="https://api.moonshot.cn/v1"
```

Run it with:

```bash
python kimi_text.py
```

You will see a single line of text: Kimi K3’s final answer. Wording varies; this is an actual API call and incurs usage charges.
