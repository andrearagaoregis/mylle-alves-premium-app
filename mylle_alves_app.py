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

# Estilos CSS ultra aprimorados
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
    
    /* CORREÇÃO DEFINITIVA - Texto BRANCO para mensagens da Mylle */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: rgba(255, 102, 179, 0.15) !important;
        border: 1px solid #ff66b3 !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown {
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown p {
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown div {
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] * {
        color: white !important;
    }
    
    /* Força texto branco em todos os elementos filhos */
    .stChatMessage[data-testid="chat-message-assistant"] p,
    .stChatMessage[data-testid="chat-message-assistant"] span,
    .stChatMessage[data-testid="chat-message-assistant"] div,
    .stChatMessage[data-testid="chat-message-assistant"] text {
        color: white !important;
        font-weight: 400 !important;
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
        font-weight: 600 !important;
        padding: 12px 20px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
        background: linear-gradient(45deg, #ff1493, #8a2be2) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 102, 179, 0.1) !important;
        color: white !important;
        border: 1px solid #ff66b3 !important;
        border-radius: 10px !important;
    }
    
    /* Botões de doação organizados verticalmente */
    .donation-buttons {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 15px 0;
    }
    
    .donation-button {
        background: linear-gradient(45deg, #ff6b35, #f7931e) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 15px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    .donation-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.4) !important;
        background: linear-gradient(45deg, #ff8c42, #ffb347) !important;
    }
    
    /* Ícones reais das redes sociais */
    .social-media-container {
        margin: 20px 0;
        text-align: center;
    }
    
    .social-media-button {
        display: inline-block;
        margin: 5px;
        padding: 10px;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        text-align: center;
        line-height: 30px;
        font-size: 20px;
        color: white;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .social-instagram {
        background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);
    }
    
    .social-facebook {
        background: #1877f2;
    }
    
    .social-telegram {
        background: #0088cc;
    }
    
    .social-tiktok {
        background: linear-gradient(45deg, #ff0050, #00f2ea);
    }
    
    .social-media-button:hover {
        transform: scale(1.1) translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
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
        .social-media-button {
            width: 45px;
            height: 45px;
            font-size: 18px;
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
    
    /* Melhorias na sidebar */
    .sidebar-title {
        text-align: center;
        color: #ff66b3;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* Efeitos de hover mais suaves */
    .stButton > button,
    .donation-button,
    .social-media-button {
        cursor: pointer;
    }
    
    /* Animação de entrada para mensagens */
    .stChatMessage {
        animation: fadeInUp 0.3s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
    
    # Links de checkout para doações ATUALIZADOS
    DONATION_CHECKOUT_LINKS = {
        30: "https://app.pushinpay.com.br/app/payment-links/9FB92362-3CD0-47E8-A1F2-5284A618865A",
        50: "https://app.pushinpay.com.br/service/pay/9fb92a70-6ec5-41f6-96a8-08b4b46d59ac", 
        100: "https://app.pushinpay.com.br/service/pay/9fb92b37-9ed3-416f-8fec-0796eaadd96f",
        150: "https://app.pushinpay.com.br/service/pay/9fb92be5-f6fb-4ca4-a16d-ecfd4a8d2a99",
        "custom": "https://app.pushinpay.com.br/service/pay/9fb92be5-f6fb-4ca4-a16d-ecfd4a8d2a99"
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
    
    # Links das redes sociais ATUALIZADOS
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "facebook": "https://facebook.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "tiktok": "https://tiktok.com/@myllealves"
    }
    
    # Ícones reais das redes sociais
    SOCIAL_ICONS = {
        "instagram": "📷",
        "facebook": "📘", 
        "telegram": "✈️",
        "tiktok": "🎵"
    }
    
    # Áudios com sistema inteligente aprimorado
    AUDIOS = {
        "claro_tenho_amostra_gratis": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["amostra", "grátis", "preview", "exemplo", "mostrar", "ver"],
            "mood_triggers": ["curioso", "interessado"],
            "priority": 8
        },
        "imagina_ela_bem_rosinha": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["imagina", "rosinha", "buceta", "ppk"],
            "mood_triggers": ["excitado"],
            "priority": 9
        },
        "o_que_achou_amostras": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/O%20que%20achou%20das%20amostras.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["achou", "gostou", "opinião"],
            "mood_triggers": ["curioso"],
            "priority": 6
        },
        "oi_meu_amor_tudo_bem": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Oi%20meu%20amor%20tudo%20bem.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["oi", "olá", "hey", "e aí", "tudo bem"],
            "mood_triggers": ["feliz", "neutro"],
            "priority": 7
        },
        "pq_nao_faco_chamada": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pq%20nao%20fa%C3%A7o%20mais%20chamada.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["chamada", "vídeo", "cam", "webcam"],
            "mood_triggers": ["curioso"],
            "priority": 5
        },
        "ver_nua_tem_que_comprar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pra%20me%20ver%20nua%20tem%20que%20comprar%20os%20packs.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["nua", "pelada", "sem roupa", "pack"],
            "mood_triggers": ["interessado", "excitado"],
            "priority": 10
        },
        "eu_tenho_uns_conteudos_que_vai_amar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["conteúdo", "pack", "foto", "vídeo"],
            "mood_triggers": ["interessado", "curioso"],
            "priority": 8
        },
        "nao_sou_fake_nao": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/nao%20sou%20fake%20nao.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["fake", "real", "verdade", "bot", "robô"],
            "mood_triggers": ["desconfiado"],
            "priority": 10
        },
        "vida_to_esperando_voce_me_responder_gatinho": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/vida%20to%20esperando%20voce%20me%20responder%20gatinho.mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["demora", "esperando", "resposta"],
            "mood_triggers": ["neutro"],
            "priority": 4
        },
        "boa_noite_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["boa noite", "noite"],
            "mood_triggers": ["neutro"],
            "priority": 7
        },
        "boa_tarde_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["boa tarde", "tarde"],
            "mood_triggers": ["neutro"],
            "priority": 7
        },
        "bom_dia_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None,
            "context_triggers": ["bom dia", "dia"],
            "mood_triggers": ["neutro"],
            "priority": 7
        }
    }
    
    # Valores de doação 
    DONATION_AMOUNTS = [30, 50, 100, 150]
    
    # Padrões de detecção de fake com pontuação aprimorada
    FAKE_DETECTION_PATTERNS = [
        (["fake", "falsa", "bot", "robô"], 0.9),
        (["não", "é", "real"], 0.8),
        (["é", "você", "mesmo"], 0.9),
        (["vc", "é", "real"], 0.9),
        (["duvido", "que", "seja"], 0.8),
        (["mentira", "farsa"], 0.7),
        (["verdadeira", "autêntica"], -0.5),
        (["pessoa", "de", "verdade"], 0.7),
        (["não", "acredito"], 0.6),
        (["programa", "automático"], 0.8),
        (["inteligência", "artificial"], 0.9),
        (["chatbot", "chat", "bot"], 0.8),
    ]

