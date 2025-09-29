import os
import subprocess
import json
import sys
import time
import requests

# =======================
# Configurações
# =======================
GOOGLE_TOKEN = os.getenv("GOOGLE_TOKEN")  # token de acesso Vertex AI
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")  # default

if not GOOGLE_TOKEN or not PROJECT_ID:
    raise EnvironmentError(
        "GOOGLE_TOKEN ou GOOGLE_PROJECT_ID não definidos. Configure os secrets no GitHub."
    )

ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/text-bison-001:predict"

MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos

# =======================
# Funções
# =======================
def get_commit_diff():
    """Captura o diff do último commit ou fallback mock"""
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_gemini(diff):
    """Chama Gemini via REST API e retorna o relatório em Markdown"""
    prompt = f"""
    Analise o seguinte diff de código .NET:

    {diff}

    Classifique problemas como Crítica, Alta, Média ou Baixa.
    Retorne o resultado em Markdown incluindo:

    - Resumo das alterações
    - Problemas detectados com severidade
    - Sugestões de melhoria (opcional)

    Análise gerada automaticamente.
    """

    headers = {
        "Authorization": f"Bearer {GOOGLE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "instances": [{"content": prompt}],
        "parameters": {"temperature": 0.2, "maxOutputTokens": 1000}
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(ENDPOINT, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            text = response.json()["predictions"][0]["content"]
            return text
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Tentativa {attempt} falhou: {e}", file=sys.stderr)
            if attempt < MAX_RETRIES:
                print(f"[INFO] Retry em {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                return "Erro ao gerar relatório via Gemini. Usando mock."

def save_report(report):
    """Salva o relatório em Markdown"""
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("[INFO] Relatório salvo em 'report.md'.")

# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    diff = get_commit_diff()

    if diff in ["Initial commit or unable to get diff", "No changes detected in the last commit."]:
        report = """## Commit Analysis Report

        ### ⚠️ Issues
        - **Critical:** Mock issue - Thread.Sleep used
        - **High:** Mock issue - Missing input validation
        - **Medium:** Mock issue - Outdated comments
        - **Low:** Mock issue - Non-descriptive variable name
        """
    else:
        print("[INFO] Enviando diff para Gemini via REST API...")
        report = analyze_with_gemini(diff)

    save_report(report)

    # Chama script que cria issue
    try:
        subprocess.run(["python", "scripts/create_issue.py"], check=True)
        print("[INFO] Script 'create_issue.py' executado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Falha ao executar 'create_issue.py': {e}", file=sys.stderr)
