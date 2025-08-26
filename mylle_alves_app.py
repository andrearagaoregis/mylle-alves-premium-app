# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import uuid
import logging
import threading
import base64
import io
import os
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from hashlib import md5

# ======================
# CONFIGURAÇÃO INICIAL
# ======================
st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None
    logger.warning("deep-translator não instalado. Tradução desabilitada.")

# Estilos CSS
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], 
    div[data-testid="stStatusWidget"], #MainMenu, header, footer, 
    .stDeployButton {display: none !important;}
    .block-container {padding-top: 0rem !important;}
    [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {gap: 0.5rem !important;}
    .stApp {
        margin: 0 !important; 
        padding: 0 !important;
        background: radial-gradient(1200px 500px at -10% -10%, rgba(255, 0, 153, 0.25) 0%, transparent 60%) ,
                    radial-gradient(1400px 600px at 110% 10%, rgba(148, 0, 211, .25) 0%, transparent 55%),
                    linear-gradient(135deg, #140020 0%, #25003b 50%, #11001c 100%);
        color: white;
    }
    .stChatMessage {padding: 12px !important; border-radius: 15px !important; margin: 8px 0 !important;}
    .stButton > button {
        transition: all 0.3s ease !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 102, 179, 0.1) !important;
        color: white !important;
        border: 1px solid #ff66b3 !important;
    }
    .social-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 15px 0;
    }
    .social-button {
        background: rgba(255, 102, 179, 0.2) !important;
        border: 1px solid #ff66b3 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }
    .social-button:hover {
        background: rgba(255, 102, 179, 0.4) !important;
        transform: scale(1.1) !important;
    }
    .cta-button {
        margin-top: 10px !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .cta-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .audio-message {
        background: rgba(255, 102, 179, 0.15) !important;
        padding: 15px !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        border: 1px solid #ff66b3 !important;
        text-align: center !important;
    }
    .audio-icon {
        font-size: 24px !important;
        margin-right: 10px !important;
    }
    .recording-indicator {
        display: inline-block;
        padding: 8px 12px;
        background: rgba(255, 0, 0, 0.2);
        border-radius: 15px;
        color: #ff4444;
        margin: 5px 0;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .typing-indicator {
        display: inline-block;
        padding: 12px;
        background: rgba(255,102,179,0.1);
        border-radius: 18px;
        margin: 5px 0;
    }
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background: #ff66b3;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }
    .donation-badge {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7em;
        margin-left: 5px;
    }
    
    /* Melhorias responsivas e de acessibilidade */
    @media (max-width: 768px) {
        .stButton > button {
            padding: 12px 8px;
            font-size: 14px;
        }
        .stChatMessage {
            padding: 8px !important;
            margin: 5px 0 !important;
        }
        .audio-message {
            padding: 10px !important;
        }
    }
    
    .stButton > button:focus {
        outline: 2px solid #ff66b3;
        outline-offset: 2px;
    }
    
    .stChatMessage {
        transition: all 0.3s ease;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = st.secrets.get("API_KEY", "AIzaSyB0R7cnWI33WjzID5spoZmXroddEoqmBoM")
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    # Links de checkout para doações
    DONATION_CHECKOUT_LINKS = {
        30: "https://seu.link.de.checkout/30reais",
        50: "https://seu.link.de.checkout/50reais", 
        100: "https://seu.link.de.checkout/100reais",
        150: "https://seu.link.de.checkout/150reais",
        "custom": "https://seu.link.de.checkout/personalizado"
    }
    
    # Links de checkout para packs
    CHECKOUT_TARADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACC74F-01EC-4770-B182-B5775AF62A1D"
    CHECKOUT_MOLHADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD1E6-0EFD-4E3E-9F9D-BA0C1A2D7E7A"
    CHECKOUT_SAFADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD395-EE65-458E-9F7E-FED750CC9CA9"
    
    MAX_REQUESTS_PER_SESSION = 100
    REQUEST_TIMEOUT = 30
    IMG_PROFILE = "https://i.ibb.co/bMynqzMh/BY-Admiregirls-su-Admiregirls-su-156.jpg"
    IMG_PREVIEW = "https://i.ibb.co/fGqCCyHL/preview-exclusive.jpg"
    
    PACK_IMAGES = {
        "TARADINHA": "https://i.ibb.co/sJJRttzM/BY-Admiregirls-su-Admiregirls-su-033.jpg",
        "MOLHADINHA": "https://i.ibb.co/NnTYdSw6/BY-Admiregirls-su-Admiregirls-su-040.jpg", 
        "SAFADINHA": "https://i.ibb.co/GvqtJ17h/BY-Admiregirls-su-Admiregirls-su-194.jpg"
    }
    
    IMG_GALLERY = [
        "https://i.ibb.co/VY42ZMST/BY-Admiregirls-su-Admiregirls-su-255.jpg",
        "https://i.ibb.co/Q7s9Zwcr/BY-Admiregirls-su-Admiregirls-su-183.jpg",
        "https://i.ibb.co/0jRMxrFB/BY-Admiregirls-su-Admiregirls-su-271.jpg"
    ]
    
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/5Gfw3hQ/home-prev-1.jpg",
        "https://i.ibb.co/vkXch6N/home-prev-2.jpg",
        "https://i.ibb.co/v4s5fnW/home-prev-3.jpg",
        "https://i.ibb.co/7gVtGkz/home-prev-4.jpg"
    ]
    
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "onlyfans": "https://onlyfans.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "twitter": "https://twitter.com/myllealves"
    }
    
    SOCIAL_ICONS = {
        "instagram": "📸 Instagram",
        "onlyfans": "💎 OnlyFans",
        "telegram": "✈️ Telegram",
        "twitter": "🐦 Twitter"
    }
    
    # Áudios
    AUDIOS = {
        "claro_tenho_amostra_gratis": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "imagina_ela_bem_rosinha": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "o_que_achou_amostras": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/O%20que%20achou%20das%20amostras.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "oi_meu_amor_tudo_bem": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Oi%20meu%20amor%20tudo%20bem.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "pq_nao_faco_chamada": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pq%20nao%20fa%C3%A7o%20mais%20chamada.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "ver_nua_tem_que_comprar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pra%20me%20ver%20nua%20tem%20que%20comprar%20os%20packs.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "eu_tenho_uns_conteudos_que_vai_amar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "nao_sou_fake_nao": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/nao%20sou%20fake%20nao.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "vida_to_esperando_voce_me_responder_gatinho": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/vida%20to%20esperando%20voce%20me%20responder%20gatinho.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "boa_noite_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "boa_tarde_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "bom_dia_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        }
    }
    
    # Valores de doação 
    DONATION_AMOUNTS = [30, 50, 100, 150]
    
    # Padrões de detecção de fake com pontuação
    FAKE_DETECTION_PATTERNS = [
        (["fake", "falsa", "bot", "robô"], 0.8),
        (["não", "é", "real"], 0.7),
        (["é", "você", "mesmo"], 0.9),
        (["vc", "é", "real"], 0.9),
        (["duvido", "que", "seja"], 0.8),
        (["mentira", "farsa"], 0.7),
        (["verdadeira", "autêntica"], -0.5),
        (["pessoa", "de", "verdade"], 0.6),
        (["não", "acredito"], 0.5),
        (["programa", "automático"], 0.7),
    ]

# ======================
# SISTEMA DE ÁUDIO
# ======================
class AudioManager:
    def __init__(self):
        self.audio_history = defaultdict(list)
        self.last_audio_time = {}
    
    def get_least_used_audio(self, audio_keys: List[str], user_id: str) -> Optional[str]:
        """Retorna o áudio menos usado recentemente pelo usuário"""
        if not audio_keys:
            return None
            
        user_history = self.audio_history.get(user_id, {})
        
        # Filtrar áudios que não foram usados recentemente
        available_audios = []
        for audio_key in audio_keys:
            last_used = user_history.get(audio_key, 0)
            if time.time() - last_used > 300:  # 5 minutos de cooldown
                available_audios.append(audio_key)
        
        if not available_audios:
            available_audios = audio_keys
        
        # Encontrar o áudio menos usado
        usage_count = {}
        for audio_key in available_audios:
            usage_count[audio_key] = Config.AUDIOS[audio_key]["usage_count"]
        
        if usage_count:
            least_used = min(usage_count.items(), key=lambda x: x[1])[0]
            return least_used
        
        return None
    
    def mark_audio_used(self, audio_key: str, user_id: str):
        """Marca um áudio como usado"""
        if audio_key in Config.AUDIOS:
            Config.AUDIOS[audio_key]["usage_count"] += 1
            Config.AUDIOS[audio_key]["last_used"] = time.time()
            
            if user_id not in self.audio_history:
                self.audio_history[user_id] = {}
            self.audio_history[user_id][audio_key] = time.time()

# Instância global do gerenciador de áudio
audio_manager = AudioManager()

# ======================
# SISTEMA DE DOAÇÃO
# ======================
class DonationSystem:
    def __init__(self):
        self.donation_history = defaultdict(list)
        self.total_donations = 0
    
    def show_donation_modal(self):
        """Mostra modal de doação com links de checkout"""
        with st.expander("💝 Fazer uma Doação", expanded=True):
            st.markdown("""
            <div style="
                background: rgba(255,102,179,0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
            ">
                <h3 style="color: #ff66b3; margin: 0;">💝 Apoie Meu Conteúdo</h3>
                <p style="color: #aaa; margin: 5px 0 0;">Sua doação me ajuda a criar mais conteúdo exclusivo!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de valor rápido com links de checkout
            st.markdown("### 🎯 Valores Sugeridos")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("R$ 30", key="donate_30", use_container_width=True):
                    self._redirect_to_checkout(30)
            with col2:
                if st.button("R$ 50", key="donate_50", use_container_width=True):
                    self._redirect_to_checkout(50)
            with col3:
                if st.button("R$ 100", key="donate_100", use_container_width=True):
                    self._redirect_to_checkout(100)
            with col4:
                if st.button("R$ 150", key="donate_150", use_container_width=True):
                    self._redirect_to_checkout(150)
    
    def _redirect_to_checkout(self, amount: float, is_custom: bool = False):
        """Redireciona para página de checkout"""
        user_id = get_user_id()
        
        # Obter link de checkout apropriado
        if is_custom:
            checkout_url = Config.DONATION_CHECKOUT_LINKS["custom"]
        else:
            checkout_url = Config.DONATION_CHECKOUT_LINKS.get(amount, Config.DONATION_CHECKOUT_LINKS["custom"])
        
        # Redirecionar para checkout
        st.markdown(f"""
        <script>
            window.open('{checkout_url}', '_blank');
        </script>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ Redirecionando para página de pagamento de R$ {amount:.2f}...")

# Instância global do sistema de doação
donation_system = DonationSystem()

# ======================
# FUNÇÕES AUXILIARES
# ======================
def get_user_id() -> str:
    """Gera ID único do usuário baseado na sessão"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def detect_fake_question(text: str) -> float:
    """Detecta se o texto contém dúvidas sobre autenticidade"""
    text = text.lower()
    words = re.findall(r'\w+', text)
    probability = 0
    
    for pattern, score in Config.FAKE_DETECTION_PATTERNS:
        if all(word in words for word in pattern):
            probability += score
    
    return min(1.0, max(0, probability))

def init_db() -> sqlite3.Connection:
    """Inicializa banco de dados"""
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            session_id TEXT,
            timestamp DATETIME,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    return conn

def save_message(conn: sqlite3.Connection, user_id: str, session_id: str, role: str, content: str):
    """Salva mensagem no banco de dados"""
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO conversations (user_id, session_id, timestamp, role, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, datetime.now(), role, content))
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {e}")

def load_messages(conn: sqlite3.Connection, user_id: str, session_id: str, limit: int = 50) -> List[Dict]:
    """Carrega mensagens do banco de dados"""
    try:
        c = conn.cursor()
        c.execute('''
            SELECT role, content, timestamp FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (user_id, session_id, limit))
        
        messages = []
        for row in reversed(c.fetchall()):
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        return messages
    except Exception as e:
        logger.error(f"Erro ao carregar mensagens: {e}")
        return []

def call_gemini_api(prompt: str, user_id: str) -> Dict:
    """Chama a API do Gemini"""
    try:
        # Verificar se API Key está configurada
        if Config.API_KEY == "sua_chave_api_gemini_aqui":
            return {
                "text": "⚠️ Sistema em configuração. Configure sua API Key do Gemini para usar o chat.",
                "audio": None,
                "cta": {"show": False}
            }
        
        # Detectar pergunta sobre fake
        fake_probability = detect_fake_question(prompt)
        if fake_probability > 0.7:
            return {
                "text": "Não sou fake não, amor! Ouça minha voz... 😘",
                "audio": "nao_sou_fake_nao",
                "cta": {"show": False}
            }
        
        # Preparar dados para API
        data = {
            "contents": [{
                "parts": [{"text": f"""
Você é Mylle Alves, uma criadora de conteúdo adulto brasileira de 22 anos. 
Seja natural, carinhosa e um pouco provocante. Use emojis e gírias brasileiras.
Sempre incentive a compra dos seus packs de fotos.

Mensagem do usuário: {prompt}

Responda de forma natural e envolvente, como se fosse realmente você conversando.
"""}]
            }]
        }
        
        response = requests.post(
            Config.API_URL,
            json=data,
            timeout=Config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Selecionar áudio baseado no contexto
            audio_key = None
            if any(word in prompt.lower() for word in ["oi", "olá", "bom dia"]):
                audio_key = "oi_meu_amor_tudo_bem"
            elif any(word in prompt.lower() for word in ["pack", "foto", "conteúdo"]):
                audio_key = "eu_tenho_uns_conteudos_que_vai_amar"
            
            return {
                "text": text,
                "audio": audio_key,
                "cta": {"show": True, "label": "📦 Ver Packs", "target": "offers"}
            }
        else:
            return {
                "text": "Estou com problemas técnicos agora, amor 😔 Tenta de novo em um minutinho?",
                "audio": None,
                "cta": {"show": False}
            }
            
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return {
            "text": "Oops! Algo deu errado... Me manda de novo? 😘",
            "audio": None,
            "cta": {"show": False}
        }

# ======================
# INTERFACE DO USUÁRIO
# ======================
def show_home_page():
    """Mostra página inicial"""
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #ff66b3; font-size: 2.5em; margin-bottom: 10px;">
            🔥 Mylle Alves Premium 🔥
        </h1>
        <p style="color: #aaa; font-size: 1.2em; margin-bottom: 30px;">
            Conteúdo exclusivo e muito quente te esperando...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Imagem de perfil
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(Config.IMG_PROFILE, width=300, caption="Mylle Alves 💋")
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Conversar Comigo", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col2:
        if st.button("📦 Ver Meus Packs", use_container_width=True):
            st.session_state.current_page = "offers"
            st.rerun()
    
    with col3:
        if st.button("🖼️ Galeria", use_container_width=True):
            st.session_state.current_page = "gallery"
            st.rerun()
    
    # Links sociais
    st.markdown("### 🌟 Me siga nas redes:")
    social_cols = st.columns(4)
    
    for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
        with social_cols[i]:
            icon = Config.SOCIAL_ICONS[platform]
            if st.button(icon, key=f"social_{platform}", use_container_width=True):
                st.markdown(f'<script>window.open("{link}", "_blank");</script>', unsafe_allow_html=True)

def show_chat_page():
    """Mostra página de chat"""
    st.markdown("### 💬 Chat com Mylle Alves")
    
    # Área de mensagens
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Mostrar áudio se disponível
                if message["role"] == "assistant" and message.get("audio"):
                    audio_url = Config.AUDIOS.get(message["audio"], {}).get("url")
                    if audio_url:
                        st.audio(audio_url)
    
    # Input do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Verificar limite de requests
        if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
            st.error("Limite de mensagens atingido para esta sessão.")
            return
        
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.request_count += 1
        
        # Salvar no banco
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "user", prompt)
        
        # Mostrar mensagem do usuário
        with st.chat_message("user"):
            st.write(prompt)
        
        # Gerar resposta
        with st.chat_message("assistant"):
            with st.spinner("Digitando..."):
                response = call_gemini_api(prompt, get_user_id())
                
                st.write(response["text"])
                
                # Reproduzir áudio se disponível
                if response.get("audio"):
                    audio_url = Config.AUDIOS.get(response["audio"], {}).get("url")
                    if audio_url:
                        st.audio(audio_url)
                        audio_manager.mark_audio_used(response["audio"], get_user_id())
                
                # Mostrar CTA se necessário
                if response.get("cta", {}).get("show"):
                    if st.button(response["cta"]["label"], key="cta_button"):
                        st.session_state.current_page = response["cta"]["target"]
                        st.rerun()
        
        # Salvar resposta no banco
        assistant_message = {
            "role": "assistant", 
            "content": response["text"],
            "audio": response.get("audio")
        }
        st.session_state.messages.append(assistant_message)
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "assistant", response["text"])

def show_offers_page():
    """Mostra página de ofertas"""
    st.markdown("### 📦 Meus Packs Exclusivos")
    
    # Pack Taradinha
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["TARADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 🔥 Pack Taradinha - R$ 30
        - 50+ fotos sensuais
        - Conteúdo exclusivo
        - Acesso imediato
        """)
        if st.button("💳 Comprar Pack Taradinha", key="buy_taradinha"):
            st.markdown(f'<script>window.open("{Config.CHECKOUT_TARADINHA}", "_blank");</script>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pack Molhadinha
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["MOLHADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 💦 Pack Molhadinha - R$ 50
        - 80+ fotos quentes
        - Vídeos exclusivos
        - Conteúdo premium
        """)
        if st.button("💳 Comprar Pack Molhadinha", key="buy_molhadinha"):
            st.markdown(f'<script>window.open("{Config.CHECKOUT_MOLHADINHA}", "_blank");</script>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pack Safadinha
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(Config.PACK_IMAGES["SAFADINHA"], width=200)
    with col2:
        st.markdown("""
        #### 😈 Pack Safadinha - R$ 80
        - 120+ fotos explícitas
        - Vídeos longos
        - Conteúdo mais ousado
        """)
        if st.button("💳 Comprar Pack Safadinha", key="buy_safadinha"):
            st.markdown(f'<script>window.open("{Config.CHECKOUT_SAFADINHA}", "_blank");</script>', unsafe_allow_html=True)

def show_gallery_page():
    """Mostra galeria de fotos"""
    st.markdown("### 🖼️ Galeria de Fotos")
    
    st.info("🔒 Algumas fotos são apenas uma amostra. Para ver o conteúdo completo, adquira meus packs!")
    
    cols = st.columns(3)
    for i, img_url in enumerate(Config.IMG_GALLERY):
        with cols[i % 3]:
            st.image(img_url, caption=f"Foto {i+1}")
    
    st.markdown("---")
    if st.button("📦 Ver Todos os Packs", use_container_width=True):
        st.session_state.current_page = "offers"
        st.rerun()

def show_sidebar():
    """Mostra sidebar com navegação"""
    with st.sidebar:
        st.markdown("### 🔥 Mylle Alves")
        st.image(Config.IMG_PROFILE, width=150)
        
        st.markdown("---")
        
        # Navegação
        if st.button("🏠 Início", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
        
        if st.button("📦 Packs", use_container_width=True):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button("🖼️ Galeria", use_container_width=True):
            st.session_state.current_page = "gallery"
            st.rerun()
        
        st.markdown("---")
        
        # Sistema de doação
        donation_system.show_donation_modal()
        
        st.markdown("---")
        st.markdown("💋 **Mylle Alves Premium**")
        st.markdown("Conteúdo exclusivo para maiores de 18 anos")

def handle_age_verification():
    """Verifica idade do usuário"""
    if not st.session_state.get('age_verified', False):
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #ff66b3;">🔞 Verificação de Idade</h1>
            <p style="font-size: 1.2em; color: #aaa;">
                Este conteúdo é destinado apenas para maiores de 18 anos.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Sou maior de 18", use_container_width=True):
                st.session_state.age_verified = True
                st.rerun()
        
        with col3:
            if st.button("❌ Sou menor de 18", use_container_width=True):
                st.error("Você deve ser maior de 18 anos para acessar este conteúdo.")
                st.stop()
        
        return False
    return True

# ======================
# FUNÇÃO PRINCIPAL
# ======================
def main():
    # Inicializar sessão
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_db()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(random.randint(100000, 999999))
    
    if 'messages' not in st.session_state:
        st.session_state.messages = load_messages(
            st.session_state.db_conn, 
            get_user_id(), 
            st.session_state.session_id
        )
    
    if 'request_count' not in st.session_state:
        st.session_state.request_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    # Verificação de idade
    if not handle_age_verification():
        return
    
    # Mostrar sidebar
    show_sidebar()
    
    # Roteamento de páginas
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "chat":
        show_chat_page()
    elif st.session_state.current_page == "offers":
        show_offers_page()
    elif st.session_state.current_page == "gallery":
        show_gallery_page()

if __name__ == "__main__":
    main()

