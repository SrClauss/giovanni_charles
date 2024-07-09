from tkinter import Tk, Button, Frame, filedialog
from diario_oficial import find_elements
from tabela_leilao import extract_data
import pdfplumber
import cruza_dados
from tinydb import TinyDB
from tqdm import tqdm

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
        


def open_file_and_find_leilao():
    file = filedialog.askopenfilename()
    print(file)
    extract_data(pdfplumber.open(file))
    remove_duplicates_leilao()
           
if __name__ == "__main__":
    tk = Tk()
    tk.geometry("400x350")
    frame = Frame(tk, width=300, height=300, padx=20, pady=20)
    frame.pack()
    button_carregar_diario = Button(frame, text="Carregar Diário Oficial", width=200, pady=15, command= lambda: open_file_and_find_diario())
    button_carregar_diario.pack(pady=10, padx=10)
    button_carregar_relacao = Button(frame, text="Carregar Relação de Veículos Arrematados", width=200, pady=15, command=lambda: open_file_and_find_leilao())
    button_carregar_relacao.pack(pady=10, padx=10)
    button_cruzar_dados = Button(frame, text="Cruzar Dados", width=250, pady=15, command=lambda: cruza_dados.cruza_dados())
    button_cruzar_dados.pack(pady=10, padx=10)
    buttons = [button_carregar_diario, button_carregar_relacao, button_cruzar_dados]

    tk.mainloop()
