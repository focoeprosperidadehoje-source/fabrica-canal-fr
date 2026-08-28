# TODO: Script principal da live 24h para o canal FR.
# Implementar quando SSH_KEY_VPS_FR e STREAM_KEY_H_FR estiverem configurados.
# Baseado em: fabrica-canal-en/ao_vivo_en/ao_vivo_en.py
# Adaptar:
#   CANAL_ID = "UC7dZrYzY22dO-h6RfRN1bsw"
#   PLAYLIST_LIVES = "PLUEPEIYr2qHA"
#   FUSO = pytz.timezone("Europe/Paris")
#   STREAM_KEY_H = os.environ.get("STREAM_KEY_H_FR", "")
#   BASE_DIR = Path("/root/ao_vivo_fr")
#   VOZ = "fr-FR-DeniseNeural"
#   CHAVES_CONTEUDO: GEMINI_KEY_LIVE_CONTENT_1_FR, GEMINI_KEY_LIVE_CONTENT_2_FR
#   CHAVES_CHAT: GEMINI_KEY_LIVE_CHAT_1_FR, _2_FR, _3_FR
#   Timer offset: ciclo_start - 3600 (FR dispara 1h antes do ES para não colidir)
#   Persona: Notre-Dame de Lourdes, Vierge Marie
#   TITULOS_LIVE e DESCRICAO_LIVE em francês
print("ao_vivo_fr.py: aguardando SSH key e stream key para implementação completa.")