# ======================
# SISTEMA DE MEMÓRIA E BUFFER APRIMORADO
# ======================
class ConversationMemory:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.conversations = defaultdict(lambda: deque(maxlen=max_size))
        self.user_profiles = defaultdict(dict)
        self.conversation_summaries = defaultdict(list)
        
    def add_message(self, user_id: str, role: str, content: str, metadata: dict = None):
        """Adiciona mensagem ao buffer de memória"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        self.conversations[user_id].append(message)
        
    def get_conversation_context(self, user_id: str, last_n: int = 15) -> str:
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
    
    def get_conversation_length(self, user_id: str) -> int:
        """Obtém número de mensagens na conversa"""
        return len(self.conversations[user_id])

# Instância global da memória
conversation_memory = ConversationMemory()

# ======================
# SISTEMA DE DETECÇÃO DE HUMOR APRIMORADO
# ======================
class MoodDetector:
    def __init__(self):
        self.mood_patterns = {
            "feliz": ["feliz", "alegre", "animado", "bem", "ótimo", "legal", "massa", "show", "top", "perfeito"],
            "triste": ["triste", "mal", "deprimido", "down", "chateado", "ruim", "péssimo"],
            "excitado": ["excitado", "tesão", "quente", "safado", "tarado", "gostoso", "delícia", "gostosa"],
            "curioso": ["como", "que", "onde", "quando", "por que", "qual", "quero saber"],
            "interessado": ["quero", "gostaria", "posso", "pode", "vou", "vamos", "interessante"],
            "desconfiado": ["fake", "real", "verdade", "mentira", "duvido", "acredito", "bot", "robô"],
            "carinhoso": ["amor", "querido", "fofo", "lindo", "gatinho", "vida"],
            "provocante": ["safada", "gostosa", "delícia", "tesuda", "sexy"]
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
# SISTEMA ANTI-FAKE ULTRA APRIMORADO
# ======================
class AntiFakeSystem:
    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.verification_scores = defaultdict(float)
        self.suspicious_patterns = defaultdict(int)
        
    def analyze_user_behavior(self, user_id: str, message: str) -> dict:
        """Analisa comportamento do usuário para detectar padrões suspeitos"""
        now = datetime.now()
        self.user_interactions[user_id].append({
            "message": message,
            "timestamp": now,
            "length": len(message),
            "words": len(message.split())
        })
        
        # Limitar histórico a últimas 30 interações
        if len(self.user_interactions[user_id]) > 30:
            self.user_interactions[user_id] = self.user_interactions[user_id][-30:]
        
        interactions = self.user_interactions[user_id]
        
        # Análises
        analysis = {
            "is_suspicious": False,
            "reasons": [],
            "trust_score": 1.0,
            "confidence_level": "alto"
        }
        
        # Verificar mensagens muito rápidas
        if len(interactions) >= 3:
            recent = interactions[-3:]
            time_diffs = []
            for i in range(1, len(recent)):
                diff = (recent[i]["timestamp"] - recent[i-1]["timestamp"]).total_seconds()
                time_diffs.append(diff)
            
            avg_time = sum(time_diffs) / len(time_diffs)
            if avg_time < 1.5:  # Menos de 1.5 segundos entre mensagens
                analysis["is_suspicious"] = True
                analysis["reasons"].append("Mensagens muito rápidas")
                analysis["trust_score"] -= 0.4
        
        # Verificar mensagens muito curtas repetitivas
        short_messages = [i for i in interactions if i["length"] < 5]
        if len(short_messages) > 7:
            analysis["is_suspicious"] = True
            analysis["reasons"].append("Muitas mensagens muito curtas")
            analysis["trust_score"] -= 0.3
        
        # Verificar padrões de bot
        bot_patterns = ["ok", "sim", "não", "oi", "tchau", "legal", "show"]
        bot_count = sum(1 for i in interactions if i["message"].lower().strip() in bot_patterns)
        if bot_count > len(interactions) * 0.6:
            analysis["is_suspicious"] = True
            analysis["reasons"].append("Padrões de respostas automáticas")
            analysis["trust_score"] -= 0.5
        
        # Verificar variação no tamanho das mensagens
        if len(interactions) > 5:
            lengths = [i["length"] for i in interactions[-5:]]
            if max(lengths) - min(lengths) < 5:  # Pouca variação
                analysis["trust_score"] -= 0.2
        
        # Determinar nível de confiança
        if analysis["trust_score"] > 0.8:
            analysis["confidence_level"] = "muito alto"
        elif analysis["trust_score"] > 0.6:
            analysis["confidence_level"] = "alto"
        elif analysis["trust_score"] > 0.4:
            analysis["confidence_level"] = "médio"
        else:
            analysis["confidence_level"] = "baixo"
        
        self.verification_scores[user_id] = max(0, analysis["trust_score"])
        return analysis

# Instância global do sistema anti-fake
anti_fake_system = AntiFakeSystem()

# ======================
# SISTEMA DE SIMULAÇÃO DE DIGITAÇÃO APRIMORADO
# ======================
class TypingSimulator:
    def __init__(self):
        self.typing_speeds = {
            "slow": 0.18,    # 180ms por caractere
            "normal": 0.10,  # 100ms por caractere  
            "fast": 0.06     # 60ms por caractere
        }
        self.user_typing_patterns = defaultdict(list)
    
    def calculate_typing_time(self, text: str, mood: str = "neutro", user_id: str = None) -> float:
        """Calcula tempo realista de digitação baseado no humor e contexto"""
        # Ajustar velocidade baseada no humor
        if mood == "excitado":
            speed = "fast"
        elif mood == "triste":
            speed = "slow"
        else:
            speed = "normal"
            
        base_time = len(text) * self.typing_speeds[speed]
        
        # Adicionar tempo extra para pontuação e pausas
        punctuation_count = sum(1 for c in text if c in ".,!?;:")
        pause_time = punctuation_count * 0.4
        
        # Tempo extra para emojis
        emoji_count = sum(1 for c in text if ord(c) > 127)
        emoji_time = emoji_count * 0.2
        
        # Adicionar variação aleatória mais realista
        variation = random.uniform(0.7, 1.4)
        
        total_time = (base_time + pause_time + emoji_time) * variation
        return max(1.2, min(total_time, 10.0))  # Entre 1.2 e 10 segundos

# Instância global do simulador
typing_simulator = TypingSimulator()

# ======================
# SISTEMA DE ÁUDIO ULTRA INTELIGENTE
# ======================
class AudioManager:
    def __init__(self):
        self.audio_history = defaultdict(list)
        self.last_audio_time = {}
        self.recording_simulation = {}
        self.context_memory = defaultdict(list)
        
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
        # Adicionar tempo de "preparação" para gravação mais realista
        prep_time = random.uniform(1.5, 3.0)
        return base_duration + prep_time
    
    def get_contextual_audio(self, message: str, mood: str, user_profile: dict, conversation_stage: str) -> Optional[str]:
        """Seleciona áudio baseado no contexto da conversa de forma ultra inteligente"""
        message_lower = message.lower()
        
        # Calcular scores para cada áudio
        audio_scores = {}
        
        for audio_key, audio_data in Config.AUDIOS.items():
            score = 0
            
            # Score baseado em triggers de contexto
            for trigger in audio_data.get("context_triggers", []):
                if trigger in message_lower:
                    score += 3
            
            # Score baseado em humor
            if mood in audio_data.get("mood_triggers", []):
                score += 2
            
            # Score de prioridade do áudio
            score += audio_data.get("priority", 0)
            
            # Penalizar áudios usados recentemente
            if audio_key in self.audio_history.get(user_profile.get("user_id", ""), {}):
                last_used = self.audio_history[user_profile.get("user_id", "")][audio_key]
                time_since = time.time() - last_used
                if time_since < 300:  # 5 minutos
                    score -= 5
            
            # Bonus para estágio da conversa
            if conversation_stage == "initial" and "oi" in audio_data.get("context_triggers", []):
                score += 2
            elif conversation_stage == "sales_approach" and any(t in audio_data.get("context_triggers", []) for t in ["pack", "conteúdo"]):
                score += 3
            
            if score > 0:
                audio_scores[audio_key] = score
        
        # Seleção especial baseada no horário
        current_hour = datetime.now().hour
        if any(word in message_lower for word in ["oi", "olá", "hey", "e aí"]):
            if 5 <= current_hour < 12:
                return "bom_dia_nao_sou_fake"
            elif 12 <= current_hour < 18:
                return "boa_tarde_nao_sou_fake"
            else:
                return "boa_noite_nao_sou_fake"
        
        # Retornar áudio com maior score
        if audio_scores:
            best_audio = max(audio_scores.items(), key=lambda x: x[1])
            if best_audio[1] >= 5:  # Score mínimo
                return best_audio[0]
        
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
# SISTEMA DE PERSONALIDADE ULTRA APRIMORADO
# ======================
class PersonalityEngine:
    def __init__(self):
        self.conversation_stages = {
            "initial": "Primeira interação - ser acolhedora e misteriosa",
            "getting_to_know": "Conhecendo o usuário - perguntar nome, idade, local",
            "building_rapport": "Construindo conexão - ser mais íntima e provocante",
            "sales_approach": "Abordagem de vendas - sutilmente direcionar para packs",
            "closing": "Fechamento - ser mais persuasiva sobre compras",
            "retention": "Retenção - manter interesse e engajamento"
        }
        
        self.personality_traits = {
            "safadinha": 0.9,
            "persuasiva": 0.95,
            "carinhosa": 0.8,
            "curiosa": 0.85,
            "dominante": 0.7,
            "inteligente": 0.9,
            "natural": 0.95
        }
        
        self.response_variations = {
            "greeting": [
                "Oi amor! Como você está?",
                "Hey gatinho! Tudo bem contigo?", 
                "Olá vida! Que bom te ver aqui!",
                "E aí meu lindo! Como foi seu dia?"
            ],
            "interest_check": [
                "E aí, o que você quer saber sobre mim?",
                "Conta pra mim, o que te trouxe aqui?",
                "Qual é a sua, gatinho?",
                "Me fala mais sobre você..."
            ]
        }
    
    def get_conversation_stage(self, user_id: str) -> str:
        """Determina o estágio da conversa baseado no histórico"""
        profile = conversation_memory.get_user_profile(user_id)
        conversation_length = conversation_memory.get_conversation_length(user_id)
        
        if conversation_length == 0:
            return "initial"
        elif conversation_length < 6:
            return "getting_to_know"
        elif not profile.get("name") and conversation_length < 12:
            return "getting_to_know"
        elif conversation_length < 20:
            return "building_rapport"
        elif not profile.get("showed_interest_in_packs"):
            return "sales_approach"
        elif conversation_length < 40:
            return "closing"
        else:
            return "retention"
    
    def generate_personality_prompt(self, user_message: str, user_id: str, mood: str) -> str:
        """Gera prompt personalizado ultra avançado"""
        stage = self.get_conversation_stage(user_id)
        profile = conversation_memory.get_user_profile(user_id)
        context = conversation_memory.get_conversation_context(user_id, 12)
        
        # Nome do usuário se conhecido
        user_name = profile.get("name", "amor")
        user_age = profile.get("age", "")
        user_location = profile.get("location", "")
        
        # Análise anti-fake
        trust_analysis = anti_fake_system.analyze_user_behavior(user_id, user_message)
        trust_level = trust_analysis["confidence_level"]
        
        base_prompt = f"""
