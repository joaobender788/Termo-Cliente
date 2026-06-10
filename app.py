import streamlit as st
import requests

# Configuração da página do jogo
st.set_page_config(page_title="TERMO", page_icon="🧩", layout="centered")

st.title("🧩 TERMO - Sistema Distribuído")
st.write("Tente adivinhar a palavra secreta de 5 letras!")

# ATENÇÃO: Enquanto testamos no computador, a URL é a do localhost (127.0.0.1:8000)
# Quando jogarmos na nuvem, vamos trocar esse link pelo link da Render!
API_URL = "https://termo-api-5hlq.onrender.com/verificar"
API_URL_REINICIAR = "https://termo-api-5hlq.onrender.com/reiniciar"
API_URL_REVELAR = "https://termo-api-5hlq.onrender.com/revelar"

# Inicializar o estado do jogo se não existir
if "tentativas" not in st.session_state:
    st.session_state.tentativas = []
    try:
        requests.post(API_URL_REINICIAR) # Avisa o servidor para sortear
    except:
        pass
if "fim_de_jogo" not in st.session_state:
    st.session_state.fim_de_jogo = False

# Função para renderizar as letras com cores estilo Termo
def estilizar_letra(letra, cor):
    cores = {
        "verde": "#3aa35c",   # Letra certa no lugar certo
        "amarelo": "#d3ad24", # Letra existe mas lugar errado
        "cinza": "#312a2c"    # Letra não existe
    }
    bg_color = cores.get(cor, "#312a2c")
    return f'<div style="display:inline-block; width:45px; height:45px; line-height:45px; text-align:center; font-weight:bold; font-size:20px; color:white; background-color:{bg_color}; margin:3px; border-radius:5px; text-transform:uppercase;">{letra}</div>'

# Mostrar o histórico de jogadas na tela
for jogada in st.session_state.tentativas:
    palavra = jogada["palavra"]
    cores = jogada["cores"]
    
    # Cria uma linha com as 5 caixinhas coloridas
    linha_html = "".join([estilizar_letra(palavra[i], cores[i]) for i in range(5)])
    st.markdown(linha_html, unsafe_allow_html=True)

st.write("---")

# Interface para o usuário digitar o palpite
if not st.session_state.fim_de_jogo and len(st.session_state.tentativas) < 6:
    with st.form(key="palpite_form", clear_on_submit=True):
        input_palpite = st.text_input("Digite seu palpite (5 letras):", max_chars=5).strip().upper()
        botao_enviar = st.form_submit_button("Enviar Palpite")
        
    if botao_enviar:
        if len(input_palpite) != 5:
            st.warning("A palavra precisa ter exatamente 5 letras!")
        else:
            # A MÁGICA DO SISTEMA DISTRIBUÍDO: O cliente envia o dado via rede para a API processar
            try:
                resposta = requests.post(API_URL, json={"palpite": input_palpite})
                
                if resposta.status_code == 200:
                    dados = resposta.json()
                    
                    if "erro" in dados:
                        st.error(dados["erro"])
                    else:
                        # Salva o resultado retornado pelo servidor
                        st.session_state.tentativas.append({
                            "palavra": dados["palpite"],
                            "cores": dados["resultado"]
                        })
                        
                        if dados["venceu"]:
                            st.session_state.fim_de_jogo = True
                            st.balloons()
                            st.success("🎉 Parabéns! Você acertou a palavra secreta!")
                        
                        # Recarrega a página para atualizar a tela
                        st.rerun()
                else:
                    st.error("Erro na comunicação com o servidor do jogo.")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao Servidor do Jogo. Ele está ligado?")

# Se esgotar as tentativas
if len(st.session_state.tentativas) >= 6 and not st.session_state.fim_de_jogo:
    st.error("💥 Fim de jogo! Você esgotou as 6 tentativas.")
    
    # Bate na API para descobrir qual era a palavra
    try:
        resposta_revelar = requests.get(API_URL_REVELAR)
        if resposta_revelar.status_code == 200:
            palavra_correta = resposta_revelar.json().get("palavra", "")
            st.warning(f"A palavra secreta era: **{palavra_correta}**")
    except:
        pass
        
    st.session_state.fim_de_jogo = True

# Botão para reiniciar o jogo
if st.session_state.fim_de_jogo:
    if st.button("Jogar Novamente"):
        st.session_state.tentativas = []
        st.session_state.fim_de_jogo = False
        try:
            requests.post(API_URL_REINICIAR)
        except:
            pass
        st.rerun()
