import os, sys, json, time, re, datetime
from google.genai import Client
from google.oauth2.service_account import Credentials
import gspread
from zoneinfo import ZoneInfo
import novenas

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
    # Slot 06:00 — Novenas (novenas.py). Sem retroatividade; só a partir de novenas.ATIVACAO_06H.
    {"horario": "06:00", "personagem": "Maria", "idioma": "FR", "foco": "Morning consecration to Our Lady: protection, direction and strength for the day that begins.", "periodo": novenas.CFG["periodo"], "ativacao": novenas.ATIVACAO_06H},
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
agora_local = datetime.datetime.now(ZoneInfo(novenas.TZ))
hoje = agora_local.date()
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

def slot_exigido(v, d):
    """Travas do slot 06:00: sem retroatividade (evita upload público imediato de vídeo atrasado)."""
    if v.get("ativacao") and d < v["ativacao"]:
        return False
    if v["horario"] == "06:00":
        if d < hoje: return False
        if d == hoje and agora_local.hour >= 4: return False
        if novenas.plano_do_dia(d) is None: return False
    return True
data_alvo = None
grade_para_processar = []

data_check = limite_passado
while data_check <= meta_estoque:
    horarios_presentes = dias_existentes.get(data_check, [])
    faltando = [v for v in GRADE_DIARIA if slot_exigido(v, data_check) and v["horario"] not in horarios_presentes]
    if faltando:
        data_alvo = data_check
        grade_para_processar = faltando
        break
    data_check += datetime.timedelta(days=1)

if not data_alvo:
    print(f"✅ STOCK ATTEINT jusqu'au {meta_estoque}. Arrêt.")
    sys.exit(0)

pilar_do_dia = PILARES[data_alvo.weekday()]
contexto_sazonal = calcular_contexto_sazonal(data_alvo)
print(f"\n📅 DATE CIBLE: {data_alvo} | Pilier: {pilar_do_dia}")

esperas_exponenciais = [10, 20, 40, 80, 120]

