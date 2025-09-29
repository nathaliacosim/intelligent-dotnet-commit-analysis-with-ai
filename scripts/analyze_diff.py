import os
import sys
import json
import subprocess
import time
from google.cloud import aiplatform

# =======================
# Logging simples
# =======================
def log_info(msg):
    print(f"[INFO] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)

# =======================
# Carregar credenciais
# =======================
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
if not credentials_json:
    raise EnvironmentError("GOOGLE_CREDENTIALS não definido.")

credentials = json.loads(credentials_json)
project_id = credentials.get("project_id")
if not project_id:
    raise EnvironmentError("Project ID não encontrado nas credenciais.")

aiplatform.init(project=project_id, credentials=credentials)

# =======================
# Funções principais
# =======================
def get_commit_diff():
    """Captura o diff do último commit ou retorna fallback mock."""
    try:
        # Checa se existe commit anterior
        subprocess.run(["git", "rev-parse", "HEAD~1"], check=True, stdout=subprocess.DEVNULL)
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True)
        if not diff.strip():
            diff = "No changes detected in the last commit."
    except subprocess.CalledProcessError:
        diff = "Initial commit or unable to get diff"
    return diff

def analyze_with_gemini(diff, retries=3, delay=5):
    """Chama Gemini para analisar o diff e retorna Markdown."""
    prompt = f"""
            Analise o seguinte diff de código .NET:

            {diff}

            Classifique problemas como Crítica, Alta, Média ou Baixa.
            Retorne o resultado em Markdown.
    """
    model = "gemini-1.5"
    for attempt in range(1, retries+1):
        try:
            response = aiplatform.TextGenerationModel(model_name=model).predict(prompt)
            return response.text
        except Exception as e:
            log_error(f"Tentativa {attempt} falhou: {e}")
            if attempt < retries:
                log_info(f"Retry em {delay} segundos...")
                time.sleep(delay)
    return "Erro ao gerar relatório via Gemini. Usando mock."

def save_report(report, filename="report.md"):
    """Salva relatório em arquivo Markdown."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        log_info(f"Relatório salvo em '{filename}'.")
    except IOError as e:
        log_error(f"Falha ao salvar relatório: {e}")

# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    diff = get_commit_diff()

    if diff in ["Initial commit or unable to get diff", "No changes detected in the last commit."]:
        log_info("Usando relatório mock para primeiro commit ou commit sem alterações.")
        report = """## Commit Analysis Report

        ### ⚠️ Issues
        - **Critical:** Mock issue - Thread.Sleep used
        - **High:** Mock issue - Missing input validation
        - **Medium:** Mock issue - Outdated comments
        - **Low:** Mock issue - Non-descriptive variable name
        """
    else:
        log_info("Enviando diff para Gemini...")
        report = analyze_with_gemini(diff)

    save_report(report)

    try:
        subprocess.run(["python", "scripts/create_issue.py"], check=True)
        log_info("Script 'create_issue.py' executado com sucesso.")
    except subprocess.CalledProcessError as e:
        log_error(f"Falha ao executar 'create_issue.py': {e}")
