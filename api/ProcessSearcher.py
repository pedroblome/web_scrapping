from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import json

class ProcessSearcher:
    def __init__(self, data_request):
        service = Service()
        options = ChromeOptions()
        self.driver = webdriver.Chrome(options, service)
        self.data_request = data_request
        self.df = pd.DataFrame(columns = ["link", "processo", "ultima_movimentacao"])
        
        self._search_pje_df()
        self.json_response = self._return_json_dataframe()
        self.driver.quit()
    
    def _search_pje_df(self):
        try:
            self.driver.get('https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam')
            
            dr = self.data_request
            if "cpf" in dr:
                info = dr["cpf"]
                search_field = self.driver.find_element(
                    By.XPATH, '//*[@id="fPP:dnp:nomeParte"]'
                )
            elif "nome" in dr:
                info = dr["nome"]
                search_field = self.driver.find_element(
                    By.XPATH, '//*[@id="fPP:dnp:nomeParte"]'
                )
            
            search_field.click()
            search_field.send_keys(info)
            
            # clica botao de pesquisa
            self.driver.find_element(
                By.XPATH, '//*[@id="fPP:searchProcessos"]'
            ).click()
            
            # wait result table
            WebDriverWait(self.driver, 200).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]')
                )
            )
            
            #localiza tabela e extrai html
            table = self.driver.find_element(
                By.XPATH, '//*[@id="fPP:processosGridPanel_body"]'
            )
            html_table = table.get_attribute("outerHTML")
            
            self._format_dataframe_pje_df(html_table)
        
        except Exception as e:
            print(e)
        
    def _format_dataframe_pje_df(self, html_table):
        soup = BeautifulSoup(html_table, "html.parser")
        
        table_data = []
        for line in soup.find_all("tr"):
            line_data = []
            link_tag = line.find(
                "a", class_="btn btn-default btn-sm"
            ) #localiza link em "detalhes do processo"

            if link_tag:
                link = link_tag.get("onclick").split("'")[3]
                link = "https://pje1g.trf1.jus.br" + link
            
            line_data += [
                column.get_text(strip = True) for column in line.find_all(["th", "td"])
            ]
        
            if "Ver detalhes do processo" in line_data:
                index_line = line_data.index("Ver detalhes do processo")
                line_data[index_line] = link
            
            table_data.append(line_data)
        
        df_pje = pd.DataFrame(
            table_data, columns=["link", "processo", "ultima_movimentacao"]
        )
        df_pje = df_pje.iloc[2:]
        df_pje.reset_index(drop=True, inplace=True)
        
        self.df = pd.concat([self.df, df_pje], ignore_index=True)
        
    # Funções para outros sites
    #...
    
    def _return_json_dataframe(self):
        try:
            json_data = self.df.to_json(orient="records")
            json_data = json.loads(json_data)
            json_data = {"items": json_data}
            return json_data
        except Exception as e:
            print(e)