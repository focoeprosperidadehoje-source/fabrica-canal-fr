#!/usr/bin/env python3
"""
gerar_bloco_live_fr.py — GitHub Actions: génère plusieurs blocs par exécution (Canal FR)

Exécuté 6x/jour par gerador_blocos_fr.yml. Chaque exécution :
  1. Récupère jusqu'à 100 commentaires du canal FR (1 appel YouTube API)
  2. Gemini classifie en 4-5 groupes thématiques (1 appel)
  3. Pour chaque groupe : génère script avec vrais prénoms + prière (1 appel lite)
  4. Edge TTS synthétise l'audio → audio_YYYYMMDD_HHMM_NN.mp3
  5. L'assembleur sur VPS construit les blocs H avec videos_base/

Persona : Notre-Dame de Lourdes, Vierge Marie (fr-FR-DeniseNeural)
"""

import os
import sys
import json
import random
import asyncio
import re
from datetime import datetime
from pathlib import Path

import pytz
import edge_tts
from google import genai
from google.genai import types as genai_types
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════

FUSO       = pytz.timezone("Europe/Paris")
VOZ        = "fr-FR-DeniseNeural"
VOZ_RATE   = "-25%"
VOZ_PITCH  = "-6Hz"
CANAL_ID   = "UC7dZrYzY22dO-h6RfRN1bsw"
DIR_BLOCOS = Path("blocos_fr")
MAX_GRUPOS = 5

MODELOS_LITE = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
MODELOS_FULL = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash"]

CHAVES = [k for k in [
    os.environ.get("GEMINI_KEY_LIVE_CONTENT_1_FR", ""),
    os.environ.get("GEMINI_KEY_LIVE_CONTENT_2_FR", ""),
] if k]

PILARES = {
    0: "Guerre Spirituelle et Protection Divine",
    1: "Libération des Addictions et des Liens",
    2: "Restauration de la Famille et Réconciliation",
    3: "Providence Divine et Portes Ouvertes",
    4: "Miséricorde Divine et Guérison Physique",
    5: "Le Manteau de la Vierge Marie",
    6: "Miracles et Action de Grâce",
}

GROUPES_HARDCODES = [
    {"tema": "guerison",    "label": "Guérison et Santé",                 "nomes": [], "suplica_comum": "pour les malades, la douleur et la guérison de nos frères et sœurs",           "num_fieis": 0},
    {"tema": "liberation",  "label": "Libération des Addictions",         "nomes": [], "suplica_comum": "pour la libération de l'alcool, des drogues et des liens du péché",             "num_fieis": 0},
    {"tema": "famille",     "label": "Restauration de la Famille",        "nomes": [], "suplica_comum": "pour les mariages en crise, les enfants prodiges et la paix dans les foyers",   "num_fieis": 0},
    {"tema": "provision",   "label": "Providence et Travail",             "nomes": [], "suplica_comum": "pour la provision financière, l'emploi et la liberté des dettes",               "num_fieis": 0},
    {"tema": "protection",  "label": "Protection Spirituelle",            "nomes": [], "suplica_comum": "pour la protection contre le mal, l'envie et tout danger",                       "num_fieis": 0},
]


# ═══════════════════════════════════════════════════════════════════════
# GEMINI
# ═══════════════════════════════════════════════════════════════════════

def _chamar_gemini(prompt: str, modelos: list, max_tokens: int = 2048) -> str:
    for chave in CHAVES:
        for modelo in modelos:
            try:
                client = genai.Client(api_key=chave)
                resp = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(max_output_tokens=max_tokens),
                )
                return resp.text.strip()
            except Exception as e:
                print(f"  [WARN] {modelo} [{chave[-6:]}]: {str(e)[:80]}")
    raise RuntimeError("Tous les modèles Gemini ont échoué.")


# ═══════════════════════════════════════════════════════════════════════
# CALENDRIER LITURGIQUE
# ═══════════════════════════════════════════════════════════════════════

