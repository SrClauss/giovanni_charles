from tkinter import Tk, Button, Frame, filedialog, simpledialog, Listbox
import tkinter
from diario_oficial import find_elements
from tabela_leilao import extract_data
import pdfplumber
import cruza_dados
from tinydb import TinyDB
from tqdm import tqdm
from datetime import datetime
import os
import shutil
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
    print(file)
    find_elements(file)
    remove_duplicates_diario()
        
def rename_and_move_jsons(details: str):
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"arquivados/{date}_{details}.json"

    #faça uma copia de db.json para arquivdos com o nome filename
    shutil.copy("db.json", filename)
    #apague o conteudo de db.json
    db.drop_tables()

    print("JSONs arquivados com sucesso")




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

def show_list_dialog():
    dialog = ListDialog(None)
    desarquivar_jsons(dialog.result)

def desarquivar_jsons(filename):
    global db
    db.close()
    shutil.copy(f"arquivados/{filename}", "db.json")
    print("JSONs desarquivados com sucesso")
    db = TinyDB('db.json')
    global leilao
    global diario_oficial

    leilao = db.table('leilao')
    diario_oficial = db.table('diario_oficial')
    

 
  
if __name__ == "__main__":
    tk = Tk()
    tk.geometry("400x500")
    tk.resizable(False, False)
    frame = Frame(tk, width=300, height=300, padx=20, pady=20)
    frame.pack()
    button_carregar_diario = Button(frame, text="Carregar Diário Oficial", width=200, pady=15, command= lambda: open_file_and_find_diario())
    button_carregar_diario.pack(pady=10, padx=10)
    button_carregar_relacao = Button(frame, text="Carregar Relação de Veículos Arrematados", width=200, pady=15, command=lambda: open_file_and_find_leilao())
    button_carregar_relacao.pack(pady=10, padx=10)
    button_cruzar_dados = Button(frame, text="Cruzar Dados", width=250, pady=15, command=lambda: cruza_dados.cruza_dados())
    button_cruzar_dados.pack(pady=10, padx=10)
    button_arquivar = Button(frame, text="Arquivar JSONs", width=250, pady=15, command=lambda: open_file_dialog())
    button_arquivar.pack(pady=10, padx=10)
    button_desarquivar = Button(frame, text="Desarquivar JSONs", width=250, pady=15, command=lambda:show_list_dialog())
    button_desarquivar.pack(pady=10, padx=10)


 

    tk.mainloop()
