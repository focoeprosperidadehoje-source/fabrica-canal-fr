# -*- coding: utf-8 -*-
"""novenas.py — Slot 06:00 (Novenas) — gerado a partir do padrão do PT (aprovado por Leandro em 2026-09-25). Somente personas marianas do canal."""
import datetime

CFG = {
 "canal": "FR", "tz": "Europe/Paris", "lang_name": "French (français)",
 "ativacao": datetime.date(2026, 9, 30), "epoca_pedidos": datetime.date(2026, 9, 30),
 "status_pronto": "Ready for Audio", "invocacao_padrao": "Notre-Dame de Lourdes",
 "promessa_regra": 'MUST start with "Notre-Dame". Ex: "Notre-Dame Guérit Ton Foyer", "Notre-Dame Ouvre les Portes".',
 "festas": [
   {"id": "lourdes", "inicio": (2, 2), "nome": "Neuvaine à Notre-Dame de Lourdes", "invocacao": "Notre-Dame de Lourdes",
    "festa": "Fête de Notre-Dame de Lourdes (11 février)"},
   {"id": "assomption", "inicio": (8, 6), "nome": "Neuvaine de l'Assomption", "invocacao": "Vierge Marie, élevée au Ciel",
    "festa": "Solennité de l'Assomption de la Vierge Marie (15 août)"},
   {"id": "immaculee", "inicio": (11, 29), "nome": "Neuvaine à l'Immaculée Conception", "invocacao": "Marie Immaculée",
    "festa": "Solennité de l'Immaculée Conception (8 décembre)"},
   {"id": "noel", "inicio": (12, 16), "nome": "Neuvaine de Noël avec la Vierge Marie", "invocacao": "Vierge Marie",
    "festa": "Noël (25 décembre) — Marie, la Mère qui attend l'Enfant Jésus"},
 ],
 "intencoes_festa": ["la guérison des maladies et la santé de ceux que tu aimes", "l'unité et la restauration de ta famille",
   "la réconciliation, le pardon et la paix", "la libération des addictions et de toutes les chaînes", "la protection et l'avenir de tes enfants",
   "le travail, la subsistance et les portes ouvertes", "la protection spirituelle de ton foyer contre tout mal",
   "les causes impossibles et désespérées", "la gratitude pour les grâces reçues et la consécration à Marie"],
 "categorias": {
   "saude": ("Neuvaine pour la Guérison et la Santé", "maladies, santé physique, traitements et opérations"),
   "familia": ("Neuvaine pour la Restauration de la Famille", "disputes, éloignement et restauration de la famille et du couple"),
   "emprego": ("Neuvaine pour Trouver un Travail", "chômage, travail, subsistance et portes ouvertes"),
   "dividas": ("Neuvaine pour Sortir des Dettes", "dettes, difficultés financières et providence divine"),
   "filhos": ("Neuvaine pour les Enfants", "protection, chemin et conversion des enfants"),
   "vicios": ("Neuvaine de Libération des Addictions", "addictions, dépendances et chaînes de ceux que nous aimons"),
   "ansiedade": ("Neuvaine pour Vaincre l'Angoisse", "anxiété, angoisse, tristesse profonde et paix intérieure"),
   "protecao": ("Neuvaine de Protection Spirituelle", "protection contre le mal, la jalousie et les attaques spirituelles"),
   "causas": ("Neuvaine pour les Causes Impossibles", "causes impossibles, urgentes et désespérées"),
   "luto": ("Neuvaine de Consolation dans le Deuil", "deuil, manque et consolation après la perte d'un proche")},
 "meses": ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
 "completa": "(Complète)", "dia_label": "Jour {n}", "thumb_fmt": "NEUVAINE JOUR {n}",
 "data_no_titulo_festa": False, "data_fmt": "",
 "periodo": "ce matin",
 "desc_link": "📿 Priez la neuvaine complète, jour après jour : {url}",
 "cap_titulo": "⏱️ Chapitres de la neuvaine :",
 "cap": ["Ouverture et intention du jour", "Méditation de la Parole", "Prière de la neuvaine", "Supplication du jour", "Notre Père, Je vous salue Marie et Gloire au Père", "Conclusion et bénédiction"],
 "sinal_da_cruz": "Au nom du Père... et du Fils... et du Saint-Esprit... Amen...",
 "ato_contricao": ("Prions ensemble l'acte de contrition... Mon Dieu... j'ai un très grand regret de vous avoir offensé... "
   "parce que vous êtes infiniment bon, infiniment aimable... et que le péché vous déplaît... "
   "Je prends la ferme résolution, avec le secours de votre sainte grâce... de ne plus vous offenser et de faire pénitence... Amen..."),
 "pai_nosso": ("Notre Père, qui es aux cieux... que ton nom soit sanctifié... que ton règne vienne... que ta volonté soit faite sur la terre comme au ciel... "
   "Donne-nous aujourd'hui notre pain de ce jour... Pardonne-nous nos offenses... comme nous pardonnons aussi à ceux qui nous ont offensés... "
   "Et ne nous laisse pas entrer en tentation... mais délivre-nous du Mal... Amen..."),
 "ave_maria": ("Je vous salue, Marie, pleine de grâce... le Seigneur est avec vous... Vous êtes bénie entre toutes les femmes... "
   "et Jésus, le fruit de vos entrailles, est béni... Sainte Marie, Mère de Dieu... priez pour nous, pauvres pécheurs... maintenant et à l'heure de notre mort... Amen..."),
 "gloria": "Gloire au Père... et au Fils... et au Saint-Esprit... comme il était au commencement, maintenant et toujours, et dans les siècles des siècles... Amen...",
 "oracoes_festa": {
   "lourdes": ("Prions maintenant la prière de cette neuvaine... Ô Notre-Dame de Lourdes... qui es apparue à Bernadette dans la grotte de Massabielle... "
     "et qui as dit : Je suis l'Immaculée Conception... viens aujourd'hui dans ma vie... Regarde mes douleurs... les besoins de ma famille... "
     "et tout ce que je ne peux pas porter seul... En ce jour de ta neuvaine je te confie mon intention... "
     "Couvre-moi de ton manteau... protège mon foyer... guéris ce qui est blessé... et conduis-moi toujours plus près de Jésus... Amen..."),
   "noel": ("Prions maintenant la prière de cette neuvaine... Ô Marie... Mère de l'espérance... "
     "toi qui gardais dans ton cœur l'Enfant qui allait naître... prépare aussi mon cœur à accueillir Jésus en ce Noël... "
     "En ce jour de la neuvaine je te confie mon intention et ma famille... que la lumière de Bethléem entre dans notre maison... et apporte la paix... la guérison... et l'unité... Amen...")},
 "oracao_festa_generica": ("Prions maintenant la prière de cette neuvaine... Ô {inv}... regarde mon cœur fatigué... "
   "Toi qui as dit oui au dessein de Dieu... apprends-moi à faire confiance comme tu as fait confiance... "
   "En ce jour de ta neuvaine je te confie mon intention... Purifie ma vie... éloigne de moi tout mal... et présente ma prière à ton Fils Jésus... Amen..."),
 "oracao_pedido": ("Prions maintenant la prière de cette neuvaine... Ô Notre-Dame de Lourdes... Mère de Dieu et notre Mère... "
   "en cette neuvaine je viens à tes pieds avec une demande qui pèse sur mon cœur... Tu connais ma douleur... avant même que je la dise... "
   "En ce jour de la neuvaine je te confie mon intention... et je te demande de la porter à ton Fils Jésus... comme tu as porté le besoin des mariés à Cana... "
   "Que la volonté de Dieu soit faite... et que j'aie la force d'attendre avec foi... Amen..."),
 "jaculatoria": "{inv}... priez pour nous...",
 "cta_pista": "invite them to write in the comments their intention or the name of the person they entrust to Notre-Dame de Lourdes, because these intentions are prayed in our 24-hour live stream",
}

