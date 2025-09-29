import os
import requests

# =======================
# Configuração
# =======================
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")  # ex: "usuario/repositorio"
ISSUE_TITLE = "🤖 Commit Analysis Report"

if not GITHUB_TOKEN or not GITHUB_REPO:
    raise EnvironmentError("GH_TOKEN ou GITHUB_REPOSITORY não definidos.")

# =======================
# Ler relatório
# =======================
with open("report.md", "r", encoding="utf-8") as f:
    report_md = f.read()

# =======================
# Extrair labels do Markdown
# =======================
labels = ["ai-analysis"]  # sempre adiciona essa
if "**Critical:**" in report_md:
    labels.append("critical")
if "**High:**" in report_md:
    labels.append("high")
if "**Medium:**" in report_md:
    labels.append("medium")
if "**Low:**" in report_md:
    labels.append("low")

# =======================
# Criar issue
# =======================
url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
payload = {
    "title": ISSUE_TITLE,
    "body": report_md,
    "labels": labels
}

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"[INFO] Issue criada com sucesso: {response.json().get('html_url')}")
except Exception as e:
    print(f"[ERROR] Falha ao criar issue: {e}")
