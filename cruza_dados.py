import tinydb
import openpyxl
import tkinter
from tkinter import filedialog

db_dados_cruzados = tinydb.TinyDB("db_dados_cruzados.json")



def normatiza_nomes(nome):
    conectores_sempre_minusculos = [
        "de", "da", "do", "dos", "di", "das", "d'", "e", "y", "van", "von", "de la", "del",
        "a", "para", "por", "em", "al", "à", "às", "of", "in", "iz", "ov", "al", "bin", "ibn", "abu", "um", "bint",
        "el", "la", "los", "las", "lo", "le", "l'", "les", "un", "una", "unos", "unas", "the", "a", "an", "ou", "and", "or", "i", "ili"
    ]
    nome = nome.lower()
    nome = nome.split(" ")
    for i in range(len(nome)):
        if nome[i] not in conectores_sempre_minusculos:
            nome[i] = nome[i].capitalize()
    nome = " ".join(nome)
    return nome
    

def gera_peticoes():
    pass
def cruza_dados():
    db = tinydb.TinyDB('db.json')
    diario_oficial = db.table('diario_oficial')
    leilao = db.table('leilao')

    def processa_nomes(nome):
        words = ["Banco ", "Bco. ","Bco.", "Bv", "Bco "]
        for word in words:
            if word in nome:
                nome = (nome.split(word)[0] + " | " + word + " " + nome.split(word)[1]).replace("- ", "").replace(" -", "").replace(" - ", "").replace("-","")
        return nome

    lista_diario_oficial = diario_oficial.all()
    lista_leilao = leilao.all()
    sorted(lista_diario_oficial, key=lambda x: x['chassi'])
    sorted(lista_leilao, key=lambda x: x['chassi'])

    cruzamento = []
    for automovel in lista_leilao:
        for proprietario in lista_diario_oficial:
            if automovel['chassi'].upper() == proprietario['chassi'].upper() or automovel['placa'].replace(
                    "-", "").upper() == proprietario['placa'].replace("-", "").upper():
                cruzamento.append({
                    "proprietario": normatiza_nomes(processa_nomes(proprietario['proprietario'])),
                    "placa": automovel['placa'],
                    "modelo": automovel['modelo'],
                    "ano": automovel['ano'],
                    "chassi": automovel['chassi'],
                    "data_aprensao": automovel['data_aprensao'],
                    "data_liberacao": automovel['data_liberacao'],
                    "data_nf": automovel['data_nf'],
                    "diarias": automovel['diarias'],
                    "reboque": automovel['reboque'],
                    "debito_patio": automovel['debito_patio'],
                    "multas": automovel['multas'],
                    "tx_licenciamento": automovel['tx_licenciamento'],
                    "ipva": automovel['ipva'],
                    "debito": automovel['debitos'],
                    "arremate": automovel['arremate'],
                    "total": automovel['saldo'],
                    
                    
                })





    db_dados_cruzados.insert_multiple(cruzamento)
    gera_peticoes()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Proprietario', 'Placa', 'Modelo', 'Ano', 'Chassi', 'Data Apreensao', 'Data Liberacao', 'Data NF', 'Diarias', 'Reboque', 'Debito Patio', 'Multas', 'Taxa Licenciamento', 'IPVA', 'Debito', 'Arremate', 'Total'])
    for r in cruzamento:
        ws.append([r['proprietario'], r['placa'], r['modelo'], r['ano'], r['chassi'], r['data_aprensao'], r['data_liberacao'], r['data_nf'], r['diarias'], r['reboque'], r['debito_patio'], r['multas'], r['tx_licenciamento'], r['ipva'], r['debito'], r['arremate'], r['total']])
    file = filedialog.asksaveasfilename(defaultextension='.xlsx')
    wb.save(file)
    print('Dados cruzados com sucesso')
