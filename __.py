import pdfplumber as pdf
import re
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
import tinydb as db

db = db.TinyDB("db.json")
table = db.table("diario_oficial")

def text_between(text:str, word_init:str, word_end:str):
    position_init = text.find(word_init)
    if position_init == -1:
        raise Exception(f"Word {word_init} not found")
    position_init += len(word_init)
    position_end = text.find(word_end)
    if position_end == -1:
        raise Exception(f"Word {word_end} not found")
    return text[position_init:position_end].strip().upper()


def text_proprietario(text:str):
    position_init = text.find('Prop.:')
    increment = 6

    if position_init == -1:
        position_init = text.find('Prop .:')
        increment = 7
    if position_init == -1:
        position_init = text.find('Prop  .:')
        increment = 8
    if position_init == -1:
        position_init = text.find(' Prop')
        increment = 5

    position_init += increment
    position_end = text[position_init:].find('/')
    if position_end != -1:
        return text[position_init:position_init+position_end].strip()
    return text[position_init:].strip()
def text_ano(text:str):
    position_init = text.find('Fab .:')
    increment = 6
    if position_init == -1:
        position_init = text.find('Fab.:')
        increment = 5
    if position_init == -1:
        position_init = text.find('Ano Fab')
        increment = 8
    if position_init == -1:
        raise Exception('Ano não encontrado')

    return text[position_init+increment:position_init+increment+5].strip() 
        
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
    import json
    json.dump(text, open("text.json", "w"))

    for t in text:

        dictionary = {}
   
        try:
            dictionary["placa"] = text_between(t, "Placa:", "Chassi:")
        except Exception as e:
            dictionary["placa"] = ""
            print(f"Error in placa: {e}")

        try:
            dictionary["chassi"] = text_between(t, "Chassi:", " Marca")
        except Exception as e:
            dictionary["chassi"] = ""
            print(f"Error in chassi: {e}")

        try:
            dictionary["modelo"] = text_between(t, "Modelo:", " Ano Fab")
        except Exception as e:
            try:
                dictionary["modelo"] = text_between(t, "Modelo:", " Ano")
            except Exception as e:
                dictionary["modelo"] = ""
                print(f"Error in modelo: {e}")
        try:
            dictionary["ano"] = text_ano(t)

        except Exception as e:
            dictionary["ano"] = ""
            print(f"Error in ano: {e}")

        
        try:
            dictionary["proprietario"] = text_proprietario(t)
        except Exception as e:
            dictionary["proprietario"] = ""
            print(f"Error in proprietario: {e}")

        result.append(dictionary)


        
      

            
    print("Elements extracted")
    for error in errors:
        print(error)

    table.insert_multiple(result)


