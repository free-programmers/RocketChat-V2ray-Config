import requests
import subprocess
import schedule
import time
import json
import tempfile
import os
import socket
import base64
import time
from urllib.parse import urlparse
from config import *

# -------------------------
# Rocket.Chat webhook
# -------------------------
def send_to_rocketchat_webhook(message):
    print(f"sending new config to RocketChat server.")
    data = {"text": message}
    try:
        time.sleep(1)
        requests.post(ROCKET_WEBHOOK, json=data, timeout=5)
    except Exception as e:
        print("Failed to send message:", e)

# -------------------------
# V2Ray & Config Processing
# -------------------------
def download_configs(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.text.splitlines()

def parse_v2ray_line(line):
    line = line.strip()
    if line.startswith("vmess://"):
        b64data = line[len("vmess://"):]
        try:
            decoded = base64.b64decode(b64data).decode("utf-8")
            config_json = json.loads(decoded)
            return {"type": "vmess", "config": config_json}
        except Exception as e:
            print("Failed to decode vmess line:", e)
            return None
    elif line.startswith("vless://") or line.startswith("trojan://"):
        return {"type": "uri", "uri": line}
    else:
        return None

def tcp_ping(host, port, timeout=3):
    start = time.time()
    try:
        s = socket.create_connection((host, port), timeout)
        s.close()
        return int((time.time() - start) * 1000)  # ms
    except:
        return None

def test_v2ray_config(config_json):
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        json.dump(config_json, f, ensure_ascii=False)
        tmp_path = f.name

    process = subprocess.Popen(["v2ray", "-config", tmp_path])
    time.sleep(2)  # wait for V2Ray to start

    proxies = {
        "http": f"socks5h://127.0.0.1:{LOCAL_PORT}",
        "https": f"socks5h://127.0.0.1:{LOCAL_PORT}"
    }

    result = {"status": False, "info": ""}

    try:
        start_time = time.time()
        r = requests.get(TEST_URL, proxies=proxies, timeout=5)
        ping_ms = int((time.time() - start_time) * 1000)
        result["status"] = True
        result["info"] = {"ip": r.json().get("origin"), "ping_ms": ping_ms}
    except Exception as e:
        result["info"] = {"error": str(e), "ping_ms": "N/A", "ip": "N/A"}
    finally:
        process.terminate()
        os.unlink(tmp_path)

    return result

def extract_host_port_from_uri(uri):
    try:
        parsed = urlparse(uri)
        host = parsed.hostname
        port = parsed.port
        return host, port
    except:
        return None, None

def format_message(config, ping_info):
    if config["type"] == "vmess":
        config_str = json.dumps(config["config"], ensure_ascii=False)
    else:
        config_str = config["uri"]

    ping = ping_info.get("ping_ms", "N/A")
    ip = ping_info.get("ip", "N/A")

    message = (
        f"Auto Config Bot {time.time()}\n"
        f"✅ Working V2Ray Config found!\n"
        f"🌐Ping: {ping} ms\n"
        f"🌐IP: {ip}\n"
        f"🚧 Config:\n```\n{config_str}\n```"
    )
    return message

# -------------------------
# MAIN LOOP
# -------------------------
def main():
    while True:
        try:
            lines = download_configs(CONFIG_URL)
            print(f"Fetched {len(lines)} lines from subscription.")

            for line in lines:
                parsed = parse_v2ray_line(line)
                if parsed is None:
                    continue

                host, port = None, None
                if parsed["type"] == "vmess":
                    server_info = parsed["config"].get("outbounds", [{}])[0].get("settings", {}).get("vnext", [{}])[0]
                    host = server_info.get("address")
                    port = server_info.get("port")
                else:
                    host, port = extract_host_port_from_uri(parsed["uri"])

                if host and port:
                    ping_ms = tcp_ping(host, port)
                    if ping_ms is not None:
                        if parsed["type"] == "vmess":
                            result = test_v2ray_config(parsed["config"])
                            if result["status"]:
                                message = format_message(parsed, result["info"])
                                send_to_rocketchat_webhook(message)
                        else:
                            message = format_message(parsed, {"ping_ms": ping_ms, "ip": host})
                            send_to_rocketchat_webhook(message)
        except Exception as e:
            print("Error in main loop:", e)

        print(f"Sleeping {FETCH_INTERVAL/60} minutes...")
        time.sleep(FETCH_INTERVAL)


main()
schedule.every(3).hours.do(main)

while True:
    print(f"{time.time()}")
    schedule.run_pending()
    time.sleep(1)


