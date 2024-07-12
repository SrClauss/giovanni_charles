import tinydb
from openpyxl import Workbook
from tkinter import filedialog


db = tinydb.TinyDB('db.json')
table_leilao = db.table('leilao')
table_diario_oficial = db.table('diario_oficial')



def cruza_dados():
   
    print('Cruzando dados...')
    diario_oficial = table_diario_oficial.all()
    results = []

    """
            "placa": "OMG4476",
            "chassi": "LXYXCBL02C0298258",
            "modelo": "2012",
            "ano": "Conservado",
            "data_aprensao": "28/06/2021",
            "data_liberacao": "28/08/2023",
            "data_nf": "26/08/2023",
            "diarias": "4.259,52",
            "multas": "0,00",
            "reboque": "138,04",
            "debito": "5.667,54",
            "debito_patio": "700,00",
            "tx_licenciamento": "824,43",
            "ipva": "445,55",
            "arremate": "700,00",
            "total": "-4.967,54"
    """
 
    for veiculo in diario_oficial:
        chassi = veiculo['chassi']
        result = table_leilao.search(tinydb.Query().chassi == chassi)
        if result != []:
            results.append({
                'proprietario': veiculo['proprietario'],
                'placa': veiculo['placa'],
                'modelo': veiculo['modelo'],
                'ano': veiculo['ano'],
                'chassi': veiculo['chassi'],
                'data_aprensao': result[0]['data_aprensao'],
                'data_liberacao': result[0]['data_liberacao'],
                'data_nf': result[0]['data_nf'],
                'diarias': result[0]['diarias'],
                'reboque': result[0]['reboque'],
                'debito_patio': result[0]['debito_patio'],
                'multas': result[0]['multas'],
                'tx_licenciamento': result[0]['tx_licenciamento'],
                'ipva': result[0]['ipva'],
                'debito': result[0]['debito'],
                'arremate': result[0]['arremate'],
                'total': result[0]['total']



                
            })
    wb = Workbook()
    ws = wb.active
    ws.append(['Proprietario', 'Placa', 'Modelo', 'Ano', 'Chassi', 'Data Apreensao', 'Data Liberacao', 'Data NF', 'Diarias', 'Reboque', 'Debito Patio', 'Multas', 'Taxa Licenciamento', 'IPVA', 'Debito', 'Arremate', 'Total'])
    #como dimensionar o tamanho das colunas?
    
    for r in results:
        ws.append([r['proprietario'], r['placa'], r['modelo'], r['ano'], r['chassi'], r['data_aprensao'], r['data_liberacao'], r['data_nf'], r['diarias'], r['reboque'], r['debito_patio'], r['multas'], r['tx_licenciamento'], r['ipva'], r['debito'], r['arremate'], r['total']])
    file = filedialog.asksaveasfilename(defaultextension='.xlsx')
    wb.save(file)
    print('Dados cruzados com sucesso')
