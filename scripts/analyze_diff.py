import os
import subprocess
import json
import requests

# =======================
# Carregar API Key
# =======================
API_KEY = os.getenv("AI_STUDIO_API_KEY")
if not API_KEY:
    raise EnvironmentError("AI_STUDIO_API_KEY não definido.")

# =======================
# Funções
# =======================
def get_commit_diff():
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_gemini(diff):
    """Chama Gemini via REST API e retorna Markdown"""
    url = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5:generateMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    prompt = f"""
Analise o seguinte diff de código .NET:

{diff}

Classifique problemas como Crítica, Alta, Média ou Baixa.
Retorne o resultado em Markdown.
"""
    payload = {
        "prompt": {
            "text": prompt
        },
        "temperature": 0.2
    }
    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        # O texto gerado normalmente fica em result['candidates'][0]['content']
        return result['candidates'][0]['content']
    except Exception as e:
        print(f"[ERROR] Falha ao chamar Gemini REST API: {e}")
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
