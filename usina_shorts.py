import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread

CHAVE_API = os.environ.get("GEMINI_API_KEY")
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_FR")

print("🔐 Authentification Google Sheets (SHORTS FR)...")
credenciais_dict = json.loads(GOOGLE_JSON)
escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
gc = gspread.authorize(credenciais)

client = Client(api_key=CHAVE_API, http_options={'api_version': 'v1'})

def obter_modelo_lite():
    try:
        modelos = client.models.list()
        lite_models = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods and ('flash-lite' in m.name or '8b' in m.name)]
        return sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-2.5-flash-lite'
    except:
        return 'gemini-2.5-flash-lite'

modelo_usina = obter_modelo_lite()

ID_PLANILHA = "1KgIjWrLUVlllhlZB1R9fkHGxxZlLsax1aOVGZrYwgnU"
PILARES = {
    0: "Guerre spirituelle et protection divine",
    1: "Libération des addictions et des liens",
    2: "Restauration de la famille et du mariage",
    3: "Providence divine et portes ouvertes",
    4: "Miséricorde divine et guérison physique",
    5: "Le manteau de Notre-Dame",
    6: "Miracles et gratitude"
}
GRADE_SHORTS = [
    {"horario": "06:00", "personagem": "Maria", "idioma": "FR",
     "foco": "Matin: Sous le manteau de Notre-Dame, commence ta journée avec un miracle.", "ref": "18:00"},
    {"horario": "14:00", "personagem": "Maria", "idioma": "FR",
     "foco": "Après-midi: Intercession, guérison et miracles.", "ref": "18:00"}
]

aba_shorts = gc.open_by_key(ID_PLANILHA).worksheet("FR_SHORTS")
aba_longos = gc.open_by_key(ID_PLANILHA).worksheet("FR")

todas_linhas = aba_shorts.get_all_values()
if len(todas_linhas) > 500:
    aba_shorts.delete_rows(2, 100)
    todas_linhas = aba_shorts.get_all_values()

proxima_linha_vazia = len(todas_linhas) + 1
valores_coluna_a = [linha[0].strip() for linha in todas_linhas[1:] if len(linha) > 0]
valores_coluna_b = [linha[1].strip() for linha in todas_linhas[1:] if len(linha) > 1]

dias_existentes = {}
hoje = datetime.date.today()
limite_passado = hoje - datetime.timedelta(days=2)

for d_str, h_str in zip(valores_coluna_a, valores_coluna_b):
    if d_str and h_str:
        try:
            d_obj = datetime.datetime.strptime(d_str, '%Y-%m-%d').date()
            if d_obj >= limite_passado:
                if d_obj not in dias_existentes: dias_existentes[d_obj] = []
                dias_existentes[d_obj].append(h_str)
        except: pass

meta_estoque = hoje + datetime.timedelta(days=5)

gaps = []
data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    horarios_faltando = [v for v in GRADE_SHORTS if v["horario"] not in horarios_presentes]
    if horarios_faltando:
        gaps.append((data_check, horarios_faltando))
    data_check += datetime.timedelta(days=1)

if not gaps:
    print(f"✅ STOCK SHORTS ATTEINT jusqu'au {meta_estoque}. Arrêt.")
    sys.exit(0)

dados_longos = aba_longos.get_all_values()

