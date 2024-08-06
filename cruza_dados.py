import tinydb
import openpyxl
import tkinter
from tkinter import filedialog
def cruza_dados():
    db = tinydb.TinyDB('db.json')
    diario_oficial = db.table('diario_oficial')
    leilao = db.table('leilao')

    def processa_nomes(nome):
        words = ["Banco ", "Bco. ","Bco.", "Bv", "Bco "]
        for word in words:
            if word in nome:
                nome = nome.split(word)[0].replace("- ", "").replace(" -", "").replace(" - ", "").replace("-","")
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
                    "proprietario": processa_nomes(proprietario['proprietario']),
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
                    "debito": automovel['debito'],
                    "arremate": automovel['arremate'],
                    "total": automovel['total']
                })




    amostra1 = diario_oficial.all()[211]
    amostra2 = leilao.all()[0]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Proprietario', 'Placa', 'Modelo', 'Ano', 'Chassi', 'Data Apreensao', 'Data Liberacao', 'Data NF', 'Diarias', 'Reboque', 'Debito Patio', 'Multas', 'Taxa Licenciamento', 'IPVA', 'Debito', 'Arremate', 'Total'])


    for r in cruzamento:
        ws.append([r['proprietario'], r['placa'], r['modelo'], r['ano'], r['chassi'], r['data_aprensao'], r['data_liberacao'], r['data_nf'], r['diarias'], r['reboque'], r['debito_patio'], r['multas'], r['tx_licenciamento'], r['ipva'], r['debito'], r['arremate'], r['total']])
    file = filedialog.asksaveasfilename(defaultextension='.xlsx')
    wb.save(file)
    print('Dados cruzados com sucesso')

