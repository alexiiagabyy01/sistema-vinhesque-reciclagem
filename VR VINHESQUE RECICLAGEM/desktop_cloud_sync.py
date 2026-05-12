import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import sync_server


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "cloud_sync_config.json"
DEFAULT_INTERVAL_SECONDS = 60


def load_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)
    else:
        config = {}
    url = (config.get("cloud_url") or os.environ.get("CLOUD_SYNC_URL") or "").strip().rstrip("/")
    token = (config.get("sync_token") or os.environ.get("SYNC_TOKEN") or "").strip()
    interval = int(config.get("interval_seconds") or os.environ.get("CLOUD_SYNC_INTERVAL") or DEFAULT_INTERVAL_SECONDS)
    if not url:
        raise RuntimeError("Configure cloud_sync_config.json com cloud_url.")
    return {"cloud_url": url, "sync_token": token, "interval_seconds": max(interval, 15)}


def request_json(url, token):
    headers = {}
    if token:
      headers["X-Vinhesque-Token"] = token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def sync_once(config):
    payload = request_json(f"{config['cloud_url']}/api/mobile-operations", config["sync_token"])
    imported = 0
    skipped = 0
    errors = []
    for row in payload.get("operations", []):
        operation = row.get("operation") or {}
        if not operation:
            skipped += 1
            continue
        try:
            result = sync_server.import_operation(operation)
            if result.get("message") == "Ja sincronizado.":
                skipped += 1
            elif result.get("ok"):
                imported += 1
            else:
                errors.append(result.get("message") or "Erro desconhecido.")
        except Exception as exc:
            errors.append(f"{operation.get('mobile_id', '')}: {exc}")
    return imported, skipped, errors


def main():
    sync_server.init_db()
    config = load_config()
    print("Vinhesque Cloud Sync")
    print(f"Nuvem: {config['cloud_url']}")
    print(f"Banco local: {sync_server.DB_PATH}")
    print("Pressione Ctrl+C para parar.")
    while True:
        try:
            imported, skipped, errors = sync_once(config)
            now = time.strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{now}] Importados: {imported} | Ja estavam no banco: {skipped} | Erros: {len(errors)}")
            for error in errors[:5]:
                print(f"  - {error}")
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            now = time.strftime("%d/%m/%Y %H:%M:%S")
            print(f"[{now}] Aguardando nuvem: {exc}")
        time.sleep(config["interval_seconds"])


if __name__ == "__main__":
    main()