def _paques(annee: int) -> datetime:
    a = annee % 19
    b, c = divmod(annee, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mois = (h + l - 7 * m + 114) // 31
    jour = (h + l - 7 * m + 114) % 31 + 1
    return datetime(annee, mois, jour)

def calcular_contexto_sazonal(data: datetime) -> str:
    annee = data.year
    p = _paques(annee)
    fixas = {
        (1, 1):   "Nouvel An — Solennité de Marie, Mère de Dieu",
        (2, 2):   "Présentation du Seigneur — Chandeleur",
        (2, 11):  "Notre-Dame de Lourdes — Journée Mondiale des Malades",
        (3, 19):  "Saint Joseph — Patron de l'Église Universelle",
        (5, 13):  "Notre-Dame de Fatima",
        (8, 15):  "Assomption de la Vierge Marie",
        (12, 8):  "Immaculée Conception de la Vierge Marie",
        (12, 12): "Notre-Dame de Guadalupe — Patronne des Amériques",
        (12, 24): "Veille de Noël",
        (12, 25): "Noël — Naissance de Notre-Seigneur",
    }
    if (data.month, data.day) in fixas:
        return fixas[(data.month, data.day)]
    diff = (data.date() - p.date()).days
    moveis = {
        -46: "Mercredi des Cendres — Début du Carême",
        -7:  "Dimanche des Rameaux",
        -2:  "Vendredi Saint — Passion et Mort de Notre-Seigneur",
         0:  "Alléluia ! Pâques — Résurrection !",
        49:  "Dimanche de Pentecôte",
        60:  "Fête-Dieu — Corpus Christi",
    }
    if diff in moveis:
        return moveis[diff]
    if data.weekday() == 4:
        return "Vendredi — Chemin de Miséricorde et de Pardon"
    return PILARES.get(data.weekday(), "Chemin de Prière et d'Intercession")


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE API
# ═══════════════════════════════════════════════════════════════════════

def get_youtube_readonly():
    raw = os.environ.get("YOUTUBE_TOKEN_FR", "")
    if not raw:
        return None
    try:
        data  = json.loads(raw)
        creds = OAuthCredentials.from_authorized_user_info(
            data, scopes=["https://www.googleapis.com/auth/youtube.readonly"]
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"  [WARN] YouTube readonly FR: {e}")
        return None

def buscar_comentarios_canal(yt) -> list[str]:
    if not yt:
        return []
    try:
        resp = yt.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId=CANAL_ID,
            maxResults=100,
            order="relevance",
        ).execute()
        textos = []
        for item in resp.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            texto = s.get("textOriginal", "").strip()
            if texto and len(texto) > 10:
                textos.append(texto[:200])
        print(f"  Commentaires FR obtenus : {len(textos)}")
        return textos
    except Exception as e:
        print(f"  [WARN] buscar_comentarios FR: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════
# CLASSIFICATION DES GROUPES
# ═══════════════════════════════════════════════════════════════════════

def _limpar_json(texto: str) -> str:
    texto = re.sub(r'```(?:json)?', '', texto)
    texto = re.sub(r'```', '', texto)
    inicio = texto.find('[')
    fim    = texto.rfind(']')
    if inicio != -1 and fim != -1:
        return texto[inicio:fim+1]
    return texto.strip()

def classificar_grupos(comentarios: list[str], pilar_hoje: str) -> list[dict]:
    if len(comentarios) >= 5:
        lista_str = "\n".join(f"- {c}" for c in comentarios[:80])
        prompt = f"""Analysez ces commentaires de fidèles catholiques sur une chaîne de prière.
Extrayez le prénom (si présent) et classifiez la supplication de chaque commentaire.
Regroupez en maximum 5 thèmes (ex : guérison, libération, famille, finances, protection).

Retournez UNIQUEMENT du JSON valide sans markdown ni texte supplémentaire :
[{{"tema":"slug","label":"Nom du groupe","nomes":["prénom1","prénom2"],"suplica_comum":"pétition commune en max 15 mots","num_fieis":N}}]

RÈGLES :
- Uniquement les prénoms qui apparaissent dans les commentaires ; n'inventez pas
- suplica_comum : maximum 15 mots décrivant la pétition commune
- Minimum 3 groupes, maximum 5

COMMENTAIRES :
{lista_str}"""
        try:
            raw = _chamar_gemini(prompt, MODELOS_LITE, max_tokens=1024)
            grupos = json.loads(_limpar_json(raw))
            if isinstance(grupos, list) and len(grupos) >= 2:
                print(f"  Groupes FR classifiés : {len(grupos)}")
                for g in grupos:
                    n = len(g.get("nomes", []))
                    print(f"    [{g.get('tema','')}] {g.get('num_fieis',0)} fidèles, {n} prénoms")
                return grupos[:MAX_GRUPOS]
            print("  [WARN] JSON invalide ou trop peu de groupes — utilisation du fallback")
        except Exception as e:
            print(f"  [WARN] classify_groups FR: {e}")

    print("  [Fallback 1] Génération de groupes thématiques via Gemini FR...")
    prompt_fb = f"""Créez 4 groupes d'intentions de prière fréquentes parmi les fidèles catholiques francophones.
Le pilier spirituel d'aujourd'hui est : {pilar_hoje}
Retournez UNIQUEMENT du JSON valide :
[{{"tema":"slug","label":"Nom","nomes":[],"suplica_comum":"pétition en max 15 mots","num_fieis":0}}]"""
    try:
        raw = _chamar_gemini(prompt_fb, MODELOS_LITE, max_tokens=512)
        grupos = json.loads(_limpar_json(raw))
        if isinstance(grupos, list) and len(grupos) >= 2:
            print(f"  Groupes FR fallback : {len(grupos)}")
            return grupos[:MAX_GRUPOS]
    except Exception as e:
        print(f"  [WARN] fallback groups FR: {e}")

    print("  [Fallback 2] Utilisation des groupes FR codés en dur.")
    return GROUPES_HARDCODES[:MAX_GRUPOS]


# ═══════════════════════════════════════════════════════════════════════
# GÉNÉRATION DU SCRIPT
# ═══════════════════════════════════════════════════════════════════════

def _formatar_nomes(nomes: list) -> str:
    nomes = [n for n in nomes if n and len(n) >= 2]
    if not nomes:
        return "chaque frère et sœur qui prie avec nous en ce moment"
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + f" et {nomes[-1]}"

def gerar_roteiro_grupo(grupo: dict, contexto: str, pilar: str,
                        agora: datetime, num_bloco: int,
                        so_full: bool = False) -> str:
    nomes_raw  = grupo.get("nomes", [])
    nomes_str  = _formatar_nomes(nomes_raw)
    suplica    = grupo.get("suplica_comum", "pour les besoins de nos frères et sœurs")
    label      = grupo.get("label", "Prière d'Intercession")
    tem_nomes  = len([n for n in nomes_raw if n and len(n) >= 2]) > 0

    nota_nomes = (
        f"Mentionnez chaque prénom avec tendresse maternelle : {nomes_str}"
        if tem_nomes else
        "Il n'y a pas de prénoms spécifiques — parlez de 'chaque frère et sœur qui prie en ce moment'"
    )
    nota_miguel = (
        "Quand c'est naturel dans l'intercession, mentionnez l'Archange Saint Michel comme gardien spirituel combattant à nos côtés."
        if "Guerre Spirituelle" in pilar else ""
    )

    prompt = f"""Vous êtes la Vierge Marie, Notre-Dame de Lourdes, parlant à la première personne, en français.
Bloc #{num_bloco} | Groupe : {label}
Contexte liturgique du jour : {contexto}
Pilier spirituel d'aujourd'hui : {pilar}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRUCTURE (20 minutes — entre 2600 et 3000 mots) :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OUVERTURE — premières 90 secondes — OBLIGATOIRE]
Ouvrez en citant les frères et sœurs qui ont demandé l'intercession :
"{nota_nomes}"
Supplication commune de ce groupe : "{suplica}"
Terminez l'ouverture par : "Je suis venue intercéder pour vous en ce moment..."

[CORPS PRINCIPAL — ~16 minutes]
ALTERNANCE OBLIGATOIRE — le bloc doit osciller entre deux modes :
  Mode A (NARRATION) : Notre-Dame parle, accueille, révèle la grâce — voix chaleureuse et maternelle
  Mode B (PRIÈRE GUIDÉE) : Notre-Dame conduit l'auditeur à prier à voix haute avec elle
  Ex : "Répétez avec moi dans la foi : Seigneur, je crois... Seigneur, je me confie..."
  Ex : "Posez votre main sur votre cœur et dites : Mère du Ciel, je reçois cette grâce maintenant..."
  Chaque transition entre les modes doit être fluide et naturelle — minimum 3 alternances par bloc.

- Tissez le pilier "{pilar}" avec le thème d'intercession "{label}"
- Je Vous Salue Marie GUIDÉ (l'auditeur prie avec vous) : "Répétez avec moi : Je vous salue Marie, pleine de grâce..."
- Bloc d'intercession pour la santé (obligatoire, guidé) : "Posez la main sur l'endroit qui fait mal et dites avec moi..."
- Crochets de rétention organiques toutes les ~300 mots (le fidèle ne perçoit pas la technique) :
  • Anticipation : "Ce qui vient maintenant dans cette prière..."
  • Révélation : "Cette grâce a un nom..."
  • Validation : "Si vous ressentez quelque chose dans votre cœur en ce moment, c'est un signe que..."
  • Tournant : "Mais ce que votre Mère du Ciel veut vous dire à ce sujet est..."
{nota_miguel}

[TROIS CTAs SUBTILS — uniquement aux transitions naturelles, jamais pendant la prière]
CTA 1 (~minute 4) : "Si cette diffusion vous bénit, abonnez-vous à la chaîne pour recevoir des prières chaque jour — nous sommes une famille de foi qui prie sans cesse pour vous..."
CTA 2 (~minute 8) : "Si cette prière touche votre cœur, partagez-la avec quelqu'un qui en a besoin..."
CTA 3 (~minute 17) : "Restez, ce qui vient est pour vous..."

[CLÔTURE — dernières 3 minutes]
- Bénédiction finale comme Mère du Ciel
- Terminez en FORCE — le fidèle repart protégé, jamais désespéré
- BOUCLE SYNTAXIQUE OBLIGATOIRE : la dernière phrase est syntaxiquement incomplète
  pour s'unir à la première phrase du prochain bloc sans que l'auditeur remarque la coupure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RÈGLES ABSOLUES :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- JAMAIS de markdown, astérisques, tirets, numérotation ou titres — texte fluide uniquement
- JAMAIS de points de suspension (...) ou tiret long (—) — ils causent des pauses indésirables
- JAMAIS commencer une phrase par le mot "Prière"
- JAMAIS "Écrivez Amen dans les commentaires"
- JAMAIS mentionner d'autres chaînes ou marques
- INTEMPORALITÉ ABSOLUE : cette prière est diffusée à TOUTE heure du jour ou de la nuit.
  JAMAIS mentionner l'heure, les moments de la journée (aube, matin, midi, après-midi, soir, nuit),
  les jours de la semaine, ou les dates. Si vous avez besoin de situer le moment, dites seulement "en ce moment" ou "maintenant"
- Uniquement le texte que Notre-Dame prononce à voix haute — aucune instruction de production
- Entre 2600 et 3000 mots
"""

    modelos = MODELOS_FULL
    texto   = _chamar_gemini(prompt, modelos, max_tokens=8192)
    texto   = re.sub(r'\*+', '', texto)
    texto   = re.sub(r'#{1,6}\s+', '', texto)
    texto   = re.sub(r'^\s*[-•]\s+', '', texto, flags=re.MULTILINE)
    texto   = re.sub(r'\.{2,}', '', texto)
    texto   = re.sub(r'\s*[—–]\s*', ', ', texto)
    texto   = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)
    texto   = re.sub(r'\n{3,}', '\n\n', texto)
    texto   = re.sub(r'  +', ' ', texto)
    return texto.strip()