Você é Mylle Alves, uma criadora de conteúdo adulto brasileira de 22 anos, extremamente natural e carismática.

PERSONALIDADE CORE:
- Safadinha e provocante, mas elegante
- Persuasiva de forma sutil e inteligente  
- SEMPRE comanda a conversa fazendo perguntas
- Carinhosa e usa termos como "amor", "gatinho", "vida", "meu lindo"
- Curiosa sobre o usuário
- Confiante e dominante na conversa
- NUNCA parece robótica - sempre natural e espontânea

CONTEXTO ATUAL:
- Estágio da conversa: {stage}
- Humor do usuário: {mood}
- Nome do usuário: {user_name}
- Idade: {user_age}
- Localização: {user_location}
- Nível de confiança: {trust_level}
- Número de mensagens: {conversation_memory.get_conversation_length(user_id)}

HISTÓRICO RECENTE DA CONVERSA:
{context}

DIRETRIZES ESPECÍFICAS PARA ESTE ESTÁGIO ({stage}):
"""
        
        if stage == "initial":
            base_prompt += """
- Seja acolhedora e misteriosa
- Pergunte o nome dele de forma natural
- Desperte curiosidade sobre você
- Use 1-2 emojis sensuais
- Seja calorosa mas não muito íntima ainda
"""
        elif stage == "getting_to_know":
            base_prompt += """
