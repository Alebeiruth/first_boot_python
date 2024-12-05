import json
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
from difflib import SequenceMatcher  # Para medir similaridade entre strings
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters


# Download NLTK data (including 'punkt_tab')
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Carregar a base de conhecimento
def carregar_base_conhecimento():
    try:
        with open("perguntas_respostas.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Erro: O arquivo perguntas_respostas.json não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print("Erro: O arquivo perguntas_respostas.json está corrompido ou não é um JSON válido.")
        return None

# Exemplo de uso da função carregar_base_conhecimento
base_conhecimento = carregar_base_conhecimento()
if base_conhecimento:
    print("Base de conhecimento carregada com sucesso.")
else:
    print("Falha ao carregar a base de conhecimento.")

# Processamento de linguagem natural para encontrar respostas relevantes
def encontrar_resposta(pergunta, base_conhecimento):
    if base_conhecimento is None:
        return "Base de conhecimento não carregada."

    # Pré-processa a pergunta do usuário
    palavras = word_tokenize(pergunta.lower())
    palavras_filtradas = [palavra for palavra in palavras if palavra not in stopwords.words('portuguese')]

    melhor_pontuacao = 0
    melhor_resposta = "Desculpe, não encontrei uma resposta para a sua pergunta."

    # Compara cada pergunta da base com a pergunta do usuário
    for item in base_conhecimento:
        palavras_base = word_tokenize(item["pergunta"].lower())
        palavras_base_filtradas = [palavra for palavra in palavras_base if palavra not in stopwords.words('portuguese')]

        # Mede similaridade entre as perguntas usando SequenceMatcher
        pontuacao = SequenceMatcher(None, " ".join(palavras_filtradas), " ".join(palavras_base_filtradas)).ratio()

        # Atualiza a melhor resposta com base na maior pontuação
        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_resposta = item["resposta"]

    return melhor_resposta


# Salvar histórico em um arquivo
def salvar_historico(nome_usuario, historico):
    with open(f"historico_{nome_usuario}.txt", "w", encoding="utf-8") as file:
        file.write(f"Histórico de conversa com {nome_usuario}:\n")
        file.write("\n".join(historico))

# Interface gráfica com Tkinter
def iniciar_interface_grafica(base_conhecimento):
    def enviar_pergunta():
        pergunta = entrada.get()
        if pergunta.lower() == "encerrar":
            historico.append(f"Você: {pergunta}\nChatbot: Chat encerrado.")
            salvar_historico(nome_usuario, historico)
            janela.destroy()
        elif not pergunta.strip():
            resposta = "Por favor, insira uma pergunta válida."
        else:
            resposta = encontrar_resposta(pergunta, base_conhecimento)
            historico.append(f"Você: {pergunta}\nChatbot: {resposta}")
        texto.insert(tk.END, f"Você: {pergunta}\nChatbot: {resposta}\n\n")
        entrada.delete(0, tk.END)

    # Solicita o nome do usuário ao abrir a interface
    nome_usuario = simpledialog.askstring("Chatbot", "Olá! Qual é o seu nome?")
    if not nome_usuario:
        print("O nome do usuário é necessário para continuar.")
        return

    historico = []

    # Configuração da janela
    janela = tk.Tk()
    janela.title(f"Chatbot - Usuário: {nome_usuario}")

    texto = scrolledtext.ScrolledText(janela, width=50, height=20, wrap=tk.WORD)
    texto.grid(column=0, row=0, padx=10, pady=10)

    entrada = tk.Entry(janela, width=40)
    entrada.grid(column=0, row=1, padx=10, pady=10)

    botao_enviar = tk.Button(janela, text="Enviar", command=enviar_pergunta)
    botao_enviar.grid(column=0, row=2, padx=10, pady=10)

    janela.mainloop()

# Função principal do Chatbot em modo texto
def chatbot_texto():
    base_conhecimento = carregar_base_conhecimento()

    nome_usuario = input("Olá! Qual é o seu nome? ")
    if not nome_usuario.strip():
        print("Nome inválido. Encerrando o chat.")
        return

    print(f"Bem-vindo, {nome_usuario}! Pergunte o que desejar ou digite 'Encerrar' para sair.")

    historico = []

    while True:
        pergunta = input("Você: ")

        if pergunta.strip().lower() == "encerrar":
            salvar_historico(nome_usuario, historico)
            print("Chat encerrado. O histórico foi salvo.")
            break

        if not pergunta.strip():
            print("Parece que você não escreveu nada. Por favor, tente novamente.")
            continue

        resposta = encontrar_resposta(pergunta, base_conhecimento)
        print(f"Chatbot: {resposta}")
        historico.append(f"Você: {pergunta}\nChatbot: {resposta}")


# Escolher modo de execução
if __name__ == "__main__":
    print("Escolha o modo do chatbot:")
    print("1 - Interface Gráfica")
    print("2 - Interface Texto Simples")
    escolha = input("Digite sua escolha (1 ou 2): ").strip()

    base_conhecimento = carregar_base_conhecimento()

    if escolha == "1":
        iniciar_interface_grafica(base_conhecimento)
    elif escolha == "2":
        chatbot_texto()
    else:
        print("Escolha inválida. Encerrando.")
