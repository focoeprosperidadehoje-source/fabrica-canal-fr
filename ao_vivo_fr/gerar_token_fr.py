#!/usr/bin/env python3
"""
gerar_token_fr.py — Gera youtube_token.json para o Canal FR (live stream).
Executar uma unica vez no VPS1 apos o setup inicial.

Uso:
  cd /root/ao_vivo_fr
  python3 gerar_token_fr.py

O script mostra uma URL — abra no browser, autorize com
canalinteligenciadivinafrance@gmail.com, cole o codigo de volta aqui.
O token e salvo automaticamente em /root/ao_vivo_fr/youtube_token.json.

PRE-REQUISITO: YT_CLIENT_ID e YT_CLIENT_SECRET no .env.
Extraia do token do ES (mesmo OAuth client):
  python3 -c "import json; d=json.load(open('/root/ao_vivo_es/youtube_token.json')); print('YT_CLIENT_ID=' + d.get('client_id','')); print('YT_CLIENT_SECRET=' + d.get('client_secret',''))"
Depois adicione ao /root/ao_vivo_fr/.env:
  echo 'YT_CLIENT_ID=...' >> /root/ao_vivo_fr/.env
  echo 'YT_CLIENT_SECRET=...' >> /root/ao_vivo_fr/.env
"""

import os
import sys
from pathlib import Path


def _load_env(path: str):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass


_load_env("/root/ao_vivo_fr/.env")

CLIENT_ID     = os.environ.get("YT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET", "")
SAVE_PATH     = Path("/root/ao_vivo_fr/youtube_token.json")
SCOPES        = ["https://www.googleapis.com/auth/youtube"]

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERRO: YT_CLIENT_ID ou YT_CLIENT_SECRET ausentes em /root/ao_vivo_fr/.env")
    print()
    print("Extraia do token do ES (VPS1):")
    print("  python3 -c \"import json; d=json.load(open('/root/ao_vivo_es/youtube_token.json')); print('YT_CLIENT_ID=' + d.get('client_id','')); print('YT_CLIENT_SECRET=' + d.get('client_secret',''))\"")
    print()
    print("Depois adicione ao .env:")
    print("  echo 'YT_CLIENT_ID=...' >> /root/ao_vivo_fr/.env")
    print("  echo 'YT_CLIENT_SECRET=...' >> /root/ao_vivo_fr/.env")
    sys.exit(1)

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Instalando google-auth-oauthlib...")
    import subprocess
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "google-auth-oauthlib"],
        check=True,
    )
    from google_auth_oauthlib.flow import InstalledAppFlow

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

print("=" * 60)
print("Gerador de Token YouTube -- Canal FR")
print("=" * 60)
print()
print("1. Copie a URL abaixo e abra no navegador")
print("2. Faca login com canalinteligenciadivinafrance@gmail.com")
print("3. Autorize e copie o codigo exibido")
print("4. Cole o codigo aqui e pressione Enter")
print()

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
print(f"URL para autorizar:\n{auth_url}\n")
code = input("Cole o codigo aqui: ").strip()
flow.fetch_token(code=code)
creds = flow.credentials

SAVE_PATH.write_text(creds.to_json())
print()
print(f"Token salvo em {SAVE_PATH}")
print()
print("Proximo passo: iniciar a live FR:")
print("  systemctl start ao_vivo_fr")
print("  systemctl status ao_vivo_fr")
