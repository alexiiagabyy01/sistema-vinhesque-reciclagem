import json
import mimetypes
import os
import re
import shutil
import socket
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from PIL import Image, ImageWin
except ModuleNotFoundError:
    Image = None
    ImageWin = None

try:
    from vr_reciclagem import VRReciclagemApp
except ModuleNotFoundError:
    VRReciclagemApp = None


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "vr_reciclagem.db"
DB_PATH = Path(os.environ.get("DB_PATH", str(DEFAULT_DB_PATH))).resolve()
RECEIPTS_DIR = Path(os.environ.get("RECEIPTS_DIR", str(BASE_DIR / "comprovantes"))).resolve()
STATIC_DIR = BASE_DIR / "mobile_app"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8765"))
SYNC_TOKEN = os.environ.get("SYNC_TOKEN", "").strip()
try:
    APP_TIMEZONE = ZoneInfo(os.environ.get("APP_TIMEZONE", "America/Sao_Paulo"))
except ZoneInfoNotFoundError:
    APP_TIMEZONE = timezone(timedelta(hours=-3), "America/Sao_Paulo")


def now_local():
    return datetime.now(APP_TIMEZONE)


def parse_mobile_datetime(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return now_local()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=APP_TIMEZONE)
    return parsed.astimezone(APP_TIMEZONE)


def money(value):
    return f"R$ {float(value or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def kg(value):
    return f"{float(value or 0):,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")


def normalize_name(value):
    return " ".join(str(value or "").strip().split())


def date_br(value):
    text = str(value or "")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19], fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return text


def wrap_line(text, max_chars=30):
    text = str(text or "")
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        if len(current) + len(word) + 1 <= max_chars:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def consolidate_receipt_items(items):
    grouped = {}
    order = []
    for item in items:
        key = item["material_nome"]
        if key not in grouped:
            grouped[key] = {
                "material_nome": item["material_nome"],
                "peso_liquido": 0.0,
                "desconto": 0.0,
                "preco_kg": float(item["preco_kg"]),
                "subtotal": 0.0,
            }
            order.append(key)
        grouped[key]["peso_liquido"] += float(item["peso_liquido"])
        grouped[key]["desconto"] += float(item["desconto"])
        grouped[key]["subtotal"] += float(item["subtotal"])
    consolidated = []
    for key in order:
        item = grouped[key]
        if item["peso_liquido"] > 0:
            item["preco_kg"] = item["subtotal"] / item["peso_liquido"]
        consolidated.append(item)
    return consolidated


def get_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def desktop_user_name():
    try:
        source = (BASE_DIR / "vr_reciclagem.py").read_text(encoding="utf-8")
    except OSError:
        return "Administrador"
    match = re.search(r'^USUARIO_ADMIN\s*=\s*[\'"]([^\'"]+)[\'"]', source, re.MULTILINE)
    return match.group(1) if match else "Administrador"


def ensure_storage():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        return
    if DEFAULT_DB_PATH.exists() and DEFAULT_DB_PATH.resolve() != DB_PATH:
        shutil.copy2(DEFAULT_DB_PATH, DB_PATH)