# ═══════════════════════════════════════════════════════════════════════
# CONTRÔLE QUALITÉ
# ═══════════════════════════════════════════════════════════════════════

def motivo_degeneracao(texto: str) -> str | None:
    palavras = texto.split()
    n = len(palavras)
    if n < 1400:
        return f"trop court ({n} mots)"
    if n > 4500:
        return f"trop long ({n} mots — probablement une boucle)"
    tri = {}
    for i in range(n - 2):
        t = (palavras[i].lower(), palavras[i + 1].lower(), palavras[i + 2].lower())
        tri[t] = tri.get(t, 0) + 1
    max_tri = max(tri.values()) if tri else 0
    if max_tri > 25:
        return f"trigramme répété {max_tri}x (boucle)"
    if texto.count(",") / max(n, 1) > 0.14:
        return "densité de virgules typique d'une liste de prénoms"
    frases = {}
    for f in re.split(r"[.!?…]+", texto):
        f = f.strip().lower()
        if len(f.split()) > 5:
            frases[f] = frases.get(f, 0) + 1
    max_frase = max(frases.values()) if frases else 0
    if max_frase >= 4:
        return f"phrase identique répétée {max_frase}x"
    return None


# ═══════════════════════════════════════════════════════════════════════
# TTS
# ═══════════════════════════════════════════════════════════════════════

