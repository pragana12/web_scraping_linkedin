# Importando bibliotecas necessárias
import time
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import mysql.connector
from mysql.connector import Error
import re

# Configurações do banco de dados
db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'dados_linkind'
table_name = 'vagas_dados1'

# Configuração do Chrome
options = webdriver.ChromeOptions()
options.add_argument('--profile-directory=Default')
options.add_argument('--user-data-dir=C:\\Temp\\ChromeProfile')
options.add_argument("start-maximized")
driver = webdriver.Chrome(options=options)
driver.set_window_size(1024, 800)
driver.maximize_window()

# Configurações de Login
email_usuario = 'seu_email@gmail.com'
senha_usuario = 'suas_enha'

# Definições de URL
url = "https://www.linkedin.com/login/"
url_vagas = 'https://www.linkedin.com/jobs/search/?currentJobId=3763296160&keywords=analista%20de%20dados&origin=SWITCH_SEARCH_VERTICAL'


# Função para realizar o login no LinkedIn
def realizar_login(email, senha):
    campo_email = driver.find_element(By.XPATH, '//*[@id="username"]')
    campo_senha = driver.find_element(By.XPATH, '//*[@id="password"]')
    campo_email.send_keys(email)
    campo_senha.send_keys(senha)
    campo_senha.send_keys(Keys.RETURN)
    return driver

# Função para extrair dados das vagas no LinkedIn
def extrair_dados_vagas():

    driver.implicitly_wait(5)
    time.sleep(5)
    elementos = driver.find_elements(By.CLASS_NAME, 'ember-view.jobs-search-results__list-item')
    # Antes do loop
    start_index = 1

    # Início do loop while
    while True:
        # Obter elementos
        elementos = driver.find_elements(By.CLASS_NAME, 'ember-view.jobs-search-results__list-item')

        # Loop para processar elementos
        for i, elemento in enumerate(elementos, start=start_index):
            try:
                elemento.click()
                time.sleep(2)

                # Extrair título da vaga
                try:
                    titulo = driver.find_element(By.CLASS_NAME, 'jobs-search__job-details--wrapper').text
                    linhas = titulo.strip().split('\n')
                    titulo = linhas[0]
                except:
                    titulo = "null"
                
                # Extrair informações sobre a empresa
                try:
                    empresa = driver.find_element(By.CLASS_NAME, 'jobs-company__box').text
                    indice_inicio = empresa.find("empresa")
                    indice_fim = empresa.find("seguidores", indice_inicio)
                    empresa = empresa[indice_inicio + 7:indice_fim]
                    empresa = re.sub(r'\d', '', empresa)
                    empresa = re.sub(r'\n', ' ', empresa)
                except:
                    empresa = "null"

                # Extrair localização da vaga
                try:
                    local = driver.find_element(By.CLASS_NAME, 'job-details-jobs-unified-top-card__primary-description-container').text    
                    indice_inicio = local.find("·")
                    indice_fim = local.find(",", indice_inicio)
                    local = local[indice_inicio + 1:indice_fim]
                except:
                    local = 'null'

                # Extrair informações adicionais
                try:    
                    informacoes = driver.find_element(By.CLASS_NAME, 'mt3.mb2').text
                    informacoes = informacoes[:10]
                except:
                    informacoes = 'null'
                
                # Extrair descrição da vaga
                try:    
                    descricao = driver.find_element(By.CLASS_NAME, 'jobs-box__html-content.jobs-description-content__text.t-14.t-normal').text
                except:
                    descricao = 'null'

                # Extrair competências necessárias
                try:    
                    competencias = driver.find_element(By.XPATH, '//*[@id="how-you-match-card-container"]/section[2]/div/div[1]/div[1]/div/a').text
                except:
                    competencias = 'null'

                # Extrair ramo da empresa
                try:    
                    ramo = driver.find_element(By.CLASS_NAME, 't-14.mt5').text
                    ramo = re.sub(r'\d.*$', '', ramo)
                except:
                    ramo = 'null'

                # Conectar ao banco de dados e inserir dados
                try:
                    connection = mysql.connector.connect(
                        host=db_host,
                        user=db_user,
                        password=db_password,
                        database=db_name
                    )

                    cursor = connection.cursor()

                    sql_query = f"INSERT INTO {table_name} (titulo, empresa, local1, informacoes, descricao, competencias, ramo) " \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    values = (titulo, empresa, local, informacoes, descricao, competencias, ramo)
                    cursor.execute(sql_query, values)

                    connection.commit()

                    print('Dados inseridos no banco de dados.')
                except Error as e:
                    print('Erro ao conectar ou inserir dados no banco de dados:', e)
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
                

                # Exibir informações no console
                print(f"Título: {titulo}")
                print('------------------------------------------------------------------------------------')
                print(f"Empresa: {empresa}")
                print('------------------------------------------------------------------------------------')
                print(f"Local: {local}")
                print('------------------------------------------------------------------------------------')
                print(f"Informações: {informacoes}")
                print('------------------------------------------------------------------------------------')
                print(f"Descrição: {descricao}")
                print('------------------------------------------------------------------------------------')
                print(f"Competências: {competencias}")
                print('------------------------------------------------------------------------------------')
                print(f"Ramo: {ramo}")

                time.sleep(5)
                print(f"Clicou no elemento {i}. Aguardando 5 segundos...")# Restante do código ...

            except StaleElementReferenceException as stale_exception:
                print(f"Erro ao extrair dados da vaga (StaleElementReferenceException): {stale_exception}")

            # Encontra o elemento com conteúdo das vagas pelo XPath
            elemento = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[1]/div')

            # Usa JavaScript para rolar o elemento para baixo (200 pixels)
            driver.execute_script("arguments[0].scrollTop += 200;", elemento)
            time.sleep(2)
            if i % 25 == 0:
                proximo_start = i + 1
                novo_url = f"{url_vagas}&start={proximo_start}"
                print(novo_url)
                driver.get(novo_url)
                driver.implicitly_wait(5)
                start_index = proximo_start

        # Intervalo entre extrações
        time.sleep(5)  # Aguardar 5 minutos antes de buscar novos elementos

# Abrir a página de login
driver.get(url)
driver.implicitly_wait(5)

# Verificar se o usuario ja está logado.
if len(driver.find_elements(By.XPATH, '//*[@id="username"]')) > 1:
    driver = realizar_login(email_usuario, senha_usuario)
else:
    pass

# Extrair dados das vagas
driver.get(url_vagas)
driver.implicitly_wait(5)
extrair_dados_vagas()

# Fechar o navegador
driver.quit()
