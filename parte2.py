from transformers import pipeline
import nltk

nltk.download('punkt_tab')
generator = pipeline("text-generation", model="TucanoBR/Tucano-160m")

def prever_tucano(frase):
    completions = []
    for _ in range(3):
        completion = generator(frase, num_return_sequences=1, max_new_tokens=3, do_sample=True, top_k=50, top_p=0.95, temperature=0.7)
        words = completion[0]['generated_text'].split()
        new_word = words[len(frase.split())]
        completions.append(new_word)
    return completions

inputUsuario = ""
while inputUsuario != '#':
    inputUsuario = input("Digite uma palavra para a previsão: ").strip().lower()

    if inputUsuario != '#':
        previsao_tucano = prever_tucano(inputUsuario)
        resultado = ' '.join(previsao_tucano).replace(inputUsuario, '').strip()
        print(" | ".join(resultado.split()))
