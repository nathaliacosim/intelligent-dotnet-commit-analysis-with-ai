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
API_URL = "https://api.openai.com/v1/chat/completions"

MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos

# =======================
# Logging centralizado
# =======================
def log_info(msg):
    print(f"[INFO] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)

# =======================
# Funções
# =======================
def get_commit_diff():
    """Captura o diff do último commit de forma segura."""
    try:
        # Checa se HEAD~1 existe
        subprocess.check_output(["git", "rev-parse", "HEAD~1"], stderr=subprocess.DEVNULL)
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_ai(diff):
    """Envia o diff para a OpenAI com retry simples."""
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

                    Identifique possíveis falhas de segurança, lógica e boas práticas. Classifique como:
                    - Crítica
                    - Alta
                    - Média
                    - Baixa

                    Retorne em Markdown seguindo a estrutura:

                    ## 🔍 Relatório de Análise de Commit
                    **Resumo:** Breve descrição do diff.

                    ### ⚠️ Falhas Detectadas
                    - **Crítica:** ...
                    - **Alta:** ...
                    - **Média:** ...
                    - **Baixa:** ...

                    **Sugestões de Melhoria:** (opcional)

                    _Análise gerada automaticamente via IA._
                """
            }
        ],
        "max_tokens": 1000
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return content if content else "Nenhum relatório gerado pela IA."
        except requests.exceptions.RequestException as e:
            log_error(f"Tentativa {attempt} falhou: {e}")
            if attempt < MAX_RETRIES:
                log_info(f"Retry em {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                return "Erro ao conectar com a API da OpenAI após várias tentativas."

def save_report(report):
    """Salva o relatório em arquivo Markdown."""
    try:
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        log_info("Relatório salvo em 'report.md'.")
    except IOError as e:
        log_error(f"Falha ao salvar o relatório: {e}")

# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    diff = get_commit_diff()

    if diff.strip() in ["Initial commit or unable to get diff", "No changes detected in the last commit."]:
        log_info("Usando relatório mock para primeiro commit ou commit sem alterações.")
        report = """## Commit Analysis Report

        ### ⚠️ Issues
        - **Critical:** Mock issue - Thread.Sleep used
        - **High:** Mock issue - Missing input validation
        - **Medium:** Mock issue - Outdated comments
        - **Low:** Mock issue - Non-descriptive variable name
        """
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