# ─────────────────────── MOTOR (idêntico em todos os canais) ───────────────────────
import datetime

CANAL = CFG["canal"]
TZ = CFG["tz"]
ATIVACAO_06H = CFG["ativacao"]
EPOCA_PEDIDOS = CFG["epoca_pedidos"]
FESTAS = CFG["festas"]
INTENCOES_FESTA = CFG["intencoes_festa"]
CATEGORIAS = CFG["categorias"]
ROTACAO_FALLBACK = ["saude", "familia", "emprego", "ansiedade", "filhos", "protecao", "vicios", "dividas", "causas", "luto"]
JANELA_ANTI_REPETICAO = 3
MIN_COMENTARIOS_RANKING = 5
STATUS_PRONTO = CFG["status_pronto"]
LANG_NAME = CFG["lang_name"]
PROGRESSAO_PEDIDO = {
    1: "Day of SURRENDER: present the pain honestly and open the heart.",
    2: "Day of SURRENDER: admit what we cannot carry alone.",
    3: "Day of SURRENDER: forgive and let go of what weighs, to receive grace.",
    4: "Day of PERSEVERANCE: keep faith even when nothing seems to change.",
    5: "Day of PERSEVERANCE: the strength of Mary at the foot of the cross.",
    6: "Day of PERSEVERANCE: fight discouragement and the voice of fear.",
    7: "Day of TRUST: signs that grace is already on its way.",
    8: "Day of TRUST: give thanks in advance for what God will do.",
    9: "Day of GRATITUDE and CONSECRATION: entrust life and the cause to Our Lady.",
}
ABA_NOVENAS = "NOVENAS"
ABA_TEMAS = "TEMAS_COMENTARIOS"