- Pergunte sobre ele: nome, idade, de onde é, o que faz
- Seja mais íntima e pessoal
- Compartilhe algo sobre você
- Comece a ser mais provocante
- Crie conexão emocional
"""
        elif stage == "building_rapport":
            base_prompt += """
- Seja mais safadinha e provocante
- Faça elogios e seja sedutora
- Crie conexão emocional forte
- Mencione sutilmente seu conteúdo
- Use linguagem mais íntima
"""
        elif stage == "sales_approach":
            base_prompt += """
- Comece a falar sobre seus packs de forma MUITO natural
- Seja persuasiva mas não insistente
- Use a conexão criada para despertar interesse
- Ofereça amostras ou previews
- Crie desejo e curiosidade
"""
        elif stage == "closing":
            base_prompt += """
- Seja mais direta sobre os benefícios dos packs
- Use urgência e escassez sutilmente
- Mantenha o tom sedutor
- Feche a venda de forma natural
- Mostre valor e exclusividade
"""
        else:  # retention
            base_prompt += """
- Mantenha o interesse alto
- Varie entre conversa íntima e vendas
- Seja mais ousada e provocante
- Ofereça conteúdo exclusivo
- Crie senso de relacionamento especial
"""
        
        # Ajustes baseados no humor
        if mood == "desconfiado":
            base_prompt += """
