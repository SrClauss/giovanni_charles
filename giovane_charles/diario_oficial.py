import pdfplumber as pdf
import re
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
import tinydb as db

db = db.TinyDB("db.json")
table = db.table("diario_oficial")

def find_initial_text_area(page):
    first_word = page.extract_words()[0]
    return first_word['x0'], first_word['bottom'] + 2

def find_next_void_y_area(page):
    x, y = find_initial_text_area(page)
    page_width = page.width
    
    while page.crop((x, y, page_width, y + 4)).extract_text() != "":
        y += 40
    return y

def find_text_area(page):
    x, y = find_initial_text_area(page)
    height = find_next_void_y_area(page)
    page_width = page.width
    corte_final = 10

    while page.crop((page_width - corte_final , y, page_width, height)).extract_text() == "":
        corte_final += 10
    return page.crop((x, y, page_width - corte_final + 10, height))

def agrupar_e_media(numeros):
    agrupados = []
    grupo_temp = []

    for numero in numeros:
        if not grupo_temp:
            grupo_temp.append(numero)
        elif numero - grupo_temp[-1] < 4:
            grupo_temp.append(numero)
        else:
            if len(grupo_temp) > 1:
                agrupados.append(sum(grupo_temp) / len(grupo_temp))
            elif len(grupo_temp) == 1:
                agrupados.append(grupo_temp[0])
            grupo_temp = [numero]

    if len(grupo_temp) > 1:
        agrupados.append(sum(grupo_temp) / len(grupo_temp))
    elif len(grupo_temp) == 1:
        agrupados.append(grupo_temp[0])

    return agrupados

def define_void_areas(page_crop):
    initial_x, initial_y, final_x, final_y = page_crop.bbox
    void_areas = [initial_x]
    tq = tqdm(total=final_x - initial_x, desc="Defining void areas")
    while initial_x < final_x - 3:
        if page_crop.crop((initial_x, initial_y, initial_x + 3, final_y)).extract_text() == "":
            void_areas.append(initial_x)

        
        initial_x += 3
        tq.update(3)
    void_areas.append(final_x)

    void_areas = agrupar_e_media(void_areas)
    return void_areas
 
def extract_text(page_crop, page):

    void_areas = define_void_areas(page_crop)
    

    _, initial_y, _, final_y = page_crop.bbox

    table = page_crop.extract_table({
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
        "explicit_vertical_lines": void_areas,
        "explicit_horizontal_lines": [initial_y, final_y]
    })

    text = ""
    for row in table[0]:
        for cell in row:
            text += cell
        text += "\n"
    return text

def extract_page_text(pdf):

    pages = pdf.pages
    text = ""
    tqdm_pages = tqdm(pages, desc="Extracting text", total=len(pages))
    for i in range(len(pages)):
        page_crop = find_text_area(pages[i])
        text += extract_text(page_crop, i)
        tqdm_pages.update(1)
    return text

def find_elements(path):
  
    pdf_file = pdf.open(path)
    text = extract_page_text(pdf_file)
 

    text = text.replace("\n", " ")
    inicio = text.find("Placa:")
    text = text[inicio:]
    text = text.split("Placa:")
 

    text = [x for x in text if x != ""]


    tq = tqdm(total=len(text), desc="Extracting elements")
    
    for i in range(len(text)):
        text[i] = "Placa:" + text[i]
    result = []
    errors = []
    for t in text:

        dictionary = {}

        try:
            placa = re.search(r"Placa:[\w\s/.]+", t).group()
            dictionary["placa"] = placa.replace("Placa: ", "").replace(" Chassi",  "").replace("Placa:", "").upper()
        except Exception as e:
            
            #print(t)
            #print("erro de placa")

            
            errors.append({"string": t, "error": e})
            continue
        try:
            chassi = re.search(r"Chassi:[\w\s/.]+", t).group()
            dictionary["chassi"] = chassi.replace("Chassi: ", "").replace(" Marca/Modelo",  "").upper()
        except Exception as e:

            #print(t)
            #print("erro de chassi")
            errors.append({"string": t, "error": e})
            continue
        
        try:             
            marca_modelo = re.search(r"Marca/Modelo:([\w\s/.-]+)", t, re.IGNORECASE).group(1)
            dictionary["marca_modelo"] = marca_modelo.strip().upper()
        except:
            try:
                marca_modelo = re.search(r"Marca/ Modelo:([\w\s/.-]+)", t, re.IGNORECASE).group(1)
                dictionary["marca_modelo"] = marca_modelo.strip().upper()
            except Exception as e:                
                #print(t)
                #print("erro de marca_modelo")
                errors.append({"string": t, "error": e})
                continue
        try: 
            ano_fabricacao = re.search(r"Ano Fab.:[\w\s/]+", t).group()
            dictionary["ano_fabricacao"] = ano_fabricacao.replace("Ano Fab.:", "").replace(" Prop", "").upper()

        except:
            try:
                ano_fabricacao = re.search(r"Ano Fab .:[\w\s/]+", t).group()
                dictionary["ano_fabricacao"] = ano_fabricacao.replace("Ano Fab .:", "").replace(" Prop", "").upper()
            except Exception as e:
                #print(t)
                #print("erro de ano_fabricacao")
                errors.append({"string": t, "error": e})
                continue
        try:
            proprietario = re.search(r"Prop.:[\w\s]+", t).group()
            dictionary["proprietario"] = proprietario.replace("Prop.: ", "")
        except:
            try:
                proprietario = re.search(r"Prop .:[\w\s]+", t).group().replace("Prop.: ", "")
            except Exception as e:
                #print(t)
                #print("erro de proprietario")
                errors.append({"string": t, "error": e})
                continue

        tq.update(1)
        result.append(dictionary)
            
    print("Elements extracted")
    for error in errors:
        print(error)


    table.insert_multiple(result)


