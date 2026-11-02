import streamlit as st
import os
from dotenv import load_dotenv

# ========== DIAGNÓSTICO — NÃO ALTERAR ==========
# Carrega o .env e mostra se funcionou
load_dotenv()
CHAVE_GROQ = os.getenv("GROQ_API_KEY")

# Mostra status para diagnosticar
if not CHAVE_GROQ:
    st.error("❌ CHAVE NÃO ENCONTRADA!")
    st.info("Verifique:")
    st.code("1. O arquivo se chama exatamente .env")
    st.code("2. Está na mesma pasta que assistente_groq.py")
    st.code("3. Linha correta: GROQ_API_KEY=sua_chave_sem_aspas")
    st.stop()
else:
    st.success(f"✅ Chave carregada! Começa com: {CHAVE_GROQ[:8]}...")
# =============================================

from groq import Groq
import speech_recognition as sr
import pyttsx3

# Inicializar cliente
cliente = Groq(api_key=CHAVE_GROQ)
# Troque ESTA linha no seu código:
MODELO = "openai/gpt-oss-20b"

# Configuração da página
st.set_page_config(
    page_title="Assistente com Groq",
    page_icon="⚡",
    layout="wide"
)
st.title("⚡ Assistente de IA")

# Inicializar histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

# ========== FUNÇÕES ==========

def falar_resposta(texto):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 190)
        engine.say(texto)
        engine.runAndWait()
        engine.stop()
    except Exception as erro:
        st.warning(f"Não consegui falar: {erro}")

def ouvir_usuario():
    reconhecedor = sr.Recognizer()
    with sr.Microphone() as fonte:
        st.info("🎙️ Ouvindo... Fale agora!")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=0.5)
        audio = reconhecedor.listen(fonte, timeout=7)
    try:
        return reconhecedor.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        return "Não entendi, pode repetir?"
    except Exception as erro:
        return f"Erro: {str(erro)}"

def perguntar_groq(pergunta):
    try:
        mensagens = []
        for msg in st.session_state.historico:
            mensagens.append({"role": msg["role"], "content": msg["texto"]})
        mensagens.append({
            "role": "user",
            "content": f"Responda de forma clara, amigável e em português: {pergunta}"
        })

        resposta = cliente.chat.completions.create(
            model=MODELO,
            messages=mensagens,
            temperature=0.7,
            max_tokens=2048
        )
        return resposta.choices[0].message.content

    except Exception as e:
        return f"❌ Erro: {str(e)}"

def processar_pergunta(pergunta):
    if not pergunta.strip():
        return None

    st.session_state.historico.append({"role": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    with st.spinner("⚡ Pensando..."):
        resposta = perguntar_groq(pergunta)

    st.session_state.historico.append({"role": "assistant", "texto": resposta})
    with st.chat_message("assistant"):
        st.write(resposta)

    return resposta

# ========== INTERFACE ==========

for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["role"]):
        st.write(mensagem["texto"])

entrada = st.chat_input("Digite sua pergunta...")
if entrada:
    resp = processar_pergunta(entrada)
    if st.checkbox("🔊 Ouvir resposta", key=f"voz_{len(st.session_state.historico)}"):
        falar_resposta(resp)

if st.button("Falar com o assistente", type="primary"):
    pergunta_voz = ouvir_usuario()
    resp_voz = processar_pergunta(pergunta_voz)
    if resp_voz and not resp_voz.startswith("❌"):
        falar_resposta(resp_voz)

if st.button("Nova conversa"):
    st.session_state.historico = []
    st.rerun()

st.divider()
st.caption(f"⚡ Modelo: {MODELO}")