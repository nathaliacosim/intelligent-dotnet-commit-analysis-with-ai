import os
import subprocess
import requests
import sys
import time
from dotenv import load_dotenv

# =======================
# Carregar .env
# =======================
load_dotenv()

# =======================
# Configurações
# =======================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY não está definido. Configure no .env ou no GitHub Actions."
    )

GH_TOKEN = os.getenv("GH_TOKEN")
if not GH_TOKEN:
    raise EnvironmentError(
        "GH_TOKEN não está definido. Configure no .env ou no GitHub Actions."
    )

API_URL = "https://api.openai.com/v1/chat/completions"

# =======================
# Logging
# =======================
def log_info(msg):
    print(f"[INFO] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)

# =======================
# Funções
# =======================
def get_commit_diff():
    """Captura o diff do último commit ou retorna fallback se não houver histórico."""
    try:
        # Verifica se existe histórico
        subprocess.run(["git", "rev-parse", "HEAD~1"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_ai(diff, max_attempts=5):
    """Chama OpenAI com backoff exponencial e fallback mock."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"""
Analise o seguinte diff de código .NET:

{diff}

Identifique possíveis falhas de segurança, lógica e boas práticas no código alterado. Classifique cada falha como Crítica, Alta, Média ou Baixa.

Retorne o resultado em Markdown.
"""
            }
        ],
        "max_tokens": 1000
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 429:
                wait_time = 2 ** attempt
                log_info(f"API rate limit reached (429). Retry em {wait_time} segundos...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                return content
            else:
                log_error("Nenhum relatório gerado pela IA, usando fallback mock.")
                break
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            log_error(f"Tentativa {attempt} falhou: {e}. Retry em {wait_time} segundos...")
            time.sleep(wait_time)
    log_info("Usando relatório mock por falha persistente da API.")
    return """## Commit Analysis Report

### ⚠️ Issues
- **Critical:** Mock issue - Thread.Sleep used
- **High:** Mock issue - Missing input validation
- **Medium:** Mock issue - Outdated comments
- **Low:** Mock issue - Non-descriptive variable name
"""

def save_report(report):
    """Salva relatório em Markdown."""
    try:
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        log_info("Relatório salvo em 'report.md'.")
    except IOError as e:
        log_error(f"Falha ao salvar relatório: {e}")

# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    diff = get_commit_diff()

    if diff.strip() in ["Initial commit or unable to get diff", "No changes detected in the last commit."]:
        log_info("Usando relatório mock para primeiro commit ou commit sem alterações.")
        report = analyze_with_ai(diff)  # mesmo para mock, será fallback
    else:
        log_info("Enviando diff para OpenAI para análise real...")
        report = analyze_with_ai(diff)

    save_report(report)

    # Executa script para criar a issue
    try:
        subprocess.run(["python", "scripts/create_issue.py"], check=True)
        log_info("Script 'create_issue.py' executado com sucesso.")
    except subprocess.CalledProcessError as e:
        log_error(f"Falha ao executar 'create_issue.py': {e}")
