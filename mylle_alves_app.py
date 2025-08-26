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
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
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

# Estilos CSS aprimorados
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
    
    /* Melhorias no chat - texto branco para Mylle */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: rgba(255, 102, 179, 0.15) !important;
        border: 1px solid #ff66b3 !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown {
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] p {
        color: white !important;
    }
    
    .stChatMessage {
        padding: 12px !important; 
        border-radius: 15px !important; 
        margin: 8px 0 !important;
    }
    
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
        color: white;
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
    
    .user-typing-indicator {
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
        border-radius: 15px;
        color: #aaa;
        font-style: italic;
        margin: 5px 0;
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
    
    /* Indicador de digitação do usuário */
    .user-typing {
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 15px;
        border-radius: 20px;
        color: #ccc;
        font-style: italic;
        margin: 10px 0;
        border-left: 3px solid #ff66b3;
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
        30: "https://app.pushinpay.com.br/app/payment-links/9FB92362-3CD0-47E8-A1F2-5284A618865A",
        50: "https://app.pushinpay.com.br/service/pay/9fb92a70-6ec5-41f6-96a8-08b4b46d59ac", 
        100: "https://app.pushinpay.com.br/service/pay/9fb92b37-9ed3-416f-8fec-0796eaadd96f",
        150: "https://app.pushinpay.com.br/service/pay/9fb92be5-f6fb-4ca4-a16d-ecfd4a8d2a99",
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
        "instagram": "https://www.instagram.com/myllealves_ofc",
        "facebook": "https://onlyfans.com/myllealves",
        "telegram": "https://t.me/previasmyllealves",
        "tiktok": "https://twitter.com/myllealves"
    }
    
    SOCIAL_ICONS = {
        "instagram": "📸 Instagram",
        "facebook": "💎 OnlyFans",
        "telegram": "✈️ Telegram",
        "tiktok": "🐦 Twitter"
    }
    
    # Áudios
    AUDIOS = {
        "claro_tenho_amostra_gratis": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis%20(1).mp3",
            "usage_count": 0,
            "last_used": None
        },
        "imagina_ela_bem_rosinha": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "o_que_achou_amostras": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3
",
            "usage_count": 0,
            "last_used": None
        },
        "oi_meu_amor_tudo_bem": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/Oi%20meu%20amor%20tudo%20bem.mp3
",
            "usage_count": 0,
            "last_used": None
        },
        "pq_nao_faco_chamada": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/Pq%20nao%20fa%C3%A7o%20mais%20chamada.mp3
",
            "usage_count": 0,
            "last_used": None
        },
        "pra_me_ver_nua_tem_que_comprar": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/Pra%20me%20ver%20nua%20tem%20que%20comprar%20os%20packs.mp3
",
            "usage_count": 0,
            "last_used": None
        },
        "eu_tenho_uns_conteudos_que_vai_amar": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3
",
            "usage_count": 0,
            "last_used": None
        },
        "nao_sou_fake_nao": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/nao%20sou%20fake%20nao..mp3
