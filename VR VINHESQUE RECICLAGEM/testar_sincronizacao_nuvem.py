import sys

import desktop_cloud_sync
import sync_server


def main():
    config = desktop_cloud_sync.load_config()
    sync_server.DB_PATH = config["local_db_path"]
    if not sync_server.DB_PATH.exists():
        print(f"Banco local nao encontrado: {sync_server.DB_PATH}")
        return 1
    sync_server.init_db()
    print("Teste de sincronizacao Vinhesque")
    print(f"Nuvem: {config['cloud_url']}")
    print(f"Banco local: {sync_server.DB_PATH}")
    catalog_result, cloud_count, imported, skipped, errors = desktop_cloud_sync.sync_once(config)
    print(f"Catalogo enviado: {catalog_result.get('clientes', 0)} clientes")
    print(f"Materiais enviados: {catalog_result.get('materiais', 0)}")
    print(f"Operacoes na nuvem: {cloud_count}")
    print(f"Importados agora: {imported}")
    print(f"Ja estavam no banco: {skipped}")
    print(f"Erros: {len(errors)}")
    for error in errors:
        print(f"- {error}")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
