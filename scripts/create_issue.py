import os
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
GH_TOKEN = os.getenv("GH_TOKEN")
if not GH_TOKEN:
    raise EnvironmentError("GH_TOKEN não definido. Configure no .env ou GitHub Actions.")

REPO = os.getenv("GITHUB_REPOSITORY")
if not REPO:
    raise EnvironmentError("GITHUB_REPOSITORY não definido.")

API_URL = f"https://api.github.com/repos/{REPO}/issues"

LABEL_MAPPING = {
    "Critical": "critical",
    "High": "high",
    "Medium": "medium",
    "Low": "low"
}

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
def extract_labels(report):
    """Extrai labels de acordo com severidades encontradas no relatório."""
    labels = [label for severity, label in LABEL_MAPPING.items() if severity in report]
    return labels if labels else ["ai-analysis"]

def create_issue(title, body, labels=None):
    """Cria uma issue no GitHub com retry simples."""
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            log_info(f"Issue criada com sucesso com labels: {labels} ..")
            return
        except requests.exceptions.RequestException as e:
            log_error(f"Tentativa {attempt} falhou: {e}")
            if attempt < MAX_RETRIES:
                log_info(f"Retry em {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                log_error("Falha ao criar issue após várias tentativas.")
                sys.exit(1)

# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    try:
        with open("report.md", "r", encoding="utf-8") as f:
            report = f.read()
    except FileNotFoundError:
        log_error("report.md não encontrado. Execute analyze_diff.py primeiro.")
        sys.exit(1)

    labels = extract_labels(report)
    create_issue(
        title="🤖 AI Commit Analysis Report",
        body=report,
        labels=labels
    )