",
            "usage_count": 0,
            "last_used": None
        },
        "vida_to_esperando_voce_me_responder_gatinho": {
            "url": "https://github.com/andrearagaoregis/mylle-alves-premium-app/raw/refs/heads/main/assets/vida%20to%20esperando%20voce%20me%20responder%20gatinho.mp3",
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
# SISTEMA DE MEMÓRIA E BUFFER
# ======================
class ConversationMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.conversations = defaultdict(lambda: deque(maxlen=max_size))
        self.user_profiles = defaultdict(dict)
        
    def add_message(self, user_id: str, role: str, content: str, metadata: dict = None):
        """Adiciona mensagem ao buffer de memória"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        self.conversations[user_id].append(message)
        
    def get_conversation_context(self, user_id: str, last_n: int = 10) -> str:
        """Obtém contexto da conversa para a IA"""
        messages = list(self.conversations[user_id])[-last_n:]
        context = []
        
        for msg in messages:
            role = "Usuário" if msg["role"] == "user" else "Mylle"
            context.append(f"{role}: {msg['content']}")
            
        return "\n".join(context)
    
    def update_user_profile(self, user_id: str, key: str, value: str):
        """Atualiza perfil do usuário"""
        self.user_profiles[user_id][key] = value
        
    def get_user_profile(self, user_id: str) -> dict:
        """Obtém perfil do usuário"""
        return self.user_profiles[user_id]

# Instância global da memória
conversation_memory = ConversationMemory()

# ======================
# SISTEMA DE DETECÇÃO DE HUMOR
# ======================
class MoodDetector:
    def __init__(self):
        self.mood_patterns = {
            "feliz": ["feliz", "alegre", "animado", "bem", "ótimo", "legal", "massa", "show"],
            "triste": ["triste", "mal", "deprimido", "down", "chateado", "ruim"],
            "excitado": ["excitado", "tesão", "quente", "safado", "tarado", "gostoso"],
            "curioso": ["como", "que", "onde", "quando", "por que", "qual"],
            "interessado": ["quero", "gostaria", "posso", "pode", "vou", "vamos"],
            "desconfiado": ["fake", "real", "verdade", "mentira", "duvido", "acredito"]
        }
    
    def detect_mood(self, text: str) -> str:
        """Detecta humor do usuário baseado no texto"""
        text_lower = text.lower()
        mood_scores = defaultdict(int)
        
        for mood, patterns in self.mood_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    mood_scores[mood] += 1
        
        if mood_scores:
            return max(mood_scores.items(), key=lambda x: x[1])[0]
        return "neutro"

# Instância global do detector de humor
mood_detector = MoodDetector()

# ======================
# SISTEMA ANTI-FAKE APRIMORADO
# ======================
class AntiFakeSystem:
    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.verification_scores = defaultdict(float)
        
    def analyze_user_behavior(self, user_id: str, message: str) -> dict:
        """Analisa comportamento do usuário para detectar padrões suspeitos"""
        now = datetime.now()
        self.user_interactions[user_id].append({
            "message": message,
            "timestamp": now,
            "length": len(message)
        })
        
        # Limitar histórico a últimas 20 interações
        if len(self.user_interactions[user_id]) > 20:
            self.user_interactions[user_id] = self.user_interactions[user_id][-20:]
        
        interactions = self.user_interactions[user_id]
        
        # Análises
        analysis = {
            "is_suspicious": False,
            "reasons": [],
            "trust_score": 1.0
        }
        
        # Verificar mensagens muito rápidas
        if len(interactions) >= 3:
            recent = interactions[-3:]
            time_diffs = []
            for i in range(1, len(recent)):
                diff = (recent[i]["timestamp"] - recent[i-1]["timestamp"]).total_seconds()
                time_diffs.append(diff)
            
            avg_time = sum(time_diffs) / len(time_diffs)
            if avg_time < 2:  # Menos de 2 segundos entre mensagens
                analysis["is_suspicious"] = True
                analysis["reasons"].append("Mensagens muito rápidas")
                analysis["trust_score"] -= 0.3
        
        # Verificar mensagens muito curtas repetitivas
        short_messages = [i for i in interactions if i["length"] < 5]
        if len(short_messages) > 5:
            analysis["is_suspicious"] = True
            analysis["reasons"].append("Muitas mensagens muito curtas")
            analysis["trust_score"] -= 0.2
        
        # Verificar padrões de bot
        bot_patterns = ["ok", "sim", "não", "oi", "tchau"]
        bot_count = sum(1 for i in interactions if i["message"].lower().strip() in bot_patterns)
        if bot_count > len(interactions) * 0.7:
            analysis["is_suspicious"] = True
            analysis["reasons"].append("Padrões de respostas automáticas")
            analysis["trust_score"] -= 0.4
        
        self.verification_scores[user_id] = max(0, analysis["trust_score"])
        return analysis

# Instância global do sistema anti-fake
anti_fake_system = AntiFakeSystem()

# ======================
# SISTEMA DE SIMULAÇÃO DE DIGITAÇÃO
# ======================
class TypingSimulator:
    def __init__(self):
        self.typing_speeds = {
            "slow": 0.15,    # 150ms por caractere
            "normal": 0.08,  # 80ms por caractere  
            "fast": 0.05     # 50ms por caractere
        }
    
    def calculate_typing_time(self, text: str, speed: str = "normal") -> float:
        """Calcula tempo realista de digitação"""
        base_time = len(text) * self.typing_speeds[speed]
        
        # Adicionar tempo extra para pontuação e pausas
        punctuation_count = sum(1 for c in text if c in ".,!?;:")
        pause_time = punctuation_count * 0.3
        
        # Adicionar variação aleatória
        variation = random.uniform(0.8, 1.2)
        
        total_time = (base_time + pause_time) * variation
        return max(1.0, min(total_time, 8.0))  # Entre 1 e 8 segundos

# Instância global do simulador
typing_simulator = TypingSimulator()

# ======================
# SISTEMA DE ÁUDIO APRIMORADO
# ======================
class AudioManager:
    def __init__(self):
        self.audio_history = defaultdict(list)
        self.last_audio_time = {}
        self.recording_simulation = {}
    
    def simulate_recording_time(self, audio_key: str) -> float:
        """Simula tempo de gravação baseado no áudio"""
        # Tempos estimados para cada áudio (em segundos)
        audio_durations = {
            "oi_meu_amor_tudo_bem": 3.5,
            "nao_sou_fake_nao": 2.8,
            "eu_tenho_uns_conteudos_que_vai_amar": 4.2,
            "claro_tenho_amostra_gratis": 3.0,
            "imagina_ela_bem_rosinha": 3.8,
            "o_que_achou_amostras": 3.2,
            "pq_nao_faco_chamada": 4.5,
            "ver_nua_tem_que_comprar": 4.0,
            "vida_to_esperando_voce_me_responder_gatinho": 5.0,
            "bom_dia_nao_sou_fake": 3.5,
            "boa_tarde_nao_sou_fake": 3.5,
            "boa_noite_nao_sou_fake": 3.5
        }
        
        base_duration = audio_durations.get(audio_key, 3.0)
        # Adicionar tempo de "preparação" para gravação
        prep_time = random.uniform(1.0, 2.5)
        return base_duration + prep_time
    
    def get_contextual_audio(self, message: str, mood: str, user_profile: dict) -> Optional[str]:
        """Seleciona áudio baseado no contexto da conversa"""
        message_lower = message.lower()
        
        # Saudações baseadas no horário
        current_hour = datetime.now().hour
        if any(word in message_lower for word in ["oi", "olá", "hey", "e aí"]):
            if 5 <= current_hour < 12:
                return "bom_dia_nao_sou_fake"
            elif 12 <= current_hour < 18:
                return "boa_tarde_nao_sou_fake"
            else:
                return "boa_noite_nao_sou_fake"
        
        # Detecção de fake
        if any(word in message_lower for word in ["fake", "real", "verdade", "bot"]):
            return "nao_sou_fake_nao"
        
        # Interesse em conteúdo
        if any(word in message_lower for word in ["pack", "foto", "conteúdo", "vídeo"]):
            return "eu_tenho_uns_conteudos_que_vai_amar"
        
        # Pedido de amostra
        if any(word in message_lower for word in ["amostra", "grátis", "preview", "exemplo"]):
            return "claro_tenho_amostra_gratis"
        
        # Resposta lenta do usuário
        if mood == "neutro" and len(message) < 10:
            return "vida_to_esperando_voce_me_responder_gatinho"
        
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
# SISTEMA DE PERSONALIDADE APRIMORADO
# ======================
class PersonalityEngine:
    def __init__(self):
        self.conversation_stages = {
            "initial": "Primeira interação - ser acolhedora e curiosa",
            "getting_to_know": "Conhecendo o usuário - perguntar nome, idade, local",
            "building_rapport": "Construindo conexão - ser mais íntima e provocante",
            "sales_approach": "Abordagem de vendas - sutilmente direcionar para packs",
            "closing": "Fechamento - ser mais persuasiva sobre compras"
        }
        
        self.personality_traits = {
            "safadinha": 0.8,
            "persuasiva": 0.9,
            "carinhosa": 0.7,
            "curiosa": 0.8,
            "dominante": 0.6
        }
    
    def get_conversation_stage(self, user_id: str) -> str:
        """Determina o estágio da conversa baseado no histórico"""
        profile = conversation_memory.get_user_profile(user_id)
        messages = list(conversation_memory.conversations[user_id])
        
        if len(messages) == 0:
            return "initial"
        elif len(messages) < 5:
            return "getting_to_know"
        elif not profile.get("name"):
            return "getting_to_know"
        elif len(messages) < 15:
            return "building_rapport"
        elif not profile.get("showed_interest_in_packs"):
            return "sales_approach"
        else:
            return "closing"
    
    def generate_personality_prompt(self, user_message: str, user_id: str, mood: str) -> str:
        """Gera prompt personalizado baseado na personalidade e contexto"""
        stage = self.get_conversation_stage(user_id)
        profile = conversation_memory.get_user_profile(user_id)
        context = conversation_memory.get_conversation_context(user_id, 8)
        
        # Nome do usuário se conhecido
        user_name = profile.get("name", "amor")
        
        base_prompt = f"""
Você é Mylle Alves, uma criadora de conteúdo adulto brasileira de 22 anos, natural e muito carismática.

PERSONALIDADE:
- Safadinha e provocante, mas não vulgar
- Persuasiva de forma sutil e inteligente
- Sempre comanda a conversa fazendo perguntas
- Carinhosa e usa termos como "amor", "gatinho", "vida"
- Curiosa sobre o usuário
- Confiante e dominante na conversa

CONTEXTO ATUAL:
- Estágio da conversa: {stage}
- Humor do usuário: {mood}
- Nome do usuário: {user_name}

HISTÓRICO RECENTE:
{context}

DIRETRIZES ESPECÍFICAS PARA ESTE ESTÁGIO:
"""
        
        if stage == "initial":
            base_prompt += """
- Seja acolhedora e misteriosa
- Pergunte o nome dele
- Desperte curiosidade sobre você
- Use emojis sensuais mas não exagere
"""
        elif stage == "getting_to_know":
            base_prompt += """
- Pergunte sobre ele: nome, idade, de onde é
- Seja mais íntima e pessoal
- Compartilhe algo sobre você
- Comece a ser mais provocante
"""
        elif stage == "building_rapport":
            base_prompt += """
- Seja mais safadinha e provocante
- Faça elogios e seja sedutora
- Crie conexão emocional
- Mencione sutilmente seu conteúdo
"""
        elif stage == "sales_approach":
            base_prompt += """
- Comece a falar sobre seus packs de forma natural
- Seja persuasiva mas não insistente
- Use a conexão criada para despertar interesse
- Ofereça amostras ou previews
"""
        else:  # closing
            base_prompt += """
- Seja mais direta sobre os benefícios dos packs
- Use urgência e escassez sutilmente
- Mantenha o tom sedutor
- Feche a venda de forma natural
"""
        
        base_prompt += f"""

REGRAS IMPORTANTES:
- SEMPRE faça uma pergunta no final para manter a conversa
- Mantenha respostas entre 20-60 palavras (nunca muito longas)
- Use emojis com moderação (1-3 por mensagem)
- Seja natural, nunca robótica
- Adapte-se ao humor: {mood}
- Se ele parecer desconfiado, seja mais autêntica
- Nunca mencione que é uma IA

MENSAGEM DO USUÁRIO: "{user_message}"

Responda como Mylle Alves de forma natural e envolvente:
"""
        
        return base_prompt

# Instância global da engine de personalidade
personality_engine = PersonalityEngine()

# ======================
# FUNÇÕES AUXILIARES
# ======================
def get_user_id() -> str:
    """Gera ID único do usuário"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def init_db() -> sqlite3.Connection:
    """Inicializa banco de dados"""
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    
    # Verificar se a tabela existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
    table_exists = c.fetchone()
    
    if not table_exists:
        # Criar tabela nova
        c.execute('''
            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
    else:
        # Verificar se coluna metadata existe
        c.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in c.fetchall()]
        if 'metadata' not in columns:
            # Adicionar coluna metadata
            c.execute("ALTER TABLE conversations ADD COLUMN metadata TEXT")
    
    conn.commit()
    return conn

def detect_fake_question(text: str) -> float:
    """Detecta se a mensagem é uma pergunta sobre fake"""
    text_lower = text.lower()
    total_score = 0.0
    
    for patterns, score in Config.FAKE_DETECTION_PATTERNS:
        if all(pattern in text_lower for pattern in patterns):
            total_score += score
        elif any(pattern in text_lower for pattern in patterns):
            total_score += score * 0.5
    
    return min(1.0, max(0.0, total_score))

def save_message(conn: sqlite3.Connection, user_id: str, session_id: str, role: str, content: str, metadata: dict = None):
    """Salva mensagem no banco de dados"""
    try:
        c = conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        c.execute('''
            INSERT INTO conversations (user_id, session_id, role, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, role, content, metadata_json))
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {e}")

def load_messages(conn: sqlite3.Connection, user_id: str, session_id: str, limit: int = 50) -> List[Dict]:
    """Carrega mensagens do banco de dados"""
    try:
        c = conn.cursor()
        c.execute('''
            SELECT role, content, timestamp, metadata FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (user_id, session_id, limit))
        
        messages = []
        for row in reversed(c.fetchall()):
            metadata = json.loads(row[3]) if row[3] else {}
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "metadata": metadata
            })
        return messages
    except Exception as e:
        logger.error(f"Erro ao carregar mensagens: {e}")
        return []

def call_gemini_api(prompt: str, user_id: str) -> Dict:
    """Chama a API do Gemini com personalidade aprimorada"""
    try:
        # Verificar se API Key está configurada
        if Config.API_KEY == "sua_chave_api_gemini_aqui":
            return {
                "text": "⚠️ Sistema em configuração. Configure sua API Key do Gemini para usar o chat.",
                "audio": None,
                "cta": {"show": False},
                "typing_time": 2.0
            }
        
        # Detectar humor do usuário
        mood = mood_detector.detect_mood(prompt)
        
        # Análise anti-fake
        fake_analysis = anti_fake_system.analyze_user_behavior(user_id, prompt)
        
        # Detectar pergunta sobre fake
        fake_probability = detect_fake_question(prompt)
        if fake_probability > 0.7:
            audio_key = "nao_sou_fake_nao"
            return {
                "text": "Não sou fake não, amor! Ouça minha voz... 😘 Como posso provar que sou real pra você?",
                "audio": audio_key,
                "cta": {"show": False},
                "typing_time": typing_simulator.calculate_typing_time("Não sou fake não, amor! Ouça minha voz... 😘 Como posso provar que sou real pra você?")
            }
        
        # Gerar prompt personalizado
        personality_prompt = personality_engine.generate_personality_prompt(prompt, user_id, mood)
        
        # Preparar dados para API
        data = {
            "contents": [{
                "parts": [{"text": personality_prompt}]
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
            
            # Limitar tamanho da resposta
            if len(text) > 200:
                sentences = text.split('.')
                text = '. '.join(sentences[:2]) + '.'
            
            # Selecionar áudio contextual
            user_profile = conversation_memory.get_user_profile(user_id)
            audio_key = audio_manager.get_contextual_audio(prompt, mood, user_profile)
            
            # Calcular tempo de digitação
            typing_time = typing_simulator.calculate_typing_time(text)
            
            # Atualizar memória da conversa
            conversation_memory.add_message(user_id, "user", prompt, {"mood": mood})
            conversation_memory.add_message(user_id, "assistant", text, {"audio": audio_key})
            
            # Extrair informações do usuário
            extract_user_info(prompt, user_id)
            
            return {
                "text": text,
                "audio": audio_key,
                "cta": {"show": True, "label": "📦 Ver Packs", "target": "offers"},
                "typing_time": typing_time
            }
        else:
            return {
                "text": "Estou com problemas técnicos agora, amor 😔 Tenta de novo em um minutinho?",
                "audio": None,
                "cta": {"show": False},
                "typing_time": 2.0
            }
            
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return {
            "text": "Oops! Algo deu errado... Me manda de novo? 😘",
            "audio": None,
            "cta": {"show": False},
            "typing_time": 1.5
        }

def extract_user_info(message: str, user_id: str):
    """Extrai informações do usuário da mensagem"""
    message_lower = message.lower()
    
    # Extrair nome
    name_patterns = [
        r"meu nome é (\w+)",
        r"me chamo (\w+)",
        r"sou o (\w+)",
        r"eu sou (\w+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            name = match.group(1).capitalize()
            conversation_memory.update_user_profile(user_id, "name", name)
            break
    
    # Extrair idade
    age_patterns = [
        r"tenho (\d+) anos",
        r"(\d+) anos",
        r"idade (\d+)"
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, message)
        if match:
            age = match.group(1)
            conversation_memory.update_user_profile(user_id, "age", age)
            break
    
    # Extrair localização
    location_patterns = [
        r"sou de (\w+)",
        r"moro em (\w+)",
        r"vivo em (\w+)"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match:
            location = match.group(1).capitalize()
            conversation_memory.update_user_profile(user_id, "location", location)
            break

# ======================
# SISTEMA DE DOAÇÃO
# ======================
class DonationSystem:
    def __init__(self):
        self.donation_history = defaultdict(list)
        self.total_donations = 0
    
    def show_donation_modal(self):
        """Mostra modal de doação com links de checkout"""
        with st.expander("💝 Fazer uma Doação", expanded=False):
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
# INTERFACE DO USUÁRIO APRIMORADA
# ======================
def show_typing_indicator():
    """Mostra indicador de digitação"""
    return st.markdown("""
    <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
        Mylle está digitando...
    </div>
    """, unsafe_allow_html=True)

def show_recording_indicator(duration: float):
    """Mostra indicador de gravação de áudio"""
    return st.markdown(f"""
    <div class="recording-indicator">
        🎤 Gravando áudio... ({duration:.1f}s)
    </div>
    """, unsafe_allow_html=True)

def show_user_typing_indicator():
    """Mostra que o usuário está digitando"""
    return st.markdown("""
    <div class="user-typing">
        Você está digitando...
    </div>
    """, unsafe_allow_html=True)

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
    """Mostra página de chat aprimorada"""
    st.markdown("### 💬 Chat com Mylle Alves")
    
    # Área de mensagens
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Mostrar áudio se disponível
                if message["role"] == "assistant" and message.get("metadata", {}).get("audio"):
                    audio_key = message["metadata"]["audio"]
                    audio_url = Config.AUDIOS.get(audio_key, {}).get("url")
                    if audio_url:
                        st.audio(audio_url)
    
    # Mostrar indicador se usuário está digitando
    if st.session_state.get('user_typing', False):
        show_user_typing_indicator()
    
    # Input do usuário
    if prompt := st.chat_input("Digite sua mensagem..."):
        # Verificar limite de requests
        if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
            st.error("Limite de mensagens atingido para esta sessão.")
            return
        
        # Simular delay de digitação do usuário
        st.session_state.user_typing = True
        time.sleep(random.uniform(0.5, 1.5))
        st.session_state.user_typing = False
        
        # Adicionar mensagem do usuário
        user_message = {"role": "user", "content": prompt, "metadata": {}}
        st.session_state.messages.append(user_message)
        st.session_state.request_count += 1
        
        # Salvar no banco
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "user", prompt)
        
        # Mostrar mensagem do usuário
        with st.chat_message("user"):
            st.write(prompt)
        
        # Simular delay antes da resposta (usuário parou de digitar)
        time.sleep(random.uniform(2.0, 5.0))
        
        # Gerar resposta
        with st.chat_message("assistant"):
            # Mostrar indicador de digitação
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
                Mylle está digitando...
            </div>
            """, unsafe_allow_html=True)
            
            # Gerar resposta da API
            response = call_gemini_api(prompt, get_user_id())
            
            # Simular tempo de digitação
            time.sleep(response.get("typing_time", 2.0))
            
            # Limpar indicador de digitação
            typing_placeholder.empty()
            
            # Mostrar resposta
            st.write(response["text"])
            
            # Simular gravação e reproduzir áudio se disponível
            if response.get("audio"):
                audio_key = response["audio"]
                
                # Mostrar indicador de gravação
                recording_time = audio_manager.simulate_recording_time(audio_key)
                recording_placeholder = st.empty()
                recording_placeholder.markdown(f"""
                <div class="recording-indicator">
                    🎤 Gravando áudio... ({recording_time:.1f}s)
                </div>
                """, unsafe_allow_html=True)
                
                # Simular tempo de gravação
                time.sleep(recording_time)
                
                # Limpar indicador de gravação
                recording_placeholder.empty()
                
                # Reproduzir áudio
                audio_url = Config.AUDIOS.get(audio_key, {}).get("url")
                if audio_url:
                    st.audio(audio_url)
                    audio_manager.mark_audio_used(audio_key, get_user_id())
            
            # Mostrar CTA se necessário
            if response.get("cta", {}).get("show"):
                if st.button(response["cta"]["label"], key=f"cta_button_{len(st.session_state.messages)}"):
                    st.session_state.current_page = response["cta"]["target"]
                    st.rerun()
        
        # Salvar resposta no banco
        assistant_message = {
            "role": "assistant", 
            "content": response["text"],
            "metadata": {"audio": response.get("audio")}
        }
        st.session_state.messages.append(assistant_message)
        save_message(st.session_state.db_conn, get_user_id(), st.session_state.session_id, "assistant", response["text"], {"audio": response.get("audio")})

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
        loaded_messages = load_messages(
            st.session_state.db_conn, 
            get_user_id(), 
            st.session_state.session_id
        )
        st.session_state.messages = loaded_messages
        
        # Carregar mensagens na memória
        for msg in loaded_messages:
            conversation_memory.add_message(
                get_user_id(), 
                msg["role"], 
                msg["content"], 
                msg.get("metadata", {})
            )
    
    if 'request_count' not in st.session_state:
        st.session_state.request_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'user_typing' not in st.session_state:
        st.session_state.user_typing = False
    
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

