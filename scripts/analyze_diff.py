import os
import subprocess
import json
import sys
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# =======================
# Carregar credenciais
# =======================
service_account_json = os.getenv("GOOGLE_TOKEN")
if not service_account_json:
    raise EnvironmentError("GOOGLE_TOKEN não definido.")

try:
    creds_dict = json.loads(service_account_json)
except json.JSONDecodeError as e:
    raise ValueError("GOOGLE_TOKEN inválido ou mal formatado") from e

credentials = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# =======================
# Gerar access token
# =======================
request = google.auth.transport.requests.Request()
credentials.refresh(request)
access_token = credentials.token

# =======================
# Funções
# =======================
def get_commit_diff():
    """Captura diff do último commit"""
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_gemini(diff):
    """Chama Gemini via REST API para analisar o diff e retornar Markdown"""
    url = "https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/gemini-1.5:predict"
    url = url.replace("{project}", creds_dict["project_id"])

    payload = {
        "instances": [{"content": diff}],
        "parameters": {"temperature": 0.2}
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        # Extrai a resposta do modelo
        result = response.json()
        # Ajuste conforme o formato do Gemini REST
        return result.get("predictions", [{}])[0].get("content", "Erro: resposta vazia do Gemini")
    except requests.RequestException as e:
        print(f"[ERROR] Falha ao chamar Gemini REST API: {e}", file=sys.stderr)
        return "Erro ao gerar relatório via Gemini. Usando mock."

def save_report(report):
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
    subprocess.run(["python", "scripts/create_issue.py"], check=True)
