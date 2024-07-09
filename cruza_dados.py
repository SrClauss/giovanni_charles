import tinydb
from openpyxl import Workbook



db = tinydb.TinyDB('db.json')
table_leilao = db.table('leilao')
table_diario_oficial = db.table('diario_oficial')



def cruza_dados(buttons):
    for button in buttons:
        button.config(state='disabled')
    print('Cruzando dados...')
    diario_oficial = table_diario_oficial.all()
    results = []
    for veiculo in diario_oficial:
        chassi = veiculo['chassi']
        result = table_leilao.search(tinydb.Query().chassi == chassi)
        if result != []:
            results.append({
                'proprietario': veiculo['proprietario'],
                'data_aprensao': result[0]['data_aprensao'],
                'data_liberacao': result[0]['data_liberacao'],
                'placa': result[0]['placa'],
                'chassi': result[0]['chassi'],
                'veiculo': result[0]['modelo'],
                'diarias': result[0]['diarias'],
                'remocao': result[0]['reboque'],
                'remanescente': result[0]['total'],

            })
    wb = Workbook()

    ws = wb.active
    ws.append(['Proprietário', 'Data de apreensão', 'Data de liberação', 'Placa', 'Chassi', 'Veículo', 'Diárias', 'Remoção', 'Remanescente'])
    for result in results:
        ws.append([result['proprietario'], result['data_aprensao'], result['data_liberacao'], result['placa'], result['chassi'], result['veiculo'], result['diarias'], result['remocao'], result['remanescente']])
    wb.save('resultados.xlsx')
    

    print('Dados cruzados com sucesso e salvos em resultados.xlsx')
    for button in buttons:
        button.config(state='normal')



