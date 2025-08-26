# Instruções de Deploy - Mylle Alves Premium App

## 📋 Passos para Deploy no GitHub e Streamlit Cloud

### 1. Criar Repositório no GitHub

1. Acesse [GitHub.com](https://github.com) e faça login
2. Clique em "New repository" ou acesse: https://github.com/new
3. Configure o repositório:
   - **Nome**: `mylle-alves-premium-app`
   - **Descrição**: `Aplicativo Streamlit Premium da Mylle Alves com chat IA, sistema de vendas e doações`
   - **Visibilidade**: Público (para Streamlit Cloud gratuito)
   - **NÃO marque**: "Add a README file", "Add .gitignore", "Choose a license"
4. Clique em "Create repository"

### 2. Comandos para Upload do Código

Após criar o repositório, execute estes comandos (substitua `SEU-USUARIO` pelo seu username do GitHub):

```bash
git remote add origin https://github.com/SEU-USUARIO/mylle-alves-premium-app.git
git push -u origin main
```

### 3. Deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io/)
2. Faça login com sua conta GitHub
3. Clique em "New app"
4. Configure:
   - **Repository**: `SEU-USUARIO/mylle-alves-premium-app`
   - **Branch**: `main`
   - **Main file path**: `mylle_alves_app.py`
5. Clique em "Advanced settings..."
6. Em "Secrets", adicione:
   ```toml
   API_KEY = "sua_chave_api_gemini_aqui"
   ```
7. Clique em "Deploy!"

### 4. Configuração da API Key do Gemini

Para o chat funcionar, você precisa:

1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Crie uma API Key gratuita
3. No Streamlit Cloud, vá em Settings > Secrets
4. Adicione: `API_KEY = "sua_chave_aqui"`

### 5. Personalização dos Links de Checkout

Edite o arquivo `mylle_alves_app.py` e atualize:

```python
# Links de checkout para packs (linha ~220)
CHECKOUT_TARADINHA = "seu_link_de_checkout_aqui"
CHECKOUT_MOLHADINHA = "seu_link_de_checkout_aqui"
CHECKOUT_SAFADINHA = "seu_link_de_checkout_aqui"

# Links de doação (linha ~210)
DONATION_CHECKOUT_LINKS = {
    30: "seu_link_30_reais",
    50: "seu_link_50_reais",
    100: "seu_link_100_reais",
    150: "seu_link_150_reais",
    "custom": "seu_link_personalizado"
}
```

### 6. URLs das Imagens

As imagens estão hospedadas no ImgBB e funcionarão automaticamente. Para usar suas próprias imagens:

1. Faça upload no [ImgBB](https://imgbb.com/) ou similar
2. Atualize as URLs no arquivo `mylle_alves_app.py` (linhas ~230-270)

## ✅ Funcionalidades Incluídas

- ✅ Chat interativo com IA (Gemini)
- ✅ Sistema de áudio personalizado
- ✅ Galeria de imagens
- ✅ Sistema de vendas de packs
- ✅ Sistema de doações
- ✅ Interface responsiva
- ✅ Verificação de idade (18+)
- ✅ Banco de dados SQLite para histórico
- ❌ Reconhecimento de imagens (removido para corrigir erro)

## 🔧 Problemas Corrigidos

- ✅ Erro `NotFoundError: removeChild` do Streamlit
- ✅ Conflitos de gerenciamento de estado
- ✅ Dependências desnecessárias removidas
- ✅ Sistema de componentes simplificado

## 📞 Suporte

Se tiver problemas:
1. Verifique se a API Key está configurada
2. Confirme que o repositório está público
3. Verifique os logs no Streamlit Cloud
4. Consulte a documentação do Streamlit

## 🚀 Próximos Passos

1. Criar repositório no GitHub
2. Fazer upload do código
3. Deploy no Streamlit Cloud
4. Configurar API Key
5. Personalizar links de checkout
6. Testar todas as funcionalidades