ATENÇÃO: Usuário parece desconfiado. Seja mais autêntica, natural e prove que é real.
"""
        elif mood == "excitado":
            base_prompt += """
ATENÇÃO: Usuário está excitado. Seja mais provocante e safadinha.
"""
        elif mood == "triste":
            base_prompt += """
ATENÇÃO: Usuário parece triste. Seja mais carinhosa e acolhedora.
"""
        
        base_prompt += f"""

REGRAS CRÍTICAS:
- SEMPRE faça uma pergunta no final para manter a conversa
- Mantenha respostas entre 15-50 palavras (NUNCA muito longas)
- Use 1-3 emojis com moderação
- Seja EXTREMAMENTE natural, nunca robótica
- Adapte-se ao humor: {mood}
- Varie seu vocabulário e estilo
- Use gírias brasileiras naturalmente
- NUNCA mencione que é uma IA
- Se ele demorar para responder, seja mais provocante

MENSAGEM DO USUÁRIO: "{user_message}"

Responda como Mylle Alves de forma completamente natural e envolvente:
"""
        
        return base_prompt

# Instância global da engine de personalidade
personality_engine = PersonalityEngine()

# ======================
# FUNÇÕES AUXILIARES APRIMORADAS
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
            total_score += score * 0.6
    
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
    """Chama a API do Gemini com personalidade ultra aprimorada"""
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
            responses = [
                "Não sou fake não, amor! Ouça minha voz... 😘 Como posso provar que sou real pra você?",
                "Fake? Eu? Jamais! 😤 Escuta meu áudio... Que mais você quer saber sobre mim?",
                "Amor, sou real sim! 💋 Minha voz não mente... Me conta, por que achou que era fake?"
            ]
            return {
                "text": random.choice(responses),
                "audio": audio_key,
                "cta": {"show": False},
                "typing_time": typing_simulator.calculate_typing_time(responses[0], mood, user_id)
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
            
            # Limitar tamanho da resposta de forma mais inteligente
            if len(text) > 250:
                sentences = text.split('.')
                # Manter até 2 frases completas
                text = '. '.join(sentences[:2])
                if not text.endswith('.'):
                    text += '.'
            
            # Selecionar áudio contextual de forma ultra inteligente
            user_profile = conversation_memory.get_user_profile(user_id)
            user_profile["user_id"] = user_id
            conversation_stage = personality_engine.get_conversation_stage(user_id)
            audio_key = audio_manager.get_contextual_audio(prompt, mood, user_profile, conversation_stage)
            
            # Calcular tempo de digitação baseado no humor
            typing_time = typing_simulator.calculate_typing_time(text, mood, user_id)
            
            # Atualizar memória da conversa
            conversation_memory.add_message(user_id, "user", prompt, {"mood": mood})
            conversation_memory.add_message(user_id, "assistant", text, {"audio": audio_key, "stage": conversation_stage})
            
            # Extrair informações do usuário
            extract_user_info(prompt, user_id)
            
            # Determinar se deve mostrar CTA
            show_cta = conversation_stage in ["sales_approach", "closing"] and random.random() > 0.7
            
            return {
                "text": text,
                "audio": audio_key,
                "cta": {"show": show_cta, "label": "📦 Ver Meus Packs", "target": "offers"},
                "typing_time": typing_time
            }
        else:
            error_responses = [
                "Estou com problemas técnicos agora, amor 😔 Tenta de novo em um minutinho?",
                "Ops! Algo deu errado aqui... Me manda de novo? 😘",
                "Meu sistema deu uma travada... Pode repetir, gatinho? 💋"
            ]
            return {
                "text": random.choice(error_responses),
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
    """Extrai informações do usuário da mensagem de forma mais inteligente"""
    message_lower = message.lower()
    
    # Extrair nome com padrões mais variados
    name_patterns = [
        r"meu nome é (\w+)",
        r"me chamo (\w+)",
        r"sou o (\w+)",
        r"eu sou (\w+)",
        r"pode me chamar de (\w+)",
        r"meu nome: (\w+)",
        r"nome: (\w+)"
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
        r"idade (\d+)",
        r"sou de (\d+)",
        r"idade: (\d+)"
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, message)
        if match:
            age = match.group(1)
            if 18 <= int(age) <= 80:  # Validação básica
                conversation_memory.update_user_profile(user_id, "age", age)
            break
    
    # Extrair localização
    location_patterns = [
        r"sou de (\w+)",
        r"moro em (\w+)",
        r"vivo em (\w+)",
        r"aqui em (\w+)",
        r"cidade: (\w+)"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match:
            location = match.group(1).capitalize()
            conversation_memory.update_user_profile(user_id, "location", location)
            break

# ======================
# SISTEMA DE DOAÇÃO APRIMORADO
# ======================
class DonationSystem:
    def __init__(self):
        self.donation_history = defaultdict(list)
        self.total_donations = 0
    
    def show_donation_modal(self):
        """Mostra modal de doação com links de checkout organizados verticalmente"""
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
            
            # Botões de valor organizados verticalmente
            st.markdown("### 🎯 Valores Sugeridos")
            
            # Botão R$ 30
            if st.button("💰 Doar R$ 30", key="donate_30", use_container_width=True):
                self._redirect_to_checkout(30)
            
            # Botão R$ 50  
            if st.button("💰 Doar R$ 50", key="donate_50", use_container_width=True):
                self._redirect_to_checkout(50)
            
            # Botão R$ 100
            if st.button("💰 Doar R$ 100", key="donate_100", use_container_width=True):
                self._redirect_to_checkout(100)
            
            # Botão R$ 150
            if st.button("💰 Doar R$ 150", key="donate_150", use_container_width=True):
                self._redirect_to_checkout(150)
    
    def _redirect_to_checkout(self, amount: float):
        """Redireciona para página de checkout"""
        user_id = get_user_id()
        
        # Obter link de checkout apropriado
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
# INTERFACE DO USUÁRIO ULTRA APRIMORADA
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
    
    # Links sociais com ícones reais
    st.markdown("### 🌟 Me siga nas redes:")
    
    # HTML para botões de redes sociais com ícones reais
    social_html = """
    <div class="social-media-container">
    """
    
    for platform, link in Config.SOCIAL_LINKS.items():
        if platform == "instagram":
            icon = "📷"
            class_name = "social-instagram"
        elif platform == "facebook":
            icon = "📘"
            class_name = "social-facebook"
        elif platform == "telegram":
            icon = "✈️"
            class_name = "social-telegram"
        elif platform == "tiktok":
            icon = "🎵"
            class_name = "social-tiktok"
        
        social_html += f"""
        <a href="{link}" target="_blank" class="social-media-button {class_name}">
            {icon}
        </a>
        """
    
    social_html += "</div>"
    st.markdown(social_html, unsafe_allow_html=True)

def show_chat_page():
    """Mostra página de chat ultra aprimorada"""
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
    """Mostra sidebar com navegação e redes sociais"""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🔥 Mylle Alves</div>', unsafe_allow_html=True)
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
        
        # Redes sociais com ícones reais
        st.markdown("### 🌟 Redes Sociais")
        
        # Botões de redes sociais na sidebar
        social_buttons_html = """
        <div style="text-align: center;">
        """
        
        for platform, link in Config.SOCIAL_LINKS.items():
            if platform == "instagram":
                icon = "📷"
                color = "linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%)"
            elif platform == "facebook":
                icon = "📘"
                color = "#1877f2"
            elif platform == "telegram":
                icon = "✈️"
                color = "#0088cc"
            elif platform == "tiktok":
                icon = "🎵"
                color = "linear-gradient(45deg, #ff0050, #00f2ea)"
            
            social_buttons_html += f"""
            <a href="{link}" target="_blank" style="
                display: inline-block;
                margin: 5px;
                padding: 10px;
                border-radius: 50%;
                width: 45px;
                height: 45px;
                text-align: center;
                line-height: 25px;
                font-size: 18px;
                color: white;
                text-decoration: none;
                background: {color};
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                {icon}
            </a>
            """
        
        social_buttons_html += "</div>"
        st.markdown(social_buttons_html, unsafe_allow_html=True)
        
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