def _festas_do_ano(ano):
    out = []
    for f in FESTAS:
        ini = datetime.date(ano, f["inicio"][0], f["inicio"][1])
        out.append((ini, ini + datetime.timedelta(days=8), ini + datetime.timedelta(days=9), f))
    return sorted(out, key=lambda x: x[0])


def _festa_em(d):
    for ano in (d.year - 1, d.year):
        for ini, fim, dia_festa, f in _festas_do_ano(ano):
            if ini <= d <= fim:
                return ("festa", f, (d - ini).days + 1, ini)
            if d == dia_festa:
                return ("dia_festa", f, None, ini)
    return None


def _proxima_festa_inicio(d):
    for ano in (d.year, d.year + 1):
        for ini, _, _, _ in _festas_do_ano(ano):
            if ini >= d:
                return ini
    return None


def plano_do_dia(d):
    if d < ATIVACAO_06H:
        return None
    fe = _festa_em(d)
    if fe:
        tipo, f, n, ini = fe
        if tipo == "festa":
            return {"tipo": "festa", "dia": n, "festa": f, "ciclo_inicio": ini}
        return {"tipo": "avulsa", "motivo": f"dia da festa ({f['id']})"}
    if d < EPOCA_PEDIDOS:
        return {"tipo": "avulsa", "motivo": "antes da época de pedidos"}
    cursor = EPOCA_PEDIDOS
    guard = 0
    while cursor <= d and guard < 2000:
        guard += 1
        fe_c = _festa_em(cursor)
        if fe_c:
            cursor = fe_c[3] + datetime.timedelta(days=10)
            continue
        prox = _proxima_festa_inicio(cursor)
        fim_ciclo = cursor + datetime.timedelta(days=8)
        if prox is None or fim_ciclo < prox:
            if cursor <= d <= fim_ciclo:
                return {"tipo": "pedido", "dia": (d - cursor).days + 1, "ciclo_inicio": cursor}
            cursor = fim_ciclo + datetime.timedelta(days=1)
        else:
            if cursor <= d < prox:
                return {"tipo": "avulsa", "motivo": "intervalo antes de novena de festa"}
            cursor = prox
    return {"tipo": "avulsa", "motivo": "fallback"}


def nome_mes(d):
    return f"{CFG['meses'][d.month - 1]} {d.year}"


def nome_playlist(plano, categoria=None):
    if plano["tipo"] == "festa":
        return f"{plano['festa']['nome']} {plano['ciclo_inicio'].year} {CFG['completa']}"
    if plano["tipo"] == "pedido":
        return f"{CATEGORIAS[categoria][0]} — {nome_mes(plano['ciclo_inicio'])}"
    return None


