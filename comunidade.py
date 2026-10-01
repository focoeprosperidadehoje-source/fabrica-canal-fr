import os, json, time, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as YTCredentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_FR")
YT_TOKEN_JSON = os.environ.get("YOUTUBE_TOKEN_FR")

CANAL_ID = "UC7dZrYzY22dO-h6RfRN1bsw"

client = Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})

def obter_modelo_lite():
    try:
        modelos = client.models.list()
        lite_models = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods and ('flash-lite' in m.name or '8b' in m.name)]
        return sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-2.5-flash-lite'
    except:
        return 'gemini-2.5-flash-lite'

modelo = obter_modelo_lite()

creds_yt = YTCredentials.from_authorized_user_info(json.loads(YT_TOKEN_JSON.lstrip('﻿')))
if creds_yt and creds_yt.expired and creds_yt.refresh_token: creds_yt.refresh(Request())
youtube = build('youtube', 'v3', credentials=creds_yt)

def listar_videos_recentes(max_results=5):
    try:
        resp = youtube.search().list(part="snippet", channelId=CANAL_ID, order="date", type="video", maxResults=max_results).execute()
        return [(item['id']['videoId'], item['snippet']['title']) for item in resp.get('items', [])]
    except Exception as e:
        print(f"Erro ao listar vídeos: {e}")
        return []

def listar_comentarios(video_id, max_results=20):
    try:
        resp = youtube.commentThreads().list(part="snippet", videoId=video_id, order="time", maxResults=max_results).execute()
        comentarios = []
        for item in resp.get('items', []):
            c = item['snippet']['topLevelComment']['snippet']
            if not c.get('authorIsChannelOwner', False):
                comentarios.append({'id': item['id'], 'texto': c['textDisplay'][:500], 'autor': c['authorDisplayName']})
        return comentarios
    except Exception as e:
        print(f"Erro ao listar comentários do vídeo {video_id}: {e}")
        return []

def gerar_resposta(comentario_texto, titulo_video):
    prompt = f"""Tu es la voix de Notre-Dame de Lourdes, parlant avec amour et compassion à un fidèle.

Un fidèle a commenté sur une vidéo de prière intitulée "{titulo_video}":
"{comentario_texto}"

Réponds avec une bénédiction courte (2-3 phrases) en français, dans l'esprit de la Vierge Marie.
Commence par reconnaître leur message avec chaleur.
Termine avec une bénédiction ou une prière courte.
N'utilise pas d'astérisques. Réponds directement, sans présentation."""

    try:
        resp = client.models.generate_content(model=modelo, contents=prompt)
        return resp.text.strip()[:800]
    except Exception as e:
        print(f"Erro Gemini: {e}")
        return None

def responder_comentario(comment_id, texto):
    try:
        youtube.comments().insert(part="snippet", body={
            "snippet": {"parentId": comment_id, "textOriginal": texto}
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao responder comentário {comment_id}: {e}")
        return False

print(f"🙏 Iniciando módulo de comunidade FR — {datetime.datetime.now()}")
videos = listar_videos_recentes(max_results=3)
print(f"Vídeos recentes: {len(videos)}")

for video_id, titulo in videos:
    print(f"\n📹 Processando: {titulo[:60]}...")
    comentarios = listar_comentarios(video_id, max_results=10)
    print(f"   {len(comentarios)} comentários encontrados.")

    for c in comentarios[:3]:
        print(f"   💬 Respondendo: {c['texto'][:80]}...")
        resposta = gerar_resposta(c['texto'], titulo)
        if resposta:
            ok = responder_comentario(c['id'], resposta)
            if ok: print(f"   ✅ Resposta enviada.")
            time.sleep(3)

print("✅ Módulo de comunidade FR concluído.")


# ===== EXPORTA PEDIDOS PARA A LIVE 24h (o token da live não lê comentários) =====
try:
    import os as _os, json as _json, datetime as _dt
    from google.oauth2.service_account import Credentials as _SAC
    from googleapiclient.discovery import build as _build
    _CANAL = "FR"
    _PLAN = "1KgIjWrLUVlllhlZB1R9fkHGxxZlLsax1aOVGZrYwgnU"
    _ABA = f"PEDIDOS_{_CANAL}"
    _info = _json.loads(_os.environ.get(f"GOOGLE_CREDENTIALS_{_CANAL}") or _os.environ["GOOGLE_CREDENTIALS"])
    _sh = _build("sheets", "v4", credentials=_SAC.from_service_account_info(
        _info, scopes=["https://www.googleapis.com/auth/spreadsheets"]), cache_discovery=False)
    _cid = youtube.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    _r = youtube.commentThreads().list(part="snippet", allThreadsRelatedToChannelId=_cid, maxResults=100,
                                       order="time", textFormat="plainText").execute()
    _lim = _dt.datetime.utcnow() - _dt.timedelta(hours=72)
    _rows = [["ThreadId", "Nome", "Pedido", "Data"]]
    for _it in _r.get("items", []):
        _s = _it["snippet"]["topLevelComment"]["snippet"]
        if _s.get("authorChannelId", {}).get("value") == _cid:
            continue
        _pub = _s.get("publishedAt", "")
        try:
            if _dt.datetime.strptime(_pub[:19], "%Y-%m-%dT%H:%M:%S") < _lim:
                continue
        except Exception:
            pass
        _rows.append([_it["id"], _s.get("authorDisplayName", ""), (_s.get("textOriginal") or "")[:300], _pub])
    _abas = [x["properties"]["title"] for x in _sh.spreadsheets().get(
        spreadsheetId=_PLAN, fields="sheets.properties.title").execute()["sheets"]]
    if _ABA not in _abas:
        _sh.spreadsheets().batchUpdate(spreadsheetId=_PLAN, body={"requests": [
            {"addSheet": {"properties": {"title": _ABA}}}]}).execute()
    _sh.spreadsheets().values().clear(spreadsheetId=_PLAN, range=f"{_ABA}!A:D").execute()
    _sh.spreadsheets().values().update(spreadsheetId=_PLAN, range=f"{_ABA}!A1", valueInputOption="RAW",
                                       body={"values": _rows}).execute()
    print(f"📮 Pedidos exportados para a live ({_ABA}): {len(_rows) - 1}")
except Exception as e:
    print(f"⚠️ Exportar pedidos para a live: {e}")
