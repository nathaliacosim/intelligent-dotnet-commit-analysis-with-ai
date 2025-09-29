import os
import requests

# =======================
# Configurações
# =======================
GH_TOKEN = os.getenv("GH_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")  # exemplo: nathalia/intelligent-dotnet-commit-analysis
if not GH_TOKEN or not GITHUB_REPOSITORY:
    raise EnvironmentError("GH_TOKEN ou GITHUB_REPOSITORY não definidos.")

HEADERS = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPORT_FILE = "report.md"

# =======================
# Funções
# =======================
def read_report():
    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def extract_labels(report):
    """Extrai labels baseados em severidade do relatório."""
    labels = ["ai-analysis"]
    for severity in ["Critical", "High", "Medium", "Low"]:
        if f"**{severity}**" in report:
            labels.append(severity.lower())
    return labels

def create_issue(title, body, labels):
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues"
    payload = {
        "title": title,
        "body": body,
        "labels": labels
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print("[INFO] Issue criada com sucesso!")
    else:
        print(f"[ERROR] Falha ao criar issue: {response.status_code} - {response.text}")

# =======================
# Execução principal
# =======================
if __name__ == "__main__":
    report = read_report()
    labels = extract_labels(report)
    create_issue(title="AI Commit Analysis Report", body=report, labels=labels)
