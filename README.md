# Mylle Alves Premium - Aplicativo Streamlit

Este é um aplicativo Streamlit para criação de conteúdo interativo com chat inteligente e sistema de vendas.

## 🚀 Funcionalidades

- ✅ Chat interativo com IA (Gemini)
- ✅ Sistema de áudio personalizado
- ✅ Galeria de imagens
- ✅ Sistema de vendas de packs
- ✅ Sistema de doações
- ✅ Interface responsiva
- ✅ Banco de dados SQLite para histórico
- ❌ Reconhecimento de imagens (removido)

## 📋 Configuração

### 1. API Key do Gemini

Para usar o chat com IA, você precisa configurar uma API Key do Google Gemini:

1. Acesse: https://aistudio.google.com/
2. Crie uma API Key gratuita
3. Configure no Streamlit Cloud:
   - Vá em Settings > Secrets
   - Adicione: `API_KEY = "sua_chave_aqui"`

### 2. Links de Checkout

Atualize os links de checkout no arquivo `mylle_alves_app.py`:

```python
# Links de checkout para packs
CHECKOUT_TARADINHA = "seu_link_aqui"
CHECKOUT_MOLHADINHA = "seu_link_aqui"
CHECKOUT_SAFADINHA = "seu_link_aqui"

# Links de doação
DONATION_CHECKOUT_LINKS = {
    30: "seu_link_30_reais",
    50: "seu_link_50_reais",
    # ...
}
```

### 3. Imagens

As imagens estão hospedadas no ImgBB. Para usar suas próprias imagens:

1. Faça upload no ImgBB ou outro serviço
2. Atualize as URLs no arquivo de configuração

## 🛠️ Instalação Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/mylle-alves-app.git
cd mylle-alves-app

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
streamlit run mylle_alves_app.py
```

## 🌐 Deploy no Streamlit Cloud

1. Faça fork deste repositório
2. Acesse: https://share.streamlit.io/
3. Conecte sua conta GitHub
4. Selecione o repositório
5. Configure as secrets (API_KEY)
6. Deploy!

## 📱 Uso

1. **Verificação de Idade**: Usuários devem confirmar ser maiores de 18 anos
2. **Navegação**: Use a sidebar para navegar entre páginas
3. **Chat**: Converse com a IA na página de chat
4. **Packs**: Visualize e compre packs na página de ofertas
5. **Galeria**: Veja amostras de fotos na galeria
6. **Doações**: Sistema de doações integrado na sidebar

## 🔧 Personalização

### Cores e Estilo

Edite a seção CSS no início do arquivo para personalizar:
- Cores do tema
- Gradientes de fundo
- Estilos dos botões
- Animações

### Áudios

Adicione novos áudios na configuração:

```python
AUDIOS = {
    "novo_audio": {
        "url": "https://link-do-audio.mp3",
        "usage_count": 0,
        "last_used": None
    }
}
```

### Respostas da IA

Modifique o prompt da IA na função `call_gemini_api()` para personalizar o comportamento.

## 📊 Recursos Removidos

- Sistema de reconhecimento de imagens (pytesseract, PIL)
- Processamento OCR
- Análise de conteúdo de imagens
- Upload de imagens pelo usuário

## 🐛 Solução de Problemas

### Erro "NotFoundError: removeChild"
- ✅ Corrigido: Removido gerenciamento complexo de estado
- ✅ Corrigido: Simplificado sistema de componentes
- ✅ Corrigido: Otimizado re-renderização

### API Key não configurada
- Configure a API_KEY nas secrets do Streamlit Cloud
- Ou defina como variável de ambiente: `export API_KEY="sua_chave"`

### Imagens não carregam
- Verifique se as URLs das imagens estão acessíveis
- Use serviços confiáveis como ImgBB, Imgur, etc.

## 📄 Licença

Este projeto é para uso educacional e demonstrativo. Adapte conforme necessário para seu uso específico.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Verifique a documentação do Streamlit
- Consulte a documentação da API Gemini