@contextmanager
def connect_db():
    ensure_storage()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                telefone TEXT DEFAULT '',
                cnpj TEXT DEFAULT '',
                cidade TEXT DEFAULT '',
                observacao TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS materiais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                preco_compra REAL NOT NULL DEFAULT 0,
                preco_venda REAL NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                cliente_nome TEXT NOT NULL,
                data TEXT NOT NULL,
                total REAL NOT NULL DEFAULT 0,
                observacao TEXT DEFAULT '',
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transacao_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transacao_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                material_nome TEXT NOT NULL,
                peso_bruto REAL NOT NULL DEFAULT 0,
                desconto REAL NOT NULL DEFAULT 0,
                peso_liquido REAL NOT NULL DEFAULT 0,
                preco_kg REAL NOT NULL DEFAULT 0,
                subtotal REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(transacao_id) REFERENCES transacoes(id),
                FOREIGN KEY(material_id) REFERENCES materiais(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comprovantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transacao_id INTEGER NOT NULL,
                numero TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                cliente_nome TEXT NOT NULL,
                data TEXT NOT NULL,
                total REAL NOT NULL DEFAULT 0,
                conteudo TEXT NOT NULL,
                FOREIGN KEY(transacao_id) REFERENCES transacoes(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mobile_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mobile_id TEXT NOT NULL UNIQUE,
                transacao_id INTEGER,
                status TEXT NOT NULL DEFAULT 'synced',
                payload TEXT NOT NULL,
                synced_at TEXT NOT NULL
            )
        """)
        for sql in (
            "ALTER TABLE clientes ADD COLUMN tipo TEXT DEFAULT 'Comprador'",
            "ALTER TABLE clientes ADD COLUMN email TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN estado TEXT DEFAULT ''",
            "ALTER TABLE clientes ADD COLUMN endereco TEXT DEFAULT ''",
            "ALTER TABLE materiais ADD COLUMN descricao TEXT DEFAULT ''",
            "ALTER TABLE materiais ADD COLUMN estoque_minimo REAL NOT NULL DEFAULT 0",
            "ALTER TABLE materiais ADD COLUMN ativo INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE transacoes ADD COLUMN pagamento TEXT DEFAULT ''",
            "ALTER TABLE transacoes ADD COLUMN destino_compra TEXT DEFAULT ''",
        ):
            try:
                conn.execute(sql)
            except sqlite3.OperationalError:
                pass


def fetch_catalog():
    with connect_db() as conn:
        clientes = conn.execute("""
            SELECT id, nome, telefone, cnpj, cidade, observacao
            FROM clientes
            ORDER BY nome
        """).fetchall()
        materiais = conn.execute("""
            SELECT id, nome, preco_compra, preco_venda, estoque_minimo, ativo
            FROM materiais
            WHERE ativo = 1
            ORDER BY nome
        """).fetchall()
        today = now_local().strftime("%Y-%m-%d")
        resumo = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'COMPRA' THEN 1 ELSE 0 END), 0) AS compras,
                COALESCE(SUM(CASE WHEN tipo = 'VENDA' THEN 1 ELSE 0 END), 0) AS vendas,
                COALESCE(SUM(CASE WHEN tipo = 'VENDA' THEN total ELSE 0 END), 0) AS total_vendas
            FROM transacoes
            WHERE substr(data, 1, 10) = ?
        """, (today,)).fetchone()
    return {
        "usuario": desktop_user_name(),
        "resumo_dia": dict(resumo) if resumo else {"compras": 0, "vendas": 0, "total_vendas": 0},
        "ultima_sincronizacao": now_local().strftime("%d/%m/%Y %H:%M"),
        "clientes": [dict(row) for row in clientes],
        "materiais": [dict(row) for row in materiais],
    }


