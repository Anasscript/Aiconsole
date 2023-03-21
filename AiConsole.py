import openai
import os
import subprocess
import platform
import re
from prompt_toolkit import prompt, PromptSession
from functools import lru_cache
import getpass

def ottieni_info_sistema():
    nome_sistema = platform.system()
    versione_sistema = platform.release()
    architettura = platform.architecture()[0]
    return f"{nome_sistema} {versione_sistema} {architettura}"

def analizza_risposta_gpt(risposta):
    risposta_pulita = pulisci_risposta_gpt(risposta)
    comandi = re.split(r';\s*', risposta_pulita)
    comando_unificato = ' && '.join(comandi)
    return comando_unificato


def ottieni_input_utente(messaggio_prompt):
    input_utente = prompt(messaggio_prompt, default='', insert_text=True)
    return input_utente

def esegui_comandi(comandi):
    risultati = []

    for comando in comandi:
        input_utente = ottieni_input_utente(f"Modifica il comando '{comando}': ")
        comando = input_utente
        output = esegui_comando(comando)
        risultati.append(output)

    return risultati

def esegui_terminale():
    info_sistema = ottieni_info_sistema()
    sessione = PromptSession()

    while True:
        prompt_utente = sessione.prompt(f"AiConsole: ")

        if prompt_utente.lower() == 'esci':
            break

        prompt_gpt = f"Converti la seguente richiesta dell'utente in un comando per linux RedHat : ({prompt_utente}) esempio output:arp -a"

        risposta_gpt = ottieni_risposta_gpt(prompt_gpt)

        comando = analizza_risposta_gpt(risposta_gpt)
        output = esegui_comando(comando)
        if output != 'None':
            print(f"Risultato:\n{output}\n")
        else:
            print(f"Il comando non ha generato output")


@lru_cache(maxsize=1280000)
def ottieni_risposta_gpt(prompt):
    openai.api_key = "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"

    risposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Comando: " + prompt}],
        max_tokens=100,
        n=1,
        temperature=0.82,
    )

    messaggio = risposta.choices[0].message["content"].strip()
    return messaggio

def ottieni_risposta_gpt_per_output(output):
    output_minuscolo = output.lower()
    if "y" in output_minuscolo or "Y" in output_minuscolo:
        return "y"
    if "password" in output_minuscolo:
        password = getpass.getpass(f"L'operazione richiede verifica\nInserisci la password dell'utente: ")
        return password
    else:
        prompt_gpt = f"Comando per gestire l'output '{output}' nel terminale? ''\n\n> "
        risposta_gpt = ottieni_risposta_gpt(prompt_gpt)

    if risposta_gpt.lower() == "nessuna azione":
        return None
    else:
        return risposta_gpt

def pulisci_risposta_gpt(risposta):
    risposta_pulita = risposta.replace("''", "").strip()
    return risposta_pulita

def pulisci_risposta_gpt(risposta):
    risposta_pulita = risposta.replace("''", "").strip()
    return risposta_pulita

def esegui_comando(comando):
    try:
        if platform.system() == "Windows":
            comando = "powershell.exe -Command " + comando
        else:
            comando = "/bin/bash -c " + comando

        processo = subprocess.Popen(
            comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True
        )

        print(f"\nEseguendo il comando: {comando}")

        while True:
            output = processo.stdout.readline()
            if output == '' and processo.poll() is not None:
                break
            if output:
                print(f"{output.strip()}")
                risposta = ottieni_risposta_gpt_per_output(output.strip())

                if risposta:
                    processo.stdin.write(risposta + "\n")
                    processo.stdin.flush()
                    print(f"Invio input al comando: {risposta}")

        stderr = processo.stderr.read()
        if stderr:
            print(f"Errore: {stderr}")
        return stderr if stderr else None

    except Exception as e:
        print(f"Errore imprevisto: {e}")
        return f"Errore imprevisto: {e}"

def main():
    info_sistema = ottieni_info_sistema()
    esegui_terminale()

if __name__ == "__main__":
    main()
