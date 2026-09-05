import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread

CHAVE_API = os.environ.get("GEMINI_API_KEY")
CHAVE_API_2 = os.environ.get("GEMINI_API_KEY_2", "")
CHAVES_GEMINI = [k for k in [CHAVE_API, CHAVE_API_2] if k]
GOOGLE_JSON = os.environ.get("GOOGLE_CREDENTIALS_FR")

print("🔐 Authentification Google Sheets (Service Account FR)...")
credenciais_dict = json.loads(GOOGLE_JSON)
escopos = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
gc = gspread.authorize(credenciais)

client = Client(api_key=CHAVE_API, http_options={'api_version': 'v1'})

def obter_cascata_de_modelos():
    try:
        modelos_disponiveis = client.models.list()
        lite_models = [m.name for m in modelos_disponiveis if 'generateContent' in m.supported_generation_methods and 'flash' in m.name and ('lite' in m.name or '8b' in m.name)]
        flash_models = [m.name for m in modelos_disponiveis if 'generateContent' in m.supported_generation_methods and 'flash' in m.name and 'lite' not in m.name and '8b' not in m.name]
        melhor_lite = sorted(lite_models, reverse=True)[0] if lite_models else 'gemini-3.5-flash-lite'
        melhor_flash = sorted(flash_models, reverse=True)[0] if flash_models else 'gemini-2.5-flash'
        return [melhor_lite, melhor_lite, melhor_lite, melhor_lite, melhor_flash]
    except:
        return ['gemini-3.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-2.5-flash']

modelos_cascata = obter_cascata_de_modelos()

def _gerar(modelo, prompt):
    for chave in CHAVES_GEMINI:
        try:
            c = Client(api_key=chave, http_options={'api_version': 'v1'})
            return c.models.generate_content(model=modelo, contents=prompt).text
        except Exception as e:
            if "429" in str(e) and chave != CHAVES_GEMINI[-1]:
                print(f"[WARN] 429 sur la clé ...{chave[-6:]}. Essai avec clé 2...")
                continue
            raise
    raise RuntimeError("Toutes les clés Gemini ont échoué.")

def calcular_contexto_sazonal(data_alvo):
    ano = data_alvo.year
    a = ano % 19; b = ano // 100; c = ano % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mes = (h + l - 7 * m + 114) // 31; dia = ((h + l - 7 * m + 114) % 31) + 1
    easter = datetime.date(ano, mes, dia)

    ash_wednesday = easter - datetime.timedelta(days=46)
    good_friday = easter - datetime.timedelta(days=2)
    pentecost = easter + datetime.timedelta(days=49)
    corpus_christi = easter + datetime.timedelta(days=60)

    may_1 = datetime.date(ano, 5, 1)
    mothers_day = may_1 + datetime.timedelta(days=(6 - may_1.weekday() + 7) % 7 + 7)

    if data_alvo == easter: return "AUJOURD'HUI C'EST LE DIMANCHE DE PÂQUES."
    if data_alvo == ash_wednesday: return "AUJOURD'HUI C'EST LE MERCREDI DES CENDRES."
    if data_alvo == good_friday: return "AUJOURD'HUI C'EST LE VENDREDI SAINT."
    if data_alvo == pentecost: return "AUJOURD'HUI C'EST LE DIMANCHE DE PENTECÔTE."
    if data_alvo == corpus_christi: return "AUJOURD'HUI C'EST LA FÊTE DU CORPUS CHRISTI."
    if data_alvo == mothers_day: return "AUJOURD'HUI C'EST LA FÊTE DES MÈRES."
    if data_alvo.month == 8 and data_alvo.day == 15: return "AUJOURD'HUI C'EST LA FÊTE DE L'ASSOMPTION DE MARIE."
    if data_alvo.month == 11 and data_alvo.day == 1: return "AUJOURD'HUI C'EST LA TOUSSAINT."
    if data_alvo.month == 11 and data_alvo.day == 2: return "AUJOURD'HUI C'EST LA FÊTE DES FIDÈLES DÉFUNTS."
    if data_alvo.month == 12 and data_alvo.day == 8: return "AUJOURD'HUI C'EST LA FÊTE DE L'IMMACULÉE CONCEPTION."
    if data_alvo.month == 12 and data_alvo.day == 25: return "AUJOURD'HUI C'EST NOËL."
    if data_alvo.month == 12 and data_alvo.day == 31: return "AUJOURD'HUI C'EST LA SAINT-SYLVESTRE."
    if data_alvo.month == 1 and data_alvo.day == 1: return "AUJOURD'HUI C'EST LE JOUR DE L'AN."
    return ""

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
GRADE_DIARIA = [
    {"horario": "18:00", "personagem": "Maria", "idioma": "FR",
     "foco": "Soirée: Prière mariale de protection, guérison, libération et repos de la nuit.",
     "periodo": "ce soir"}
]