def fetch_mobile_operations():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT mobile_id, transacao_id, status, payload, synced_at
            FROM mobile_sync
            ORDER BY id
        """).fetchall()
    operations = []
    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except (TypeError, json.JSONDecodeError):
            payload = {}
        operations.append({
            "mobile_id": row["mobile_id"],
            "transacao_id": row["transacao_id"],
            "status": row["status"],
            "synced_at": row["synced_at"],
            "operation": payload,
        })
    return operations


def import_desktop_catalog(payload):
    clientes = payload.get("clientes") or []
    materiais = payload.get("materiais") or []
    with connect_db() as conn:
        for cliente in clientes:
            nome = normalize_name(cliente.get("nome"))
            if not nome:
                continue
            existing = conn.execute("SELECT id FROM clientes WHERE lower(trim(nome)) = lower(trim(?))", (nome,)).fetchone()
            values = (
                nome,
                str(cliente.get("telefone") or "").strip(),
                str(cliente.get("cnpj") or "").strip(),
                str(cliente.get("cidade") or "").strip(),
                str(cliente.get("observacao") or "").strip(),
                str(cliente.get("tipo") or "Comprador").strip() or "Comprador",
                str(cliente.get("email") or "").strip(),
                str(cliente.get("estado") or "").strip(),
                str(cliente.get("endereco") or "").strip(),
            )
            if existing:
                conn.execute("""
                    UPDATE clientes
                    SET telefone = ?, cnpj = ?, cidade = ?, observacao = ?, tipo = ?, email = ?, estado = ?, endereco = ?
                    WHERE id = ?
                """, (*values[1:], existing["id"]))
            else:
                conn.execute("""
                    INSERT INTO clientes (nome, telefone, cnpj, cidade, observacao, tipo, email, estado, endereco)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

        for material in materiais:
            nome = normalize_name(material.get("nome"))
            if not nome:
                continue
            existing = conn.execute("SELECT id FROM materiais WHERE lower(trim(nome)) = lower(trim(?))", (nome,)).fetchone()
            values = (
                nome,
                float(material.get("preco_compra") or 0),
                float(material.get("preco_venda") or 0),
                str(material.get("descricao") or "").strip(),
                float(material.get("estoque_minimo") or 0),
                int(material.get("ativo", 1)),
            )
            if existing:
                conn.execute("""
                    UPDATE materiais
                    SET preco_compra = ?, preco_venda = ?, descricao = ?, estoque_minimo = ?, ativo = ?
                    WHERE id = ?
                """, (*values[1:], existing["id"]))
            else:
                conn.execute("""
                    INSERT INTO materiais (nome, preco_compra, preco_venda, descricao, estoque_minimo, ativo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, values)
    return {"ok": True, "clientes": len(clientes), "materiais": len(materiais)}


def saldo_material(conn, material_id):
    row = conn.execute("""
        SELECT COALESCE(
            SUM(CASE
                WHEN t.tipo='COMPRA' THEN i.peso_liquido
                WHEN t.tipo='VENDA' THEN -i.peso_liquido
                ELSE 0
            END),
            0
        ) AS saldo
        FROM transacao_itens i
        JOIN transacoes t ON t.id = i.transacao_id
        WHERE i.material_id = ?
    """, (material_id,)).fetchone()
    return float(row["saldo"] if row else 0.0)


def cliente_por_nome_ou_criar(conn, nome, tipo, telefone="", documento=""):
    nome_limpo = normalize_name(nome)
    if not nome_limpo:
        raise ValueError("Cliente obrigatorio.")
    row = conn.execute("SELECT * FROM clientes WHERE lower(trim(nome)) = lower(trim(?))", (nome_limpo,)).fetchone()
    if row:
        return row
    tipo_cliente = "Vendedor" if tipo == "COMPRA" else "Comprador"
    conn.execute("""
        INSERT INTO clientes (nome, telefone, cnpj, cidade, observacao, tipo, email, estado, endereco)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome_limpo,
        str(telefone or "").strip(),
        str(documento or "").strip(),
        "",
        "Cadastro automatico gerado pelo app mobile.",
        tipo_cliente,
        "",
        "",
        "",
    ))
    return conn.execute("SELECT * FROM clientes WHERE lower(trim(nome)) = lower(trim(?))", (nome_limpo,)).fetchone()


def montar_comprovante(numero, operation, data, total):
    tipo = operation["tipo"]
    itens_consolidados = consolidate_receipt_items(operation.get("itens", []))
    peso_total = sum(float(item["peso_liquido"]) for item in itens_consolidados)
    largura_linha = 38
    cliente_texto = normalize_name(operation.get("cliente_nome"))[:25]
    data_br_texto = date_br(data)
    hora = str(data)[11:16] if len(str(data)) >= 16 else ""
    lines = [
        "VR VINHESQUE RECICLAGEM",
        "SUSTENTABILIDADE QUE GERA VALOR",
        "",
        f"CONTROLE {numero}",
        f"DATA     {data_br_texto} {hora}".rstrip(),
        "=" * largura_linha,
        "DADOS DA OPERACAO",
        f"TIPO     {tipo.title()}",
        f"CLIENTE  {cliente_texto}",
        "=" * largura_linha,
        "PRODUTOS",
        "MATERIAL|QTD|DESC|V/KG|TOTAL",
        "-" * largura_linha,
    ]
    for item in itens_consolidados:
        lines.append(
            f"{normalize_name(item.get('material_nome'))}|"
            f"{kg(item.get('peso_liquido')).replace(' kg', '')}|"
            f"{kg(item.get('desconto')).replace(' kg', '')}|"
            f"{money(item.get('preco_kg')).replace('R$ ', '')}|"
            f"{money(item.get('subtotal')).replace('R$ ', '')}"
        )
    lines.extend([
        "-" * largura_linha,
        f"{'PESO TOTAL':<23}{kg(peso_total):>13}",
        f"{'TOTAL':<23}{money(total):>13}",
        "",
        "Obrigado pela preferencia!",
    ])
    observacao = normalize_name(operation.get("observacao"))
    if observacao:
        lines.extend(["", "OBSERVACOES"])
        lines.extend(wrap_line(observacao, 30))
    return "\n".join(lines)


def receipt_renderer():
    if VRReciclagemApp is None or Image is None:
        raise RuntimeError("Pillow/customtkinter nao esta disponivel neste Python.")
    renderer = VRReciclagemApp.__new__(VRReciclagemApp)
    renderer.script_dir = str(BASE_DIR)
    renderer.asset_dir = str(BASE_DIR / "assets")
    renderer.comprovante_logo_path = str(BASE_DIR / "assets" / "logo_comprovante_preta.png")
    return renderer


