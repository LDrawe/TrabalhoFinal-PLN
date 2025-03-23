
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import defaultdict

nltk.download('punkt_tab')

def leitura(nome):
    with open(nome, 'r', encoding='utf-8') as arq:
        texto = arq.read()
    return texto

def limpar(lista):
    lixo = '.,:;?!"\'()[]{}/|#$%^&*-'
    quase_limpo = [x.strip(lixo).lower() for x in lista]
    return [x for x in quase_limpo if x.isalpha() or '-' in x]

corpus_base = leitura('corpus_bruto.txt')
sentencas_brutas = sent_tokenize(corpus_base, language='portuguese')

sentencas = [['<s>'] + limpar(word_tokenize(s)) + ['</s>'] for s in sentencas_brutas]

with open('corpus_preparado.txt', 'w', encoding='utf-8') as arq:
    for s in sentencas:
        arq.write(' '.join(s) + '\n')

with open('corpus_preparado.txt', 'r', encoding='utf-8') as arq:
    sentencas = arq.readlines()

corte = int(len(sentencas) * 0.8)
treino = sentencas[:corte]
teste = sentencas[corte:]

with open('corpus_treino.txt', 'w', encoding='utf-8') as arq:
    for s in treino:
        arq.write(s)
    
with open('corpus_teste.txt', 'w', encoding='utf-8') as arq:
    for s in teste:
        arq.write(s)

vocab = set()
contagens = defaultdict(int)

for linha in sentencas:
    sent = linha.split()
    for palavra in sent:
        vocab |= {palavra}
        contagens[palavra] += 1

hapax = [ p for p in contagens.keys() if contagens[p]== 1]
vocab -= set(hapax)
vocab |= {'<DES>'}

def ngramas(n, sent):
    return [tuple(sent[i:i+n]) for i in range(len(sent) - n + 1)]

unigramas = defaultdict(int)
bigramas = defaultdict(int)
trigramas = defaultdict(int)

for linha in sentencas:
    sent = linha.split()
    for i in range(len(sent)):
        if sent[i] in hapax:
            sent[i] = '<DES>'

    uni = ngramas(1, sent)
    bi = ngramas(2, sent)
    tri = ngramas(3, sent)

    for x in uni:
        unigramas[x] += 1
    for x in bi:
        bigramas[x] += 1
    for x in tri:
        trigramas[x] += 1

def prob_uni(x):
    V = len(vocab)
    N = sum(unigramas.values())
    return (unigramas[x] + 1) / (N + V)

def prob_bi(x):
    V = len(vocab)
    return (bigramas[x] + 1) / (unigramas[(x[0],)] + V)

def prob_tri(x):
    V = len(vocab)
    return (trigramas[x] + 1) / (bigramas[(x[0], x[1])] + V)

def prever(frase):
    palavras = limpar(word_tokenize(frase))

    if len(palavras) >= 2:
        trigramas_candidatos = [(trigramas[(palavras[-2], palavras[-1], w)], w) 
                                for w in vocab if (palavras[-2], palavras[-1], w) in trigramas]
        if trigramas_candidatos:
            trigramas_candidatos.sort(reverse=True)
            return [w for _, w in trigramas_candidatos[:3]]

    if len(palavras) >= 1:
        bigramas_candidatos = [(bigramas[(palavras[-1], w)], w) 
                               for w in vocab if (palavras[-1], w) in bigramas]
        if bigramas_candidatos:
            bigramas_candidatos.sort(reverse=True)
            return [w for _, w in bigramas_candidatos[:3]]

    return ["Nenhuma previsão disponível."]

inputUsuario = ""
while inputUsuario != '#':
    inputUsuario = input("Digite uma palavra para a previsão: (Para finalizar, digite #)").strip().lower()

    if inputUsuario != '#':
        previsao = prever(inputUsuario)
        print(" | ".join(previsao))