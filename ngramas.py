import pprint
import re
from collections import defaultdict

def leitura(nome):
    with open(nome, 'r', encoding='utf-8') as arq:
        return arq.read()

def limpar(lista):
    lixo = r'[.,:;?!"\'(){}\[\]\/|#$%^&*-]'
    return [re.sub(lixo, '', x).lower() for x in lista if re.sub(lixo, '', x).isalpha()]

corpus_base = leitura('corpus_bruto.txt')
corpus_pont = re.sub(r'[!?\.]', '#', corpus_base)
corpus = [s.strip() for s in corpus_pont.split('#') if s.strip()]

sentencas = [['<s>'] + limpar(s.split()) + ['</s>'] for s in corpus]

with open('corpus_preparado.txt', 'w', encoding='utf-8') as arq:
    for s in sentencas:
        arq.write(' '.join(s) + '\n')

with open('corpus_preparado.txt', 'r', encoding='utf-8') as arq:
    sentencas = arq.readlines()

corte = int(len(sentencas) * 0.8)
treino, teste = sentencas[:corte], sentencas[corte:]

#Construção do modelo
with open('corpus_treino.txt', 'w') as arq:
    arq.writelines(treino)

with open('corpus_teste.txt', 'w') as arq:
    arq.writelines(teste)

with open('corpus_treino.txt', 'r') as arq:
    sentencas = arq.readlines()

vocab = set()

for linha in sentencas:
    contagens = defaultdict(int)
    sent = linha.split()
    for palavra in sent:
        vocab |= {palavra}
        contagens[palavra] += 1

hapax = {p for p in contagens if contagens[p] == 1}
vocab -= set(hapax)
vocab |= {'<DES>'}

def ngramas(n, sent):
    return [tuple(sent[i:i+n]) for i in range(len(sent) - n + 1)]

unigramas = defaultdict(int)
bigramas = defaultdict(int)

for linha in sentencas:

    sent = linha.split()

    for i in range(len(sent)):
        if sent[i] in hapax:  # Apenas substituir se não estiver no vocab
            sent[i] = '<DES>'

    uni = ngramas(1,sent)
    bi = ngramas(2,sent)

    for x in uni:
        unigramas[x] += 1

    for x in bi:
        bigramas[x] += 1

pprint.pp(unigramas)
pprint.pp(bigramas)

def prob_uni(x):
    V = len(vocab)
    N = sum(unigramas.values())
    return((unigramas[x] + 1) / (N + V))

def prob_bi(x):
    V = len(vocab)
    return ((bigramas[x] + 1) / (unigramas[(x[0],)] + V))

def prever(palavra):
    candidatos = [ch for ch in bigramas.keys() if ch[0] == palavra]
    
    if not candidatos:
        return '<s>'  # Retorna um marcador neutro caso não haja bigramas conhecidos

    ordem = sorted(candidatos, key=prob_bi, reverse=True)
    return ordem[0][1]

print(prever('menina'))
print(prever('gosta'))
print(prever('gato'))