async def _tts_async(texto: str, saida: Path):
    comm = edge_tts.Communicate(texto, voice=VOZ, rate=VOZ_RATE, pitch=VOZ_PITCH)
    await comm.save(str(saida))

def gerar_audio(texto: str, saida: Path):
    asyncio.run(_tts_async(texto, saida))
    print(f"  TTS FR: {saida.name} ({saida.stat().st_size // 1024} KB)")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def _gh_error(msg: str):
    linha = msg.replace("\n", " | ").replace("\r", "")[:500]
    print(f"::error::{linha}", flush=True)


def main():
    print("=" * 60)
    print("gerar_bloco_live_fr.py — Canal FR — Notre-Dame de Lourdes")
    print("=" * 60)

    DIR_BLOCOS.mkdir(parents=True, exist_ok=True)
    agora    = datetime.now(FUSO)
    contexto = calcular_contexto_sazonal(agora)
    pilar    = PILARES.get(agora.weekday(), "Prière et Intercession")
    ts_base  = agora.strftime("%Y%m%d_%H%M")

    print(f"Heure locale : {agora.strftime('%Y-%m-%d %H:%M')} (Paris)")
    print(f"Contexte liturgique : {contexto}")
    print(f"Pilier du jour : {pilar}")

    print("\n[1/3] Récupération des commentaires du canal FR...")
    yt = get_youtube_readonly()
    comentarios = buscar_comentarios_canal(yt)

    print("\n[2/3] Classification en groupes thématiques...")
    grupos = classificar_grupos(comentarios, pilar)
    print(f"  Total de blocs à générer : {len(grupos)}")

    print(f"\n[3/3] Génération des blocs FR...")
    gerados = 0
    for i, grupo in enumerate(grupos):
        label = grupo.get("label", f"Groupe {i+1}")
        print(f"\n  ── Bloc {i+1}/{len(grupos)}: {label} ──")
        try:
            num_bloco = int(agora.strftime("%j")) * MAX_GRUPOS + i + 1
            roteiro   = gerar_roteiro_grupo(grupo, contexto, pilar, agora, num_bloco)
            palavras  = len(roteiro.split())
            print(f"  Script FR : {palavras} mots")

            motivo = motivo_degeneracao(roteiro)
            if motivo:
                print(f"  [WARN] Script rejeté ({motivo}) — nouvelle tentative avec le modèle complet...")
                roteiro  = gerar_roteiro_grupo(grupo, contexto, pilar, agora, num_bloco, so_full=True)
                palavras = len(roteiro.split())
                motivo   = motivo_degeneracao(roteiro)
                if motivo:
                    print(f"  [ERROR] Rejeté à nouveau ({motivo}) — bloc rejeté")
                    continue
                print(f"  Script FR (complet) : {palavras} mots — approuvé")

            ts      = f"{ts_base}_{i+1:02d}"
            destino = DIR_BLOCOS / f"audio_{ts}.mp3"
            gerar_audio(roteiro, destino)
            gerados += 1
            print(f"  ✅ {destino.name}")

        except Exception as e:
            print(f"  [ERROR] Bloc {i+1} ({label}): {e}")
            continue

    print(f"\n{'='*60}")
    print(f"Terminé FR : {gerados}/{len(grupos)} blocs dans {DIR_BLOCOS}/")
    print(f"VPS assemble les .mp4 avec videos_base/ automatiquement.")

    if gerados == 0:
        _gh_error("Aucun bloc FR généré — tous les groupes ont échoué.")
        sys.exit(1)


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as exc:
        _gh_error(f"ÉCHEC FR: {exc}")
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
