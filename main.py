


import streamlit as st
import requests
import json
import pandas as pd
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pygame
import hashlib
import streamlit as st
import json
import os
import subprocess

import subprocess
import streamlit as st



st.set_page_config(
    page_title="Dona sorte",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store passworda
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    st.toast('Verificação completa!', icon='🚀')



    config_carregadas = False  # Inicialmente, as configurações não estão carregadas

    # Carregar o JSON com as configurações a partir do upload de arquivo
    uploaded_file = st.file_uploader("Carregar arquivo de configurações JSON", type="json")

    if uploaded_file is not None and not config_carregadas:
        config_data = json.load(uploaded_file)
        config_carregadas = False 


        # Usar os valores do JSON para preencher as configurações
        with st.expander("Configurações de Login"):
            email = st.text_input("Digite o seu email:", value=config_data.get("email", ""))
            senha = st.text_input("Digite a sua senha:", type="password", value=config_data.get("senha", ""))

        with st.expander("Configurações Gerais"):
            valor_inicial = st.number_input("Digite o valor inicial de aposta:", value=config_data.get("valor_inicial", 1.0))
            escolha_estrategia = st.selectbox("Escolha a estratégia:", ["Sequências de Cores", "Soma dos Números"], index=config_data.get("escolha_estrategia", 1))
            navegador_headless = st.checkbox("Executar o navegador em modo oculto", value=config_data.get("navegador_headless", False))

        with st.expander("Configuração de Alerta"):
            numero_vitorias_desejado = st.number_input("Digite o número de vitórias desejado para desligar:", min_value=0, step=1, value=config_data.get("numero_vitorias_desejado", 0))
            numero_alerta_derrotas = st.number_input("Número de derrotas consecutivas para ativar o alerta sonoro:", min_value=0, step=1, value=config_data.get("numero_alerta_derrotas", 0))
                
            opcoes_alerta = ["Apenas Alertar", "Alertar e Desligar"]

            # Carregar os índices das opções de alerta do JSON
            opcao_alerta_derrota_index = config_data.get("opcao_alerta_derrota_index", 0)
            opcao_alerta_vitoria_index = config_data.get("opcao_alerta_vitoria_index", 1)

            # Usar os índices para selecionar as opções de alerta
            opcao_alerta_derrota = st.selectbox("Escolha a opção de alerta para derrotas:", opcoes_alerta, index=opcao_alerta_derrota_index)
            opcao_alerta_vitoria = st.selectbox("Escolha a opção de alerta para vitórias:", opcoes_alerta, index=opcao_alerta_vitoria_index)


        desligar = False
        st.toast('Configurações carregadas!', icon='🚀')

    if st.button("Iniciar", key="iniciar_button"):
        st.write("Iniciando o código...")

        # Configurar as opções do Chrome para executar em modo headless ou visível
        chrome_options = Options()
        if navegador_headless:
            chrome_options.add_argument("--headless")

        navegador = webdriver.Chrome(options=chrome_options)

        def imprimir_log(mensagem):
            print("[LOG]", mensagem)




        col1, col2, col3, col4 = st.columns(4)
        dica1 = col1.empty() # Indicação
        contagem_01 = col2.empty() # Derrotas
        contagem_11 = col3.empty() # Vitorias
        resultado1 = col4.empty() # Resultado da aposta anterior


        col5, col6, col7,col8= st.columns(4)
        total1 = col5.empty() # Banca atual
        valor_ganho = col6.empty()  # Ganho real
        Acertos1 = col7.empty()     # Entrada
        saldo = col8.empty()   # Saldo


        col9, col10 = st.columns(2)
        exibir_df_dado = st.empty() # Tabela de dados
        ganho_hora = st.empty() # Tabela de dados


        # Substituir as datas na URL base
        base_url = 'https://blaze.com/pt/games/double'


        def aguardar_elemento_presente(locator):
            return WebDriverWait(navegador, 100).until(EC.presence_of_element_located(locator))

        def fazer_login(email, senha):
            imprimir_log("Tentando abrir on navegador... Estaremos usando o login e senha que você forneceu. ")
            navegador.get(base_url)

            # Encontrar e clicar no botão de entrar
            botao_entrar = aguardar_elemento_presente((By.XPATH, '//*[@id="header"]/div/div[2]/div/div/div[1]/a'))
            imprimir_log("Clicando no botão entrar ")
            botao_entrar.click()

            # Preencher o campo de e-mail
            campo_email = aguardar_elemento_presente((By.XPATH, '//*[@id="auth-modal"]/div/form/div[1]/div/input'))
            imprimir_log("Logando com o e-mail fornecido ")
            campo_email.send_keys(email)

            # Preencher o campo de senha
            campo_senha = aguardar_elemento_presente((By.XPATH, "//input[@name='password']"))
            imprimir_log("Logando com a senha fornecida ")
            campo_senha.send_keys(senha)

            # Clicar no botão para logar
            botao_entrar_LOGAR = aguardar_elemento_presente((By.XPATH, '//*[@id="auth-modal"]/div/form/div[4]/button'))
            imprimir_log("Apertando o botão login ")
            botao_entrar_LOGAR.click()

        def preencher_campo_valor(valor_aposta):
            campo_valor = aguardar_elemento_presente((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[2]/div[1]/div/div[1]/input'))
            campo_valor.clear()
            campo_valor.send_keys(str(valor_aposta))

        def clicar_botao_branco():
            botao_branco = aguardar_elemento_presente((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[2]/div[2]/div/div[2]/div'))
            navegador.execute_script("arguments[0].click();", botao_branco)

        def clicar_botao_vermelho():
            botao_vermelho = aguardar_elemento_presente((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[2]/div[2]/div/div[1]'))
            navegador.execute_script("arguments[0].click();", botao_vermelho)

        def clicar_botao_preto():
            botao_preto = aguardar_elemento_presente((By.XPATH, '//*[@id="roulette-controller"]/div[1]/div[2]/div[2]/div/div[3]/div'))
            navegador.execute_script("arguments[0].click();", botao_preto)



        def clicar_botao_apostar():
            css_selector_botao_apostar = 'button.red.undefined[data-testid=""]'
            botao_apostar = WebDriverWait(navegador, 200).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector_botao_apostar)))

            while botao_apostar.text != "Começar o jogo":
                time.sleep(2)
                botao_apostar = navegador.find_element(By.CSS_SELECTOR, css_selector_botao_apostar)

            navegador.execute_script("arguments[0].click();", botao_apostar)


        horario_anterior = None


        # Conectar ao banco de dados SQLite (criará um novo banco se não existir)
        conn = sqlite3.connect('roulette_data.db')
        cursor = conn.cursor()

        # Criar a tabela se ela não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roulette_data (
                id INTEGER PRIMARY KEY,
                color1 INTEGER,
                color2 INTEGER,
                color3 INTEGER,
                color4 INTEGER,
                numero1 INTEGER,
                numero2 INTEGER,
                numero3 INTEGER,
                numero4 INTEGER,
                server_seed3 TEXT,
                horario TEXT,
                dica INTEGER,
                resultados TEXT,
                Val_aposta REAL
            )
        ''')
        conn.commit()

        url = "https://blaze.com/api/roulette_games/recent"
        server_seeds = []
        contador = 0

        # Criar um dataframe vazio para armazenar os resultados
        df_concatenado = pd.DataFrame(columns=['color1', 'color2', 'color3', 'color4', 'numero1', 'numero2', 'numero3', 'numero4', 'server_seed3', 'horario', 'dica', 'resultados', 'Val_aposta'])

        dicas_resultados = []



        max_perdeu_consecutivas = 0
        perdeu_consecutivas = 0
        max_ganhou_consecutivas = 0
        ganhou_consecutivas = 0
        ganhou_counter = 0
        perdeu_counter = 0
        server_seed_counter = 0




        # Inicializar contadores
        def calcular_dica_versao_1(color0, color1, color2, color3):

            #D(P)VVVP
            if color0 == 1 and color1 == 1 and color2 == 1 and color3 == 2:
                return 2
            #D(V)PPPV
            elif color0 == 2 and color1 == 2 and color2 == 2 and color3 == 1:
                return 1

            
            #D(P)BPPP
            elif color0 == 0 and color1 == 2 and color2 == 2 and color3 == 2:
                return 2
            #D(V)BVVV
            elif color0 == 0 and color1 == 1 and color2 == 1 and color3 == 1:
                return 1
            #D(P)BPBP
            elif color0 == 0 and color1 == 2 and color2 == 0 and color3 == 2:
                return 2
            #D(V)BVPV   
            elif color0 == 0 and color1 == 1 and color2 == 2 and color3 == 1:
                return 1
            #D(V)BVBV 
            elif color0 == 0 and color1 == 1 and color2 == 0 and color3 == 1:
                return 1
            #D(V)BVPB     
            elif color0 == 0 and color1 == 1 and color2 == 2 and color3 == 0:
                return 1

            else:
                
                #D(V)VVV     
                if color0 == 1 and color1 == 1 and color2 == 1:
                    return 1
                #D(P)PPP             
                elif color0 == 2 and color1 == 2 and color2 == 2:
                    return 2
                
                #D(P)VVP                     
                elif color0 == 1 and color1 == 1 and color2 == 2:
                    return 2
                #D(V)PPV                             
                elif color0 == 2 and color1 == 2 and color2 == 1:
                    return 1
                            
                #D(V)VPP                                     
                elif color0 == 1 and color1 == 2 and color2 == 2:
                    return 1
                #D(P)PVV                                           
                elif color0 == 2 and color1 == 1 and color2 == 1:
                    return 2
                
                
                #D(P)VPV                                               
                elif color0 == 1 and color1 == 2 and color2 == 1:
                    return 2
                #D(V)PVP                                                             
                elif color0 == 2 and color1 == 1 and color2 == 2:
                    return 1
        
        
                elif color0 ==0:
                    return 1
                elif color1 ==0:
                    return 2    
                elif color2 ==0:
                    return 1 
                else:
                    return None


        def calcular_dica_versao_2(numero0, numero1, numero2, numero3):
            soma_numeros = numero0 + numero1 + numero2 + numero3
            
            if soma_numeros % 2 == 0:
                return 1  # Vermelho para par
            else:
                return 2  # Preto para ímpar




        fazer_login(email, senha)


        result_df_placeholder = st.empty()  # Este é o espaço reservado para o DataFrame



        while not desligar:
            
            
            
            try:
                response = requests.get(url)
                # Resto do código...
            except requests.exceptions.ConnectionError as e:
                imprimir_log("Erro de conexão:", str(e))
                time.sleep(5)  # Esperar um tempo antes de tentar novamente
                continue  # Retornar ao início do loop




            dados_api = json.loads(response.text)
            
            server_seed3 = dados_api[0]["server_seed"]
            
            contador += 1
            print(f"Requisição número: {contador}")
            
            if len(server_seeds) == 0:
                server_seeds.append(server_seed3)
                print(f"Primeiro dado obtido: {server_seed3}")
            elif len(server_seeds) == 1:
                if server_seed3 != server_seeds[0]:
                    server_seeds.append(server_seed3)
                    print(f"Segundo dado obtido: {server_seed3}")
                    time.sleep(28)
                else:
                    time.sleep(1)
            else:
                if server_seed3 not in server_seeds:
                    server_seeds.pop(0)
                    server_seeds.append(server_seed3)
                    server_seed_counter += 1

                    color0 = dados_api[0]["color"]
                    color1 = dados_api[1]["color"]
                    color2 = dados_api[2]["color"]
                    color3 = dados_api[3]["color"]
                    color4 = dados_api[4]["color"]
                    color5 = dados_api[5]["color"]


                    horari0o = dados_api[0]["created_at"]
                    horario1 = dados_api[1]["created_at"]
                    horario2 = dados_api[2]["created_at"]
                    horario3 = dados_api[3]["created_at"]

                    numero0 = dados_api[0]["roll"]
                    numero1 = dados_api[1]["roll"]
                    numero2 = dados_api[2]["roll"]
                    numero3 = dados_api[3]["roll"]
                    numero4 = dados_api[4]["roll"]





                    if escolha_estrategia == "Sequências de Cores":
                        dica = calcular_dica_versao_1(color0, color1, color2, color3)
                    elif escolha_estrategia == "Soma dos Números":
                        dica = calcular_dica_versao_2(numero0, numero1, numero2, numero3)
                    else:
                        imprimir_log("Estratégia inválida. Finalizando...")
                        break


                    dicas_resultados.append(dica)  # Armazenar a dica

                    penultimo_dica = dicas_resultados[-2] if len(dicas_resultados) >= 2 else None
                    ultimo_color1 = color0

                    if penultimo_dica == ultimo_color1:
                        resultado = "Ganhou"
                        perdeu_consecutivas = 0  # Reiniciar contagem de derrotas consecutivas
                        ganhou_consecutivas += 1  
                        # Incrementar sequência de vitórias consecutivas
                        if ganhou_consecutivas > max_ganhou_consecutivas:
                            max_ganhou_consecutivas = ganhou_consecutivas
                                            
                
                            
                    elif penultimo_dica is None:
                        resultado = None  # Resultado indefinido na primeira vez
                        perdeu_consecutivas = 0 
                        ganhou_consecutivas = 0
                    else:
                        resultado = "Perdeu"
                        perdeu_consecutivas += 1
                        ganhou_consecutivas = 0
                        if perdeu_consecutivas > max_perdeu_consecutivas:
                            max_perdeu_consecutivas = perdeu_consecutivas

                    if resultado == "Ganhou":
                        ganhou_counter += 1
                    elif resultado == "Perdeu":
                        perdeu_counter += 1

                    # Calcular o valor da aposta
                    valor_aposta = valor_inicial if resultado == "Ganhou" else valor_inicial * (2 ** perdeu_consecutivas)

                    if dica == 1:
                        clicar_botao_vermelho()
                        preencher_campo_valor(valor_aposta)
                        imprimir_log("Apostano VERMELHO realizada ")
                        clicar_botao_apostar()
                        
                    elif dica == 2:
                        clicar_botao_preto()
                        preencher_campo_valor(valor_aposta)
                        imprimir_log("Apostano PRETO realizada ")
                        clicar_botao_apostar()
                        
                    else:
                        # Aguardar a próxima rodada sem fazer nada
                        pass

                    insert_query = '''
                        INSERT INTO roulette_data (color1, color2, color3, color4, numero1, numero2, numero3, numero4, server_seed3, horario, dica, resultados, Val_aposta)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    data_tuple = (
                        color0, color1, color2, color3, numero0, numero1, numero2, numero3, server_seed3, horari0o, dica, resultado, valor_aposta
                    )
                    cursor.execute(insert_query, data_tuple)
                    conn.commit()

                    data = {'color1': [color0], 'color2': [color1], 'color3': [color2], 'color4': [color3], 'numero1': [numero0], 'numero2': [numero1], 'numero3': [numero2], 'numero4': [numero3], 'server_seed3': [server_seed3], 'horario': [horari0o], 'dica': [dica], 'resultados': [resultado], 'Val_aposta': [valor_aposta]}
                    df = pd.DataFrame(data)

                    # Concatenar o dataframe com o dataframe anterior
                    df_concatenado = pd.concat([df_concatenado, df])
                    result_df_placeholder.dataframe(df_concatenado.tail(10)) 

                    #colunas col1, col2, col3, col4 = st.columns(4)
                    dica1.metric("Dica", dica)
                    contagem_01.metric("Derrotas", perdeu_counter )
                    contagem_11.metric("Vitorias",ganhou_counter )
                    resultado1.metric(f"Rodadas", server_seed_counter)
                    total1.metric(f"Ultimo resultado ",resultado )
                    Acertos1.metric("Entrada", valor_aposta)
                    valor_ganho.metric("Máximo de vitórias", max_ganhou_consecutivas)    
                    saldo.metric("Máximo de derrotas", max_perdeu_consecutivas)
                    #exibir_df_dado.dataframe(df1)
                    #ganho_hora.dataframe(df_selected)



                    if ganhou_counter >= numero_vitorias_desejado:
                        if opcao_alerta_vitoria == "Alertar e Desligar":
                            st.warning(f"Alerta sonoro ativado! Número desejado de vitórias alcançado. Desligando o código.")
                            pygame.mixer.init()
                            pygame.mixer.music.load("fim.mp3")  # Substitua pelo caminho do seu arquivo de som
                            pygame.mixer.music.play()
                            desligar = True
                            navegador.quit()

                    if max_perdeu_consecutivas >= numero_alerta_derrotas:
                        pygame.mixer.init()
                        pygame.mixer.music.load("alerta.mp3")  # Substitua pelo caminho do seu arquivo de som
                        pygame.mixer.music.play()

                        if opcao_alerta_derrota == "Alertar e Desligar":
                            st.warning(f"Alerta sonoro ativado! Número desejado de derrotas consecutivas alcançado. Desligando o código.")
                            desligar = True
                            navegador.quit()                
                        
                        
                    
                    time.sleep(28)
                    
                    # Resetar o contador de requisições
                    contador = 0
                else:
                    time.sleep(1)


