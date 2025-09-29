import os
import subprocess
import json
import sys
import requests

# =======================
# Configurações
# =======================
API_KEY = os.getenv("AI_STUDIO_API_KEY")
if not API_KEY:
    raise EnvironmentError("AI_STUDIO_API_KEY não definido.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "gemini-1.5"  # modelo Gemini disponível

# =======================
# Funções
# =======================
def get_commit_diff():
    """Captura o diff do último commit."""
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_gemini(diff):
    """Chama Gemini REST API para analisar o diff."""
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/{MODEL}:generateMessage"
    prompt = f"""
Analise o seguinte diff de código .NET:

{diff}

Classifique problemas como Crítica, Alta, Média ou Baixa.
Retorne o resultado em Markdown.
"""
    payload = {
        "prompt": {
            "messages": [{"content": prompt, "role": "user"}]
        },
        "temperature": 0.2,
        "candidate_count": 1,
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]
    except Exception as e:
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

    # Chama criação de issue
    subprocess.run(["python", "scripts/create_issue.py"], check=True)