def save_official_receipt_png(numero, conteudo):
    comprovantes_dir = RECEIPTS_DIR
    comprovantes_dir.mkdir(exist_ok=True)
    txt_path = comprovantes_dir / f"{numero}.txt"
    txt_path.write_text(conteudo, encoding="utf-8")
    png_path = comprovantes_dir / f"{numero}.png"
    renderer = receipt_renderer()
    config = renderer.comprovante_print_config()
    image = renderer.criar_imagem_comprovante(conteudo)
    image.save(png_path, dpi=(config["render_dpi"], config["render_dpi"]))
    return png_path


def save_receipt_assets(numero, conteudo):
    try:
        png_path = save_official_receipt_png(numero, conteudo)
        return png_path, None
    except Exception as exc:
        comprovantes_dir = RECEIPTS_DIR
        comprovantes_dir.mkdir(exist_ok=True)
        txt_path = comprovantes_dir / f"{numero}.txt"
        txt_path.write_text(conteudo, encoding="utf-8")
        return None, str(exc)


def default_printer_name():
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        winspool = ctypes.WinDLL("winspool.drv")
        size = wintypes.DWORD(0)
        winspool.GetDefaultPrinterW(None, ctypes.byref(size))
        if size.value <= 1:
            return None
        buffer = ctypes.create_unicode_buffer(size.value)
        if not winspool.GetDefaultPrinterW(buffer, ctypes.byref(size)):
            return None
        return buffer.value
    except Exception:
        return None