def gerar_novena(data_alvo, plano, contexto_sazonal):
    """Linha da planilha para um dia de novena (festa ou pedido) — rito fixo em novenas.py."""
    C = novenas.CFG
    n = plano["dia"]
    categoria = None
    if plano["tipo"] == "festa":
        f = plano["festa"]
        invocacao = f["invocacao"]
        contexto = (f"This is the '{f['nome']}', preparing for: {f['festa']}. Today is day {n} of 9. "
                    f"INTENTION OF THE DAY (the believer's pain): {novenas.INTENCOES_FESTA[n - 1]}.")
    else:
        categoria = novenas.escolher_tema_pedido(gc.open_by_key(ID_PLANILHA), plano["ciclo_inicio"])
        rotulo, descr = novenas.CATEGORIAS[categoria]
        invocacao = C["invocacao_padrao"]
        contexto = (f"This is the '{rotulo}', a 9-day petition novena to Our Lady ({invocacao}). "
                    f"Single theme of the novena: {descr}. Today is day {n} of 9. {novenas.PROGRESSAO_PEDIDO[n]}")
    if data_alvo.weekday() == 4:
        contexto += " TODAY IS FRIDAY: gently touch on Mercy and Forgiveness."
    if contexto_sazonal:
        contexto += f" Season/feast context: {contexto_sazonal}."
    cta_final = ("Invite them to pray the complete novena in the channel playlist and to keep praying with us live 24 hours."
                 if n == 9 else "Invite them to come back tomorrow morning for the next day of the novena (never say an exact hour).")
    prompt = f"""
    You are an empathetic Catholic spiritual guide, faithful to Church doctrine. Write ONLY the VARIABLE parts of a NOVENA video addressed to {invocacao}.
    WRITE EVERYTHING IN {novenas.LANG_NAME}. Natural, native, devotional language — never translated-sounding.
    The fixed rite (sign of the cross, act of contrition, novena prayer, Our Father, Hail Mary, Glory Be) is ALREADY inserted by the system — DO NOT write those prayers.
    CONTEXT: {contexto}
    Time of day: "{C['periodo']}".

    RULES:
    1. GANCHO (120-180 words) — HOOK 3A: (a) EMPATHIC STATEMENT about the pain of the day's intention, NO direct questions; (b) sensory setting of the morning that begins; (c) announce that today is day {n} of the novena and that {invocacao} has a grace for whoever stays until the end.
    2. REFLEXAO (450-600 words): a short Bible passage (cite book and chapter) linked to the intention, and a warm meditation. Include 1 invisible retention hook (anticipation or partial revelation) without breaking the devotional mood.
    3. SUPLICA (350-500 words): personal first-person supplication for the day's intention; MUST include a block of intercession for health (the sick in the family, physical and emotional healing). Arc: vulnerability → intercession → trust.
    4. ENCERRAMENTO (120-180 words): end in STRENGTH and confidence, never in pleading. {cta_final} Also {C['cta_pista']}. FORBIDDEN: "type Amen" style forced engagement.
    5. PROMESSA (max 40 characters): complement of the title, which already starts with the novena name and the day. Do NOT repeat the novena name. {'Focus on the intention of the day.' if plano['tipo'] == 'festa' else C['promessa_regra']} No quotes, no emoji, no date.
    6. NEVER mention exact hours. Use many ellipses (...) for voice pauses. PLAIN TEXT: no JSON, no asterisks, no brackets, no section titles inside the texts.
    7. FORBIDDEN to mention any saint or devotion other than Our Lady, Jesus and God the Father.

    EXACT FORMAT (keep these English labels, in this order; content in {novenas.LANG_NAME}):
    PROMESSA: ...
    GANCHO: ...
    REFLEXAO: ...
    SUPLICA: ...
    ENCERRAMENTO: ...
    DESC: [3 SEO paragraphs: 1st "Novena — {n}/9" + invitation to the 24h live; 2nd emotional description of the day's intention; 3rd keywords and hashtags including #novena]
    TAGS: [comma-separated tags including the word for novena]
    """
    rotulos = ["PROMESSA", "GANCHO", "REFLEXAO", "SUPLICA", "ENCERRAMENTO", "DESC", "TAGS"]
    def _lab(r): return r"(?:^|\n)[ \t>*_#]*" + r + r"[ \t*_]*:"
    padrao_fim = "|".join(_lab(r) for r in rotulos)
    for i in range(5):
        try:
            texto = _gerar(modelos_cascata[i], prompt)
        except Exception as e:
            print(f"   ⚠️ Gemini: {e}"); time.sleep(esperas_exponenciais[i]); continue
        t = texto.replace("REFLEXÃO", "REFLEXAO").replace("SÚPLICA", "SUPLICA")
        partes = {}
        for r in rotulos:
            m = re.search(_lab(r) + r"\s*(.*?)(?=(?:" + padrao_fim + r")|\Z)", t, re.IGNORECASE | re.DOTALL)
            partes[r] = re.sub(r'[*#\[\]{}]', '', m.group(1)).strip() if m else ""
        palavras = sum(len(partes[k].split()) for k in ["GANCHO", "REFLEXAO", "SUPLICA", "ENCERRAMENTO"])
        if all(partes[k] for k in ["GANCHO", "REFLEXAO", "SUPLICA", "ENCERRAMENTO"]) and palavras >= 700:
            break
        print(f"   ⚠️ Resposta incompleta ({palavras} palavras). Nova tentativa...")
        time.sleep(esperas_exponenciais[i])
    else:
        print("   ❌ Novena não gerada nesta execução — o scanner tenta de novo na próxima.")
        return None
    promessa = partes["PROMESSA"].replace('"', '').strip()[:45]
    titulo = novenas.montar_titulo(plano, promessa, categoria, data_alvo)
    roteiro = novenas.montar_roteiro(plano, partes["GANCHO"], partes["REFLEXAO"], partes["SUPLICA"], partes["ENCERRAMENTO"])
    return [str(data_alvo), "06:00", novenas.STATUS_PRONTO, "MARIA", "FR", novenas.tema_codificado(plano, categoria), titulo, roteiro,
            partes["TAGS"] or "novena", partes["DESC"] or f"Novena {n}/9", "Pending", novenas.texto_thumb(plano)]


for video in grade_para_processar:
    horario, persona, idioma, foco_teologico, periodo = video["horario"], video["personagem"].upper(), video["idioma"], video["foco"], video["periodo"]
    print(f"🎬 PRODUCTION: {horario} | {persona}")

    if horario == "06:00":
        plano = novenas.plano_do_dia(data_alvo)
        if plano and plano["tipo"] in ("festa", "pedido"):
            nova_linha = gerar_novena(data_alvo, plano, contexto_sazonal)
            if nova_linha:
                try:
                    aba.update(values=[nova_linha], range_name=f"A{proxima_linha_vazia}:L{proxima_linha_vazia}")
                    print(f"   ✅ NOVENA salva na linha {proxima_linha_vazia}: {nova_linha[6]}")
                    proxima_linha_vazia += 1
                    time.sleep(5)
                except Exception as e: print(f"   ❌ Falha ao salvar novena: {e}")
            continue
        print(f"   ☀️ Slot 06:00 avulso ({plano.get('motivo') if plano else '-'})")

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
