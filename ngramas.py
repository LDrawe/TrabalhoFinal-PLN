import pprint
import re
from collections import defaultdict

def leitura(nome):
    arq = open(nome,'r')
    texto = arq.read()
    arq.close()
    return texto

def limpar(lista):
	lixo='.,:;?!"\'()[]{}/|#$%^&*-'
	quase_limpo = [x.strip(lixo).lower() for x in lista]
	return [x for x in quase_limpo if x.isalpha() or '-' in x]

corpus_base = leitura('corpus_bruto.txt')
corpus_pont = re.sub(r'!|\?|\.', '#', corpus_base)
corpus = corpus_pont.split('#')

if '\n' in corpus:
    corpus.remove('\n')

sentencas = [ ['<s>'] + limpar(s.split()) + ['</s>'] for s in corpus]

arq = open('corpus_preparado.txt','w')
for s in sentencas:
    arq.write(' '.join(s) +'\n')
arq.close()

arq = open('corpus_preparado.txt','r')
sentencas = arq.readlines()
arq.close()

corte = int(len(sentencas) * 0.8)
treino = sentencas[:corte]
teste = sentencas[corte:]

arq = open('corpus_treino.txt','w')
for s in treino:
    arq.write(s)
arq.close()

arq = open('corpus_teste.txt','w')
for s in teste:
    arq.write(s)
arq.close()

vocab = set()
contagens = defaultdict(int)

for linha in sentencas:
    sent = linha.split()
    for palavra in sent:
        vocab |= {palavra}
        contagens[palavra] += 1

hapax = [ p for p in contagens.keys() if contagens[p] == 1]
vocab -= set(hapax)
vocab |= {'<DES>'}

print('Vocabulario:', vocab)
print('Hapax:', hapax)

def ngramas(n, sent):
    return[tuple(sent[i:i+n]) for i in range(len(sent) - n + 1)]

unigramas = defaultdict(int)
bigramas = defaultdict(int)
trigramas = defaultdict(int)

for linha in sentencas:

    sent = linha.split()

    for i in range(len(sent)):
        if sent[i] in hapax:
            sent[i] = '<DES>'

    uni = ngramas(1,sent)
    bi = ngramas(2,sent)
    tri = ngramas(3, sent)

    for x in uni:
        unigramas[x] += 1

    for x in bi:
        bigramas[x] += 1

    for x in tri:
        trigramas[x] += 1

# pprint.pp(unigramas)
# pprint.pp(bigramas)
# pprint.pp(trigramas)

def prob_uni(x):
    V = len(vocab)
    N = sum(unigramas.values())
    return((unigramas[x] + 1) / (N + V))

def prob_bi(x):
    V = len(vocab)
    return ((bigramas[x] + 1) / (unigramas[(x[0],)] + V))

def prob_tri(x):
    V = len(vocab)
    return (trigramas[x] + 1) / (bigramas[(x[0], x[1])] + V)

def prever(frase):
    palavras = frase.split()
    
    # Tentar primeiro prever trigramas
    if len(palavras) >= 2:
        trigramas_candidatos = [(trigramas[(palavras[-2], palavras[-1], w)], w) for w in vocab if (palavras[-2], palavras[-1], w) in trigramas]
        if trigramas_candidatos:
            trigramas_candidatos.sort(reverse=True)
            return [w for _, w in trigramas_candidatos[:3]]

    # Se nao caiu no return acima, tentar prever bigramas
    if len(palavras) >= 1:
        bigramas_candidatos = [(bigramas[(palavras[-1], w)], w) for w in vocab if (palavras[-1], w) in bigramas]
        if bigramas_candidatos:
            bigramas_candidatos.sort(reverse=True)
            return [w for _, w in bigramas_candidatos[:3]]

    return ["Nenhuma previsão disponível."]

inputUsuario = ""
while inputUsuario != '!sair':
    inputUsuario = input("Digite uma palavra para a previsão: ").strip().lower()

    if inputUsuario != '!sair':
        previsao = prever(inputUsuario)
        if isinstance(previsao, list):
            print(" | ".join(previsao))
        else:
            print(previsao)