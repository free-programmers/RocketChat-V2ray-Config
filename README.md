# RocketChat V2ray Hunter

A Python bot that automatically fetches V2Ray, VLESS, and Trojan configurations from a remote repository, tests their connectivity, measures latency, and sends working configurations to a Rocket.Chat channel via webhook.

## Features

- Supports **VMess**, **VLESS**, and **Trojan** protocols.
- **Automatic testing** of configurations every 12 minutes.
- Measures **ping/latency** for each configuration.
- Sends working configurations to a **Rocket.Chat webhook** with proper formatting.
- Handles **large subscription files** with multiple configurations.
- Emoji-safe JSON formatting and readable code block messages.

## Requirements

- Python 3.9+
- `requests` library
- `v2ray` installed for VMess configuration testing
- Rocket.Chat account with incoming webhook

## Usage

1. Clone the repository.
2. Create a `config.py` file with your configuration:

```python
ROCKET_WEBHOOK = "https://your.rocketchat.server/hooks/XXXXXXX"
CONFIG_URL = "https://example.com/v2ray_configs.txt"
LOCAL_PORT = 1080
FETCH_INTERVAL = 12 * 60
TEST_URL = "http://httpbin.org/ip"
CHANNEL = "#your-channel"
```

3. Run the bot:

```bash
python bot.py
```

The bot will automatically fetch configs, test them, and send working ones to the specified Rocket.Chat channel.
