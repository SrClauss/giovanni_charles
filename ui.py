from tkinter import Tk, Button, Frame, filedialog, simpledialog, Listbox
from tkcalendar import DateEntry
import tkinter
from  diario_oficial import find_elements, baixar_intervalo
from tabela_leilao import extract_data, extract_data_new_model
import pdfplumber
import cruza_dados
from tinydb import TinyDB
from tqdm import tqdm
from datetime import datetime
import os
import shutil



db_dados_cruzados = TinyDB('db_dados_cruzados.json')
db = TinyDB('db.json')
leilao = db.table('leilao')
diario_oficial = db.table('diario_oficial')

def remove_duplicates_leilao():
    vistos = set()
    duplicados = []
    print("Removendo itens duplicados em leilão")
    tq = tqdm(total=len(leilao.all()), desc="Varrendo BD 'leilao'")
    for item in leilao.all():
        if item['chassi'] in vistos:
            duplicados.append(item)
        else:
            vistos.add(item['chassi'])
        tq.update(1)
    tq.close()
    tq = tqdm(total=len(duplicados), desc="Removendo itens duplicados...")   
    for item in duplicados:
        leilao.remove(doc_ids=[item.doc_id])
        tq.update(1)
        
    tq.close()

def remove_duplicates_diario():
    vistos = set()
    duplicados = []

    print("Removendo itens duplicados em diário oficial")
    tq = tqdm(total=len(diario_oficial.all()), desc="Varrendo BD 'diario_oficial'")
    for item in diario_oficial.all():
        if item['chassi'] in vistos:
            duplicados.append(item)
        else:
            vistos.add(item['chassi'])
        tq.update(1)
    tq.close()
    tq = tqdm(total=len(duplicados), desc="Removendo itens duplicados...")
    for item in duplicados:
        diario_oficial.remove(doc_ids=[item.doc_id])
        tq.update(1)
    tq.close()


def open_file_and_find_diario():
    file = filedialog.askopenfilename()
    if not file:
        return None
    find_elements(file)
    remove_duplicates_diario()
        
def rename_and_move_jsons(details: str):
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_db = f"arquivados/db_{date}_{details}.json"
    filename_dados_cruzados = f"arquivados/dados_cruzados_{date}_{details}.json"

    #faça uma copia de db.json para arquivdos com o nome filename
    shutil.copy("db.json", filename_db)
    shutil.copy("db_dados_cruzados.json", filename_dados_cruzados)
    #apague o conteudo de db.json
    db.drop_tables()
    db_dados_cruzados.drop_tables()
    

    print("JSONs arquivados com sucesso")

import tkinter as tk
from tkinter import Toplevel, Frame, Button, Label



def open_file_dialog():
    resposta = simpledialog.askstring("Input", "Digite a descrição do arquivo")
    if resposta:
        rename_and_move_jsons(resposta)
    else:
        return None
def open_file_and_find_leilao():
    
    file = filedialog.askopenfilename()
    extract_data(pdfplumber.open(file))
    remove_duplicates_leilao()
    print("Dados extraídos com sucesso")

def open_file_and_find_leilao_new_model():
    file = filedialog.askopenfilename()
    extract_data_new_model(pdfplumber.open(file))
    remove_duplicates_leilao()
    print("Dados extraídos com sucesso")

class ListDialog(simpledialog.Dialog):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
       

    def body(self, master):
        self.title("Escolha o arquivo a ser desarquivado")
        self.listbox = Listbox(master, width=70)
        self.listbox.pack()
        for item in os.listdir("arquivados"):
            self.listbox.insert(tkinter.END, item)
        return self.listbox
    
    def apply(self) -> None:
        self.result = self.listbox.get(self.listbox.curselection())
class DateRangeDialog(simpledialog.Dialog):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
       

    def body(self, master):

        self.title("Escolha o arquivo a ser desarquivado")
        self.calendar_inicio = DateEntry(master=master, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.calendar_inicio.grid(row=0, column=0, padx=10, pady=10)
        self.calendar_fim = DateEntry(master=master, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.calendar_fim.grid(row=0, column=1, padx=10, pady=10)
   
    def apply(self) -> None:
        self.result = (self.calendar_inicio.get_date(), self.calendar_fim.get_date())
def show_date_range_dialog():
    dialog = DateRangeDialog(None)

    baixar_intervalo(dialog.result[0], dialog.result[1])
    
def show_list_dialog():
    dialog = ListDialog(None)
    desarquivar_jsons(dialog.result)

def desarquivar_jsons(filename):
    global db
    global db_dados_cruzados
    db.close()
    db_dados_cruzados.close()
    shutil.copy(f"arquivados/{filename}", "db.json")
    shutil.copy(f"arquivados/dados_cruzados_{filename.split('_')[1]}", "db_dados_cruzados.json")
    print("JSONs desarquivados com sucesso")
    db = TinyDB('db.json')
    global leilao
    global diario_oficial

    leilao = db.table('leilao')
    diario_oficial = db.table('diario_oficial')
    
    

 
  
if __name__ == "__main__":
    tk = Tk()
    tk.geometry("400x600")
    tk.resizable(False, False)
    frame = Frame(tk, width=300, height=300, padx=20, pady=20)
    frame.pack()
    button_carregar_diario = Button(frame, text="Carregar Diário Oficial", width=200, pady=15, command= lambda: open_file_and_find_diario())
    button_carregar_diario.pack(pady=10, padx=10)
    button_carregar_relacao = Button(frame, text="Carregar Relação de Veículos Arrematados", width=200, pady=15, command=lambda: open_file_and_find_leilao())
    button_carregar_relacao.pack(pady=10, padx=10)
    button_carregar_relacao_new_model = Button(frame, text="Carregar Relação de Veículos Arrematados (Novo Modelo)", width=200, pady=15, command=lambda: open_file_and_find_leilao_new_model())
    button_carregar_relacao_new_model.pack(pady=10, padx=10)
    button_cruzar_dados = Button(frame, text="Cruzar Dados", width=250, pady=15, command=lambda: cruza_dados.cruza_dados())
    button_cruzar_dados.pack(pady=10, padx=10)
    button_arquivar = Button(frame, text="Arquivar JSONs", width=250, pady=15, command=lambda: open_file_dialog())
    button_arquivar.pack(pady=10, padx=10)
    button_desarquivar = Button(frame, text="Desarquivar JSONs", width=250, pady=15, command=lambda:show_list_dialog())
    button_desarquivar.pack(pady=10, padx=10)
    button_baixar_range = Button(frame, text="Baixar Diarios em Lote", width=250, pady=15, command=lambda:show_date_range_dialog())
    button_baixar_range.pack(pady=10, padx=10)


 

    tk.mainloop()