def montar_titulo(plano, promessa, categoria=None, data=None):
    """[Palavra-chave de busca] + [Dia N] + 🙏 + [Dor/Promessa]."""
    promessa = (promessa or "").strip().strip(".").strip()
    n = plano["dia"]
    dia_lbl = CFG["dia_label"].format(n=n)
    if plano["tipo"] == "festa":
        base = f"{plano['festa']['nome']} {dia_lbl} 🙏"
        if CFG.get("data_no_titulo_festa") and data is not None:
            base += " " + CFG["data_fmt"].format(d=data.day, m=CFG["meses"][data.month - 1])
            base += " |"
    else:
        base = f"{CATEGORIAS[categoria][0]} – {dia_lbl} 🙏"
    titulo = f"{base} {promessa}".strip()
    if len(titulo) > 100:
        titulo = base.rstrip(" |")
    return titulo


def texto_thumb(plano):
    return CFG["thumb_fmt"].format(n=plano["dia"])


def tema_codificado(plano, categoria=None):
    chave = plano["festa"]["id"] if plano["tipo"] == "festa" else categoria
    return f"NOVENA|{nome_playlist(plano, categoria)}|{plano['dia']}|{plano['tipo']}|{chave}"


def montar_roteiro(plano, gancho, reflexao, suplica, encerramento):
    if plano["tipo"] == "festa":
        f = plano["festa"]
        oracao = CFG["oracoes_festa"].get(f["id"], CFG["oracao_festa_generica"]).format(inv=f["invocacao"])
        jac = CFG["jaculatoria"].format(inv=f["invocacao"])
    else:
        oracao = CFG["oracao_pedido"]
        jac = CFG["jaculatoria"].format(inv=CFG["invocacao_padrao"])
    partes = [gancho.strip(), CFG["sinal_da_cruz"], CFG["ato_contricao"], reflexao.strip(), oracao,
              suplica.strip(), CFG["pai_nosso"], CFG["ave_maria"], CFG["gloria"], jac,
              encerramento.strip(), CFG["sinal_da_cruz"]]
    return "\n\n".join(p for p in partes if p)


def _aba(planilha, nome, cabecalho):
    try:
        return planilha.worksheet(nome)
    except Exception:
        ws = planilha.add_worksheet(title=nome, rows=1000, cols=len(cabecalho))
        ws.update(values=[cabecalho], range_name="A1")
        return ws


def escolher_tema_pedido(planilha, ciclo_inicio):
    ws_nov = _aba(planilha, ABA_NOVENAS, ["Canal", "Inicio", "Tipo", "Categoria", "Fonte", "Criado_em"])
    linhas = ws_nov.get_all_values()[1:]
    ciclo_str = str(ciclo_inicio)
    do_canal = [l for l in linhas if len(l) >= 4 and l[0] == CANAL and l[2] == "pedido"]
    for l in do_canal:
        if l[1] == ciclo_str and l[3] in CATEGORIAS:
            return l[3]
    usados = [l[3] for l in sorted(do_canal, key=lambda x: x[1]) if l[1] < ciclo_str][-JANELA_ANTI_REPETICAO:]
    escolha, fonte = None, "fallback"
    try:
        ws_t = _aba(planilha, ABA_TEMAS, ["Canal", "Data", "Categoria", "Contagem"])
        rows = [r for r in ws_t.get_all_values()[1:] if len(r) >= 4 and r[0] == CANAL]
        if rows:
            ultima = max(r[1] for r in rows)
            dt_ult = datetime.datetime.strptime(ultima, "%Y-%m-%d").date()
            if (ciclo_inicio - dt_ult).days <= 30:
                lote = []
                for r in rows:
                    if r[1] == ultima and r[2] in CATEGORIAS:
                        try: lote.append((r[2], int(r[3])))
                        except ValueError: pass
                if sum(c for _, c in lote) >= MIN_COMENTARIOS_RANKING:
                    for cat, cnt in sorted(lote, key=lambda x: -x[1]):
                        if cnt > 0 and cat not in usados:
                            escolha, fonte = cat, f"comentarios {ultima}"
                            break
    except Exception as e:
        print(f"[WARN] Ranking de comentários indisponível: {e}")
    if not escolha:
        idx = len(do_canal)
        for i in range(len(ROTACAO_FALLBACK)):
            cand = ROTACAO_FALLBACK[(idx + i) % len(ROTACAO_FALLBACK)]
            if cand not in usados:
                escolha = cand
                break
    ws_nov.append_row([CANAL, ciclo_str, "pedido", escolha, fonte,
                       datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")])
    print(f"📿 Novo ciclo de pedido {ciclo_str}: '{escolha}' ({fonte})")
    return escolha
