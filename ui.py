from tkinter import Tk, Button, Frame, filedialog
from diario_oficial import find_elements
from tabela_leilao import extract_data
import pdfplumber
import cruza_dados



def open_file_and_find_diario():
    file = filedialog.askopenfilename()
    find_elements(file)
    

def open_file_and_find_leilao():

    file = filedialog.askopenfilename()
    extract_data(pdfplumber.open(file))

if __name__ == "__main__":
    tk = Tk()
    tk.geometry("400x350")
    frame = Frame(tk, width=300, height=300, padx=20, pady=20)
    frame.pack()
    button_carregar_diario = Button(frame, text="Carregar Diário Oficial", width=200, pady=15, command=lambda: open_file_and_find_diario())
    button_carregar_diario.pack(pady=10, padx=10)
    button_carregar_relacao = Button(frame, text="Carregar Relação de Veículos Arrematados", width=200, pady=15, command=lambda: open_file_and_find_leilao())
    button_carregar_relacao.pack(pady=10, padx=10)
    button_cruzar_dados = Button(frame, text="Cruzar Dados", width=250, pady=15, command=cruza_dados.cruza_dados)
    button_cruzar_dados.pack(pady=10, padx=10)
    tk.mainloop()