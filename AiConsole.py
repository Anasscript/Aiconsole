import openai
import os
import subprocess
import platform
import re
from prompt_toolkit import prompt, PromptSession
from functools import lru_cache
import getpass

print("Aiconsole versione 0.1 \n Comunica in maniera naturale col terminale\n\n\n")
api_key = input("Inserisci la tua API key: ")

def identifica_sistema_operativo():
    if os.name == 'nt':
        return "Powershell"
    else:
        release = os.uname()[2]
        distribuzione = os.uname()[3]
        return f"{distribuzione} {release}"

def estrai_comandi(testo):
    comandi = re.split(r';\s*', testo)
    comandi_puliti = [comando.strip() for comando in comandi if comando.strip()]
    return comandi_puliti

def analizza_risposta_gpt(risposta, sistema_operativo):
    risposta_pulita = risposta.replace("''", "").strip()
    comandi = estrai_comandi(risposta_pulita)

    if sistema_operativo == "Windows":
        comando_unificato = ' & '.join(comandi)
    else:
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
    sistema_operativo = identifica_sistema_operativo()

    sessione = PromptSession()

    while True:
        prompt_utente = sessione.prompt(f"AiConsole: ")

        if prompt_utente.lower() == 'esci':
            break

        prompt_gpt = f"Converti la seguente richiesta dell'utente in un comando per {sistema_operativo} : ({prompt_utente}) esempio risposta:ls"

        risposta_gpt = ottieni_risposta_gpt(prompt_gpt)
        print(f"Risposta GPT-3:\n{risposta_gpt} per {sistema_operativo}\n")
        comando = analizza_risposta_gpt(risposta_gpt, sistema_operativo)

        if comando:
            output = esegui_comando(comando)
            if output != 'None':
                print(f"Risultato:\n{output}\n")
            else:
                print(f"Il comando non ha generato output")
        else:
            print("Nessun comando estratto dalla risposta GPT-3.")

@lru_cache(maxsize=1280000)
def ottieni_risposta_gpt(prompt):
    current_dir = os.getcwd()
    current_user = getpass.getuser()
    current_os = platform.system()
    openai.api_key = "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"
    openai.api_key = ottieni_input_utente.prompt
    risposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[    {"role": "system", "content": "Directory: " + current_dir},    {"role": "system", "content": "User: " + current_user},    {"role": "system", "content": "OS: " + current_os},    {"role": "user", "content": prompt},],
        max_tokens=100,
        n=1,
        temperature=0.82,
        top_p=0.56,
    )
    messaggio = risposta.choices[0].message["content"].strip()
    return messaggio

def esegui_comando(comando):
    try:
        if platform.system() == "Windows":
            comando = 'start powershell -NoExit -Command "' + comando + '"'
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

                if "Do you want to continue?" in output.strip() or "Vuoi continuare?" in output.strip():
                    processo.stdin.write("Y\n")
                    processo.stdin.flush()
                    print("Premendo Y per continuare l'installazione...")

        stderr = processo.stderr.read()
        if stderr:
            print(f"Errore: {stderr}")
        return stderr if stderr else None

    except Exception as e:
        print(f"Errore imprevisto: {e}")
        return f"Errore imprevisto: {e}"

def main():
    info_sistema = identifica_sistema_operativo()
    esegui_terminale()

if __name__ == "__main__":
    main()