def print_receipt_png(numero, png_path):
    if Image is None or ImageWin is None:
        return False, "Pillow nao esta instalado neste Python."
    if os.name != "nt":
        return False, "Impressao direta disponivel apenas no Windows."
    printer_name = default_printer_name()
    if not printer_name:
        return False, "Nenhuma impressora padrao configurada."
    try:
        import ctypes
        from ctypes import wintypes

        class DOCINFOW(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_int),
                ("lpszDocName", wintypes.LPCWSTR),
                ("lpszOutput", wintypes.LPCWSTR),
                ("lpszDatatype", wintypes.LPCWSTR),
                ("fwType", wintypes.DWORD),
            ]

        HORZRES = 8
        VERTRES = 10
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        PHYSICALOFFSETX = 112
        PHYSICALOFFSETY = 113

        gdi32 = ctypes.windll.gdi32
        hdc = gdi32.CreateDCW("WINSPOOL", printer_name, None, None)
        if not hdc:
            raise RuntimeError("Nao foi possivel acessar a impressora padrao.")

        renderer = receipt_renderer()
        config = renderer.comprovante_print_config()
        doc_started = False
        page_started = False
        try:
            with Image.open(png_path) as source_image:
                image = source_image.convert("RGB")

            printable_width = gdi32.GetDeviceCaps(hdc, HORZRES)
            printable_height = gdi32.GetDeviceCaps(hdc, VERTRES)
            dpi_x = gdi32.GetDeviceCaps(hdc, LOGPIXELSX) or config["render_dpi"]
            dpi_y = gdi32.GetDeviceCaps(hdc, LOGPIXELSY) or config["render_dpi"]
            offset_x = gdi32.GetDeviceCaps(hdc, PHYSICALOFFSETX)
            offset_y = gdi32.GetDeviceCaps(hdc, PHYSICALOFFSETY)
            target_width = min(printable_width, renderer.mm_to_px(config.get("content_width_mm", config["printable_width_mm"]), dpi_x))
            target_height_limit = min(printable_height, renderer.mm_to_px(config["paper_height_mm"], dpi_y))
            scale = target_width / float(image.width)
            draw_width = max(1, int(round(image.width * scale)))
            draw_height = max(1, int(round(image.height * scale)))
            if draw_height > target_height_limit:
                fit_scale = target_height_limit / float(draw_height)
                draw_width = max(1, int(round(draw_width * fit_scale)))
                draw_height = max(1, int(round(draw_height * fit_scale)))
            x = offset_x + max(0, (printable_width - draw_width) // 2)
            y = offset_y

            doc_info = DOCINFOW()
            doc_info.cbSize = ctypes.sizeof(DOCINFOW)
            doc_info.lpszDocName = f"Comprovante {numero}"
            doc_info.lpszOutput = None
            doc_info.lpszDatatype = None
            doc_info.fwType = 0
            if gdi32.StartDocW(hdc, ctypes.byref(doc_info)) <= 0:
                raise RuntimeError("Nao foi possivel iniciar a impressao.")
            doc_started = True
            if gdi32.StartPage(hdc) <= 0:
                raise RuntimeError("Nao foi possivel iniciar a pagina de impressao.")
            page_started = True
            ImageWin.Dib(image).draw(hdc, (x, y, x + draw_width, y + draw_height))
            if gdi32.EndPage(hdc) <= 0:
                raise RuntimeError("Nao foi possivel finalizar a pagina de impressao.")
            page_started = False
            if gdi32.EndDoc(hdc) <= 0:
                raise RuntimeError("Nao foi possivel concluir o envio para a impressora.")
            doc_started = False
        except Exception:
            if page_started or doc_started:
                try:
                    gdi32.AbortDoc(hdc)
                except Exception:
                    pass
            raise
        finally:
            gdi32.DeleteDC(hdc)
        return True, f"Impresso em {printer_name}."
    except Exception as exc:
        return False, str(exc)


def import_operation(operation):
    mobile_id = normalize_name(operation.get("mobile_id"))
    tipo = normalize_name(operation.get("tipo")).upper()
    if not mobile_id:
        raise ValueError("mobile_id ausente.")
    if tipo not in {"COMPRA", "VENDA"}:
        raise ValueError("Tipo invalido.")
    itens = operation.get("itens") or []
    if not itens:
        raise ValueError("Operacao sem itens.")

    with connect_db() as conn:
        existing = conn.execute("SELECT transacao_id FROM mobile_sync WHERE mobile_id = ?", (mobile_id,)).fetchone()
        if existing:
            return {"ok": True, "mobile_id": mobile_id, "transacao_id": existing["transacao_id"], "message": "Ja sincronizado."}

        normalized_items = []
        for item in itens:
            material_id = item.get("material_id")
            material = None
            if material_id:
                material = conn.execute("SELECT * FROM materiais WHERE id = ?", (material_id,)).fetchone()
                if material and normalize_name(material["nome"]).lower() != normalize_name(item.get("material_nome")).lower():
                    material = None
            if not material:
                material_name = normalize_name(item.get("material_nome"))
                material = conn.execute("SELECT * FROM materiais WHERE lower(trim(nome)) = lower(trim(?))", (material_name,)).fetchone()
            if not material:
                raise ValueError(f"Material nao encontrado: {item.get('material_nome', '')}")
            peso_bruto = float(item.get("peso_bruto") or 0)
            desconto = float(item.get("desconto") or 0)
            peso_liquido = max(float(item.get("peso_liquido") or (peso_bruto - desconto)), 0)
            preco_kg = float(item.get("preco_kg") or 0)
            subtotal = float(item.get("subtotal") or (peso_liquido * preco_kg))
            if peso_liquido <= 0:
                raise ValueError(f"Peso invalido para {material['nome']}.")
            normalized_items.append({
                "material_id": material["id"],
                "material_nome": material["nome"],
                "peso_bruto": peso_bruto,
                "desconto": desconto,
                "peso_liquido": peso_liquido,
                "preco_kg": preco_kg,
                "subtotal": subtotal,
            })

        if tipo == "VENDA":
            requested = {}
            names = {}
            for item in normalized_items:
                requested[item["material_id"]] = requested.get(item["material_id"], 0.0) + item["peso_liquido"]
                names[item["material_id"]] = item["material_nome"]
            for material_id, amount in requested.items():
                saldo = saldo_material(conn, material_id)
                if amount > saldo + 1e-9:
                    raise ValueError(f"Estoque insuficiente para {names[material_id]}: disponivel {kg(saldo)}, venda {kg(amount)}.")

        cliente = cliente_por_nome_ou_criar(
            conn,
            operation.get("cliente_nome"),
            tipo,
            operation.get("cliente_telefone", ""),
            operation.get("cliente_documento", ""),
        )
        total = sum(item["subtotal"] for item in normalized_items)
        raw_date = operation.get("created_at")
        data = parse_mobile_datetime(raw_date).strftime("%Y-%m-%d %H:%M:%S")

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transacoes (tipo, cliente_id, cliente_nome, data, total, observacao, destino_compra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            tipo,
            cliente["id"],
            cliente["nome"],
            data,
            total,
            normalize_name(operation.get("observacao")),
            normalize_name(operation.get("destino_compra")) if tipo == "COMPRA" else "",
        ))
        transacao_id = cur.lastrowid
        for item in normalized_items:
            cur.execute("""
                INSERT INTO transacao_itens
                (transacao_id, material_id, material_nome, peso_bruto, desconto, peso_liquido, preco_kg, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transacao_id,
                item["material_id"],
                item["material_nome"],
                item["peso_bruto"],
                item["desconto"],
                item["peso_liquido"],
                item["preco_kg"],
                item["subtotal"],
            ))

        numero = f"{tipo[0]}-{transacao_id:06d}"
        conteudo = montar_comprovante(numero, {**operation, "tipo": tipo, "itens": normalized_items}, data, total)
        cur.execute("""
            INSERT INTO comprovantes (transacao_id, numero, tipo, cliente_nome, data, total, conteudo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (transacao_id, numero, tipo, cliente["nome"], data, total, conteudo))
        png_path, receipt_warning = save_receipt_assets(numero, conteudo)
        if png_path:
            printed, print_message = print_receipt_png(numero, png_path)
        else:
            printed = False
            print_message = f"Comprovante oficial salvo em TXT. {receipt_warning}"
        cur.execute("""
            INSERT INTO mobile_sync (mobile_id, transacao_id, status, payload, synced_at)
            VALUES (?, ?, ?, ?, ?)
        """, (mobile_id, transacao_id, "synced", json.dumps(operation, ensure_ascii=False), now_local().strftime("%Y-%m-%d %H:%M:%S")))
        return {
            "ok": True,
            "mobile_id": mobile_id,
            "transacao_id": transacao_id,
            "numero": numero,
            "printed": printed,
            "print_message": print_message,
            "message": "Sincronizado.",
        }


class SyncHandler(BaseHTTPRequestHandler):
    server_version = "VinhesqueSync/1.0"

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Vinhesque-Token")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            return self.send_json({
                "ok": True,
                "database": str(DB_PATH),
                "receipts": str(RECEIPTS_DIR),
                "auth_required": bool(SYNC_TOKEN),
                "time": now_local().isoformat(timespec="seconds"),
            })
        if parsed.path == "/api/bootstrap":
            if not self.authorized():
                return self.send_json({"error": "Token de sincronizacao invalido."}, status=401)
            return self.send_json(fetch_catalog())
        if parsed.path == "/api/mobile-operations":
            if not self.authorized():
                return self.send_json({"error": "Token de sincronizacao invalido."}, status=401)
            return self.send_json({"operations": fetch_mobile_operations()})
        return self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/desktop-catalog":
            if not self.authorized():
                return self.send_json({"error": "Token de sincronizacao invalido."}, status=401)
            try:
                return self.send_json(import_desktop_catalog(self.read_json()))
            except Exception as exc:
                return self.send_json({"error": str(exc)}, status=400)
        if parsed.path != "/api/sync":
            return self.send_json({"error": "Rota nao encontrada."}, status=404)
        if not self.authorized():
            return self.send_json({"error": "Token de sincronizacao invalido."}, status=401)
        try:
            payload = self.read_json()
            operations = payload.get("operations") or []
            results = []
            for operation in operations:
                try:
                    results.append(import_operation(operation))
                except Exception as exc:
                    results.append({
                        "ok": False,
                        "mobile_id": operation.get("mobile_id"),
                        "message": str(exc),
                    })
            return self.send_json({"results": results})
        except Exception as exc:
            return self.send_json({"error": str(exc)}, status=400)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw)

    def authorized(self):
        if not SYNC_TOKEN:
            return True
        return self.headers.get("X-Vinhesque-Token", "").strip() == SYNC_TOKEN

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_static(self, path):
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        if relative.startswith("mobile_app/"):
            relative = relative[len("mobile_app/"):]
        target = (STATIC_DIR / relative).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists() or target.is_dir():
            target = STATIC_DIR / "index.html"
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        print(f"[{now_local().strftime('%H:%M:%S')}] {self.address_string()} - {format % args}")


def main():
    ensure_storage()
    init_db()
    lan_ip = get_lan_ip()
    server = ThreadingHTTPServer((HOST, PORT), SyncHandler)
    print("Vinhesque Mobile Sync")
    print(f"Banco: {DB_PATH}")
    print(f"Comprovantes: {RECEIPTS_DIR}")
    print(f"Notebook/local: http://127.0.0.1:{PORT}")
    print(f"Celular na mesma rede: http://{lan_ip}:{PORT}")
    if SYNC_TOKEN:
        print("Token de sincronizacao: ativo")
    print("Pressione Ctrl+C para parar.")
    server.serve_forever()


if __name__ == "__main__":
    main()
