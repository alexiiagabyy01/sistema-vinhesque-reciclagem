import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import sync_server


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "cloud_sync_config.json"
LOG_PATH = BASE_DIR / "cloud_sync.log"
DEFAULT_INTERVAL_SECONDS = 60


def load_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
            config = json.load(file)
    else:
        config = {}
    url = (config.get("cloud_url") or os.environ.get("CLOUD_SYNC_URL") or "").strip().rstrip("/")
    token = (config.get("sync_token") or os.environ.get("SYNC_TOKEN") or "").strip()
    interval = int(config.get("interval_seconds") or os.environ.get("CLOUD_SYNC_INTERVAL") or DEFAULT_INTERVAL_SECONDS)
    local_db_path = (config.get("local_db_path") or os.environ.get("LOCAL_DB_PATH") or "vr_reciclagem.db").strip()
    if not url:
        raise RuntimeError("Configure cloud_sync_config.json com cloud_url.")
    db_path = Path(local_db_path)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    return {
        "cloud_url": url,
        "sync_token": token,
        "interval_seconds": max(interval, 15),
        "local_db_path": db_path.resolve(),
    }


def request_json(url, token):
    headers = {}
    if token:
      headers["X-Vinhesque-Token"] = token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url, token, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
      headers["X-Vinhesque-Token"] = token
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def write_log(message):
    line = f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] {message}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


def push_catalog(config):
    catalog = sync_server.fetch_catalog()
    response = post_json(f"{config['cloud_url']}/api/desktop-catalog", config["sync_token"], catalog)
    return response


def sync_once(config):
    catalog_result = push_catalog(config)
    payload = request_json(f"{config['cloud_url']}/api/mobile-operations", config["sync_token"])
    cloud_count = len(payload.get("operations", []))
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
    return catalog_result, cloud_count, imported, skipped, errors


def main():
    config = load_config()
    sync_server.DB_PATH = config["local_db_path"]
    if not sync_server.DB_PATH.exists():
        raise RuntimeError(
            f"Banco local nao encontrado: {sync_server.DB_PATH}\n"
            "Copie o vr_reciclagem.db da pasta antiga para a pasta nova, ao lado do arquivo .exe."
        )
    sync_server.init_db()
    print("Vinhesque Cloud Sync")
    print(f"Nuvem: {config['cloud_url']}")
    print(f"Banco local: {sync_server.DB_PATH}")
    print(f"Log: {LOG_PATH}")
    print("Pressione Ctrl+C para parar.")
    while True:
        try:
            catalog_result, cloud_count, imported, skipped, errors = sync_once(config)
            write_log(
                f"Catalogo enviado: {catalog_result.get('clientes', 0)} clientes, "
                f"{catalog_result.get('materiais', 0)} materiais | "
                f"Operacoes na nuvem: {cloud_count} | "
                f"Importados: {imported} | Ja estavam no banco: {skipped} | Erros: {len(errors)}"
            )
            for error in errors[:5]:
                write_log(f"Erro: {error}")
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            write_log(f"Aguardando nuvem: {exc}")
        time.sleep(config["interval_seconds"])


if __name__ == "__main__":
    main()
