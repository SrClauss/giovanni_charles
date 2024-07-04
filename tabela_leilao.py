import re
import tinydb
from tqdm import tqdm
db = tinydb.TinyDB('db.json')
table = db.table('leilao')

def extract_data_relacao_veiculos_arrematados_muriae(pdf_file):
    words = []
    for page in pdf_file.pages:
        words += page.extract_words()

    words_word = [word['text'] for word in words]
    words_word
    index_cnpj = words_word.index('CNPJ:') + 2
    words_word = words_word[index_cnpj:]

    indices_lotes = [i for i, x in enumerate(words_word) if x == 'Lote:']



    tables = []
    for i in range(len(indices_lotes) -1):
        tables.append(words_word[indices_lotes[i]:indices_lotes[i+1]])

    padrao_ano = re.compile(r'\b\d{4}\b')
    padrao_date = re.compile(r'\b\d{2}/\d{2}/\d{4}\b')
    padrao_moeda = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")

    results = []
    for table in tables:
        result = {}
        for word in range(len(table)):
            if padrao_ano.match(table[word]):
                ano = table[word]
                index_ano = word
                break
        result['placa'] = table[3]
        result['chassi'] = table[4]
        result['modelo'] = " ".join(table[6:index_ano])
        result['ano'] = ano
        dates = []
        valores = []
        for word in range(len(table)):
            if padrao_date.match(table[word]):
                dates.append(table[word])
            if padrao_moeda.match(table[word]):
                valores.append(table[word])
        
            
        

        if len(dates) == 3:
            result['data_aprensao'] = dates[0]
            result['data_nf'] = dates[1]
            result['data_liberacao'] = dates[2]

        if len(dates) == 2:
            result['data_aprensao'] = dates[0]
            result['data_nf'] = None
            result['data_liberacao'] = dates[1]

        if len(dates) == 1:
            result['data_aprensao'] = dates[0]
            result['data_nf'] = None
            result['data_liberacao'] = None
        

        result['diarias'] = valores[0]
        result['reboque'] = valores[1]
        result['multas'] = valores[2]
        result['tx_licenciamento'] = valores[3]
        result['ipva'] = valores[4]
        result['debitos'] = valores[5]
        result['arremate'] = valores[6]
        result['debito_patio'] = valores[7]
        result['saldo'] = f"-{valores[8]}"
        results.append(result)

    return results


def extract_data_relacao_veiculos_arrematados_cajurense(pdf_file):
    #cria uma lista com todas as palavras do pdf        
    words = []
    print("extraindo palavras")
    print(f"numero de paginas: {len(pdf_file.pages)}")


    for page in tqdm(pdf_file.pages, desc="Processando páginas"):
        words += page.extract_words()
        
    print(f"palavras extraidas: {len(words)}")

    #extrai apenas o texto das palavras
    words_word = [word['text'] for word in words]

    #encontra o indice do inicio dos dados
    index_cnpj = words_word.index('CNPJ:')
    inicio = index_cnpj + 2
    
    print(f"indice do cnpj: {index_cnpj}")
    #procura por padroes de numeros de 5 digitos
    pattern = r"(\b\d{5}\b)"
    

    #cria uma lista com as palavras que correspondem ao padrao
    padroes = []


    for word in words_word[inicio:]:
        if re.match(pattern, word):
            padroes.append(word)
    #usando os padroes separe palavras em tabelas

    print(f"padroes encontrados: {len(padroes)}")
    tables = []
    for i in range(0, len(padroes)-1, 1):
        tables.append(words_word[words_word.index(padroes[i]):words_word.index(padroes[i+1])])

    print(f"tabelas encontradas: {len(tables)}")
    #adiciona a ultima tabela
    tables.append(words_word[words_word.index(padroes[-1]):])
    #armazena os padroes de moeda e data
    padrao_moeda = r"-?\d{1,3}(?:\.\d{3})*,\d{2}"
    padrao_data = r"\d{2}/\d{2}/\d{4}"
    print("Deslocando valores incorretos...")
    #corrige a tabela que foi dividida em duas e desloca alguns valores que fogem do padrao
    for i in range(len(tables)-1):
        if not re.search(padrao_moeda, tables[i][-1]):
            tables[i+1][5] = tables[i][-1]+' '+tables[i+1][5] 


    print("Extraindo dados...")
    results = []
    for table in tables:
        result = {}

        result['placa'] = table[2]
        result['chassi'] = table[3]
        result['modelo'] = table[5]
        result['ano'] = table[6]

        dates = []
        valores = []
        for word in table:
            if re.match(padrao_data, word):
                dates.append(word)
            if re.match(padrao_moeda, word):
                valores.append(word)
        
        if len(dates) == 2:
            result['data_aprensao'] = dates[0]
            result['data_liberacao'] = None
            result['data_nf'] = dates[1]


        if len(dates) > 2:
            result['data_aprensao'] = dates[0]
            result['data_liberacao'] = dates[1]
            result['data_nf'] = dates[2]
        
        result['diarias'] = valores[0]
        result['reboque'] = valores[1]
        result['multas'] = valores[2]
        result['tx_licenciamento'] = valores[5]
        result['ipva'] = valores[6]
        result['debito'] = valores[7]
        result['arremate'] = valores[8]
        result['debito_patio'] = valores[9]
        result['total'] = valores[10]
        results.append(result)

    print("Dados extraidos com sucesso")
    return results

    
def extract_data(pdf_file):
    first_page = pdf_file.pages[0]
    words = first_page.extract_words()
    words_word = [word['text'] for word in words]
    if words_word[0] == "DEPARTAMENTO":
        table.insert_multiple(extract_data_relacao_veiculos_arrematados_cajurense(pdf_file))

    elif words_word[0] == "COORDENADORIA":
        table.insert_multiple(extract_data_relacao_veiculos_arrematados_muriae(pdf_file))


def remove_duplicates():
    all_data = table.all()
    #compara todas as entradas com mesmo chassi

    for i in range(len(all_data)):
        for j in range(i+1, len(all_data)):
            if all_data[i]['chassi'] == all_data[j]['chassi']:
                if all_data[i]['total'] > all_data[j]['total']:
                    table.remove(doc_ids=[j])
                else:
                    table.remove(doc_ids=[i])
        




