import re
from tqdm import tqdm
import tinydb as db
import fitz
import requests
from tqdm import tqdm
from colorama import Fore
import os
from datetime import date, timedelta



table = db.TinyDB("db.json").table("diario_oficial")


def baixar_diario(ano, mes, dia):
    caderno = 1
    
    while True:
        nome_arquivo = f"caderno{caderno}_{ano}-{str(mes).zfill(2)}-{str(dia).zfill(2)}.pdf"
        url = f"https://www.jornalminasgerais.mg.gov.br/modulos/www.jornalminasgerais.mg.gov.br//diarioOficial/{ano}/{str(mes).zfill(2)}/{str(dia).zfill(2)}/jornal/{nome_arquivo}"
        print(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            t = tqdm(total=total_size, unit='iB', unit_scale=True, 
                    bar_format=f"Baixando arquivo {nome_arquivo} {Fore.GREEN}{{l_bar}}{{bar}}{{r_bar}}{Fore.RESET}")
            
            with open(f"pdf/{nome_arquivo}", "wb") as file:
                for data in response.iter_content(block_size):
                    t.update(len(data))
                    file.write(data)
            t.close()
        
            
            if total_size != 0 and t.n != total_size:
                print("Erro ao baixar o PDF")
                os.remove(f"pdf/{nome_arquivo}")
                break
            else:
                print("PDF baixado com sucesso")
                find_elements(f"pdf/{nome_arquivo}")
                caderno += 1
        else:
            print("Erro ao baixar o PDF")
            print(response.status_code)
            print(response.text)
            break

def baixar_intervalo(data_inicio, data_fim):    
    while data_inicio <= data_fim:
        baixar_diario(data_inicio.year, data_inicio.month, data_inicio.day)
        data_inicio += timedelta(days=1)
    
    print("Fim do download")
        
        
def extract_page_text(pdf_file):
    document = fitz.open(pdf_file)
    full_text = ""

    for page_num in tqdm(range(len(document)), desc=f"Extracting text from {pdf_file}"):
        page = document.load_page(page_num)
        rect = page.rect
        clip = fitz.Rect(rect.x0, rect.y0 + 90, rect.x1, rect.y1 - 50)
        full_text += page.get_text("text", clip=clip)
        
    
    return full_text




def find_elements(path):
    text = extract_page_text(path).replace("\n", " ").replace("Marca/ Modelo: ", "Marca/Modelo: ").replace("  ", " ")
    group = text.split("veículos se encontram recolhidos no(s) depósito(s) abaixo relacionado(s), na cidade de")[1:]
   
    group_tuples  = []

    for g in group:
        cidade = g.split(" Placa: ")[0]
        texto = g.replace(cidade, "")
        group_tuples.append((cidade,texto))
        


    padrao = r"Placa:\s*(?P<placa>\w+)\s*Chassi:\s*(?P<chassi>\w+)\s*Marca/Modelo:\s*(?P<marca_modelo>[\w\s/]+)\s*Ano Fab\.\:\s*(?P<ano_fab>\d{4})\s*Prop\.\:\s*(?P<proprietario>[\w\s\.\:]+)\s*/"
    
    
    
    veiculos_cidade = []
    for group_tuple in tqdm(group_tuples, desc="Processing groups"):
        cidade, texto = group_tuple
     
        for match in re.finditer(padrao, texto):
            veiculo = match.groupdict()
            veiculo["cidade"] = cidade.split(".")[0]
            veiculo["patio"] = cidade.split(".")[1]
            veiculo["publicacao"] = path
            veiculos_cidade.append(veiculo)
    print(f"Encontrados {len(veiculos_cidade)} veículos em {path}")
    table.insert_multiple(veiculos_cidade)