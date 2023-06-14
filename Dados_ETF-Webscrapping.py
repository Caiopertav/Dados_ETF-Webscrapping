#Importar as bibliotecas.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

#requisições na internet.

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

#site com informações de ETF
driver.get('https://www.etf.com/etfanalytics/etf-finder') 

#Achar todos os elementos necessários dentro do HTML do site
#  Expandindo a tabela para 100 itens.
time.sleep(5)  #espera os segundos necessários para carregar pagina
#sempre fazer a busca no html, com navegador aberto pelo bot, pois muda com bot
botao_100 = driver.find_element("xpath",
                               '/html/body/div[5]/section/div/div[3]/section/div/div/div/div/div[2]/section[2]/div[2]/section[2]/div[1]/div/div[4]/button/label/span')

botao_100.click()

#driver.execute_script("arguments[0].click();", botao_100)   para caso click nao funcione, acontece em alguns sites

#Achar todos os elementos necessários dentro do HTML do site
#Pegando o número de páginas da tabela. Garantindo que code funcione msm com numero variando
numero_paginas = driver.find_element("xpath", '//*[@id="totalPages"]')

numero_paginas = numero_paginas.text.replace("of ", "")

numero_paginas = int(numero_paginas)


#Lendo a tabela de dados em html com pandas

#pega elemento da pagina através de xpath poderia ser o full
elemento = driver.find_element("xpath", '//*[@id="finderTable"]')
#pega apenas atributo html do elemento que pegamos
html_tabela = elemento.get_attribute('outerHTML')
#read do pandas pra html 
tabela = pd.read_html(str(html_tabela))[0]


lista_tabela_por_pagina = []
# estrtura de repetição, onde vai de 1 a ultima pagina que foi pega anteriormente, como elemento da pagina.
elemento = driver.find_element("xpath", '//*[@id="finderTable"]')

for pagina in range(1, numero_paginas + 1):
    
    html_tabela = elemento.get_attribute('outerHTML')
    
    tabela = pd.read_html(str(html_tabela))[0]
    
    lista_tabela_por_pagina.append(tabela)
#avança dentro da tabela cada pagina dentro do loop todas as vezes, em vez de mudar a pagina, acho que vária com estrutura do site    
    botao_avancar_pagina = driver.find_element("xpath", '//*[@id="nextPage"]')
#aperta o botão se nao pegar tem que fazer a alteração pro comentário la em cima debotões, o erro segue desconhecido.  
    botao_avancar_pagina.click()
    
#concatenar todas as tabelas em um data frame    
tabela_cadastro_etfs = pd.concat(lista_tabela_por_pagina)



#Ler a tabela de dados - Preenchendo um campo no site pra voltar as páginas
#objetivo e voltar pra pag1 da tabela 
formulario_de_voltar_pagina = driver.find_element("xpath", '//*[@id="goToPage"]')
#limpar o campo de digitação
formulario_de_voltar_pagina.clear()
#send envia uma tecla, queremos pag1
formulario_de_voltar_pagina.send_keys("1")
#tecla enter pra dar entrada no comando
formulario_de_voltar_pagina.send_keys(u'\ue007')



#Ler a tabela de dados - Lendo a tabela de dados de rentabilidade.

#pegamos o full em vez do xpath para garantir ja que havia varios elementos,ir para aba performace da tabela.
botao_mudar_pra_performance = driver.find_element("xpath", '/html/body/div[5]/section/div/div[3]/section/div/div/div/div/div[2]/section[2]/div[2]/ul/li[2]/span')

botao_mudar_pra_performance.click()

# a partir daqui é tudo igual

lista_tabela_por_pagina = []

elemento = driver.find_element("xpath", '//*[@id="finderTable"]')

for pagina in range(1, numero_paginas + 1):
    
    html_tabela = elemento.get_attribute('outerHTML')
    
    tabela = pd.read_html(str(html_tabela))[0]
    
    lista_tabela_por_pagina.append(tabela)
    
    botao_avancar_pagina = driver.find_element("xpath", '//*[@id="nextPage"]')
    
    driver.execute_script("arguments[0].click();", botao_avancar_pagina)
    
    
tabela_rentabilidade_etfs = pd.concat(lista_tabela_por_pagina)


driver.quit() #fecha o navegador


#Construindo a tabela final.
tabela_rentabilidade_etfs = tabela_rentabilidade_etfs.set_index("Ticker")
tabela_rentabilidade_etfs = tabela_rentabilidade_etfs[['1 Year', '3 Years', '5 Years']]
tabela_cadastro_etfs = tabela_cadastro_etfs.set_index("Ticker")
base_de_dados_final = tabela_cadastro_etfs.join(tabela_rentabilidade_etfs, how = 'inner')

base_de_dados_final