for data_alvo, grade_para_processar in gaps:
    pilar_do_dia = PILARES[data_alvo.weekday()]
    print(f"\n📅 DATE CIBLE SHORTS: {data_alvo} | Pilier: {pilar_do_dia}")
    for video in grade_para_processar:
        horario, persona, idioma, foco_teologico = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"]
        print(f"🎬 PRODUCTION SHORT: {horario} | {persona}")

        horario_longo_ref = video["ref"]
        titulo_referencia = ""
        for linha in dados_longos[1:]:
            if len(linha) > 6 and linha[0].strip() == str(data_alvo) and linha[1].strip() == horario_longo_ref:
                titulo_referencia = linha[6].strip()
                break

        contexto_eco = f"La vidéo longue correspondante d'aujourd'hui a le titre: '{titulo_referencia}'. Le Short DOIT être un écho de ce thème." if titulo_referencia else ""

        persona_prompt = "la Vierge Marie, Notre-Dame de Lourdes"

        oracao_padrao = "Je vous salue Marie, pleine de grâces... le Seigneur est avec vous... vous êtes bénie entre toutes les femmes... et Jésus, le fruit de vos entrailles, est béni... Sainte Marie, Mère de Dieu... priez pour nous pauvres pécheurs... maintenant et à l'heure de notre mort... Amen."

        prompt_principal = f"""
        Agis comme un guide spirituel catholique. Crée un script pour une vidéo YouTube SHORT (maximum 35 secondes de parole).
        Thème du jour: {pilar_do_dia}. Focus: {foco_teologico}. Adressé à: {persona_prompt}.
        {contexto_eco}

        STRUCTURE DU SCRIPT OBLIGATOIRE (BOUCLE PARFAITE):
        1. HOOK (Début): La première phrase de la vidéo. OBLIGATOIRE de commencer par des points de suspension en minuscules ("..."). C'est le COMPLÉMENT SYNTAXIQUE de la phrase finale — ensemble elles forment une phrase unique, continue et complète.
        2. PRIÈRE: Écris EXACTEMENT cette prière: "{oracao_padrao}"
        3. PHRASE DE BOUCLE (Fin): La dernière phrase de la vidéo. OBLIGATOIRE de se terminer par des points de suspension ("..."). Elle doit être SYNTAXIQUEMENT INCOMPLÈTE — une proposition ouverte dont le complément naturel est exactement la phrase d'ouverture.

        RÈGLES DE FLUIDITÉ:
        - Écris des phrases fluides et naturelles. Utilise des points de suspension (...) pour les pauses respiratoires.
        - Le titre doit commencer par "Prière rapide : " suivi du thème, et se terminer par le hashtag #Shorts.
        - PAS de marqueurs temporels, PAS d'astérisques, PAS d'emojis dans le script.

        FORMAT EXACT:
        TITRE: [Prière rapide : Thème - #Shorts]
        SCRIPT: [Script complet avec l'effet de boucle]
        DESC: [Courte description invitant les spectateurs à visiter la chaîne et les playlists]
        TAGS: [Tags séparés par des virgules]
        """

        texto_ia = None
        for tentativa in range(3):
            try:
                texto_ia = client.models.generate_content(model=modelo_usina, contents=prompt_principal).text
                break
            except Exception as gemini_err: print(f"   ⚠️ Erreur Gemini (tentative {tentativa+1}/3): {gemini_err}"); time.sleep(10)

        if not texto_ia: continue

        try:
            t_match = re.search(r'TITRE:\s*(.*?)(?=SCRIPT:|DESC:|TAGS:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
            g_match = re.search(r'SCRIPT:\s*(.*?)(?=DESC:|TAGS:|TITRE:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
            d_match = re.search(r'DESC:\s*(.*?)(?=TAGS:|TITRE:|SCRIPT:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
            tg_match = re.search(r'TAGS:\s*(.*?)(?=TITRE:|SCRIPT:|DESC:|$)', texto_ia, re.IGNORECASE | re.DOTALL)

            titulo_final = re.sub(r'[*"\[\]]', '', t_match.group(1)).strip() if t_match else "Prière rapide #Shorts"
            roteiro_final = g_match.group(1).strip() if g_match else texto_ia
            desc_final = d_match.group(1).strip() if d_match else "Regardez la prière complète sur notre chaîne!"
            tags_final = re.sub(r'[*\[\]]', '', tg_match.group(1)).strip() if tg_match else "shorts, prière, foi"

            nova_linha = [str(data_alvo), horario, "Ready for Audio", persona, idioma, pilar_do_dia, titulo_final, roteiro_final, tags_final, desc_final, "N/A", "N/A"]
            aba_shorts.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
            print(f"   ✅ SUCCÈS! Ligne Short {proxima_linha_vazia} remplie.")
            proxima_linha_vazia += 1
            time.sleep(3)
        except Exception as e: print(f"   ❌ Échec de l'enregistrement: {e}")