aba = gc.open_by_key(ID_PLANILHA).worksheet("FR")

todas_linhas = aba.get_all_values()
if len(todas_linhas) > 500:
    aba.delete_rows(2, 100)
    todas_linhas = aba.get_all_values()

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
data_alvo = None
grade_para_processar = []

data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    if len(horarios_presentes) < len(GRADE_DIARIA):
        data_alvo = data_check
        grade_para_processar = [v for v in GRADE_DIARIA if v["horario"] not in horarios_presentes]
        break
    data_check += datetime.timedelta(days=1)

if not data_alvo:
    print(f"✅ STOCK ATTEINT jusqu'au {meta_estoque}. Arrêt.")
    sys.exit(0)

pilar_do_dia = PILARES[data_alvo.weekday()]
contexto_sazonal = calcular_contexto_sazonal(data_alvo)
print(f"\n📅 DATE CIBLE: {data_alvo} | Pilier: {pilar_do_dia}")

esperas_exponenciais = [10, 20, 40, 80, 120]

for video in grade_para_processar:
    horario, persona, idioma, foco_teologico, periodo = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"], video["periodo"]
    print(f"🎬 PRODUCTION: {horario} | {persona}")

    persona_prompt = "la Vierge Marie, Notre-Dame de Lourdes"

    prompt_tema = f"Agis comme un Théologien. Crée un thème court (max 8 mots) pour une prière. Pilier: '{pilar_do_dia}', adressé à '{persona_prompt}', moment: '{foco_teologico}'. Saisonnalité: '{contexto_sazonal}'. UNIQUEMENT le thème, sans guillemets ni astérisques."
    tema_gerado = None
    for i in range(5):
        try:
            tema_gerado = _gerar(modelos_cascata[i], prompt_tema).replace('*', '').replace('"', '').replace('[', '').replace(']', '').strip()
            break
        except Exception as gemini_err: print(f"   ⚠️ Erreur Gemini (tentative {i+1}/5): {gemini_err}"); time.sleep(esperas_exponenciais[i])

    if not tema_gerado: continue
    time.sleep(5)

    regra_meditacao = "OBLIGATOIRE: Dans la description (DESC), ajoute une mention que la fin de la vidéo contient 5 minutes de musique céleste pour dormir/méditer."
    cta_comentarios = "À la fin, demande à l'auditeur d'écrire une raison de gratitude dans les commentaires."

    instrucao_titulo = "TITRE:[Titre magnétique. OBLIGATOIRE de commencer par 'Notre-Dame' ou 'la Vierge Marie'. FORMAT: 'Notre-Dame [douleur du croyant] [promesse urgente]'. Ex: 'Notre-Dame guérit votre famille ce soir'. PAS DE DATE. PAS D'ASTÉRISQUES NI DE CROCHETS]"

    prompt_principal = f"""
    Agis comme un guide spirituel empathique et un frère dans la foi. Écris une prière extensive de 1500 à 1800 mots sur "{tema_gerado}" adressée à {persona_prompt}.
    CONTEXTE: Moment de la journée: "{periodo}". Focus: "{foco_teologico}". Saisonnalité: "{contexto_sazonal}".

    RÈGLES DE RÉTENTION ET COPYWRITING (TRÈS IMPORTANT):
    1. FORMULE DU TITRE: Suis EXACTEMENT le format ci-dessous. Pour Notre-Dame: OBLIGATOIRE de commencer par 'Notre-Dame' ou 'la Vierge Marie'. Il est STRICTEMENT INTERDIT de commencer par le mot 'Prière'.
    2. FORMULE THUMB: Maximum 4 mots. DOIT être un déclencheur d'urgence connecté au thème (Ex: "MIRACLE URGENT AUJOURD'HUI", "SAUVEZ VOTRE FAMILLE", "FIN DE L'ANXIÉTÉ").
    3. LA RÈGLE DES 15 SECONDES (HOOK 3A): Le début du script DOIT avoir 3 blocs rapides:
       - Attention (0-5s): Une AFFIRMATION EMPATHIQUE sur la douleur du croyant. (INTERDIT d'utiliser des questions directes).
       - Cadre sensoriel (5-10s): Connecte la douleur avec la scène de {periodo}.
       - Autorité/Agenda (10-15s): Dis que {persona_prompt} a une parole de libération et demande de rester jusqu'à la fin.
    4. CTA IMMÉDIAT: {cta_comentarios}
    5. RÉINITIALISATION DE L'ATTENTION (MI-VIDÉO): Exactement au milieu du script, insère une phrase parlée pour reconnecter l'auditeur.
    6. CROCHETS DE RÉTENTION INVISIBLES: Toutes les 300 à 400 mots, incorpore organiquement — sans que le croyant perçoive la technique — l'un des suivants: (a) ANTICIPATION; (b) RÉVÉLATION PARTIELLE; (c) VALIDATION ÉMOTIONNELLE; (d) CHANGEMENT DE BLOC. Les crochets doivent être invisibles.

    RÈGLES GÉNÉRALES:
    7. INTERDIT DE MENTIONNER DES HEURES EXACTES: Utilise seulement "{periodo}".
    8. PAUSES: OBLIGATOIRE d'utiliser des points de suspension (...) abondants pour forcer les pauses dans la voix IA.
    9. ANTI-JSON: Écris en TEXTE BRUT. INTERDIT JSON, accolades {{ }} ou astérisques (*).
    OBLIGATOIRE: Comme tu t'adresses à Marie, tu DOIS utiliser les invocations 'Notre-Dame de Lourdes', 'Vierge Marie' ou 'Notre-Dame'.
    {regra_meditacao}

    FORMAT EXACT:
    {instrucao_titulo}
    THUMB: [Déclencheur d'urgence — Max 4 mots]
    SCRIPT: [Prière complète de 1500 à 1800 mots]
    DESC: [Description de 3 paragraphes avec fort SEO. PREMIER paragraphe: invite à la LIVE 24h de la chaîne ('Bientôt: priez en direct 24h/24 avec nous — activez la cloche pour ne manquer aucune prière'). DEUXIÈME paragraphe: description émotionnelle de cette prière. TROISIÈME paragraphe: mots-clés et hashtags.]
    TAGS: [Tags séparés par des virgules]
    """

    texto_ia = None
    for i in range(5):
        try:
            texto_ia = _gerar(modelos_cascata[i], prompt_principal)
            break
        except Exception as gemini_err: print(f"   ⚠️ Erreur Gemini (tentative {i+1}/5): {gemini_err}"); time.sleep(esperas_exponenciais[i])

    if not texto_ia: continue

    try:
        t_match = re.search(r'TITRE:\s*(.*?)(?=THUMB:|SCRIPT:|DESC:|TAGS:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        th_match = re.search(r'THUMB:\s*(.*?)(?=SCRIPT:|DESC:|TAGS:|TITRE:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        g_match = re.search(r'SCRIPT:\s*(.*?)(?=DESC:|TAGS:|TITRE:|THUMB:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        d_match = re.search(r'DESC:\s*(.*?)(?=TAGS:|TITRE:|THUMB:|SCRIPT:|$)', texto_ia, re.IGNORECASE | re.DOTALL)
        tg_match = re.search(r'TAGS:\s*(.*?)(?=TITRE:|THUMB:|SCRIPT:|DESC:|$)', texto_ia, re.IGNORECASE | re.DOTALL)

        titulo_final = re.sub(r'[*"\[\]]', '', t_match.group(1)).strip() if t_match else "Prière puissante"
        thumb_final = re.sub(r'[*"\[\]]', '', th_match.group(1)).strip() if th_match else "MIRACLE AUJOURD'HUI"
        roteiro_final = g_match.group(1).strip() if g_match else texto_ia
        desc_final = d_match.group(1).strip() if d_match else "Prière quotidienne."
        tags_final = re.sub(r'[*\[\]]', '', tg_match.group(1)).strip() if tg_match else "prière, foi, protection"

        nova_linha = [str(data_alvo), horario, "Ready for Audio", persona, idioma, tema_gerado, titulo_final, roteiro_final, tags_final, desc_final, "Pending", thumb_final]
        aba.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
        print(f"   ✅ SUCCÈS! Ligne {proxima_linha_vazia} remplie.")
        proxima_linha_vazia += 1
        time.sleep(5)
    except Exception as e: print(f"   ❌ Échec de l'enregistrement: {e}")
