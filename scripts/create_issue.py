import os
import requests

# Configurações
GH_TOKEN = os.getenv("GH_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")  # ex: "username/repo"
API_URL = f"https://api.github.com/repos/{REPO}/issues"

# Mapeamento de severidades para labels
LABEL_MAPPING = {
    "Critical": "critical",
    "High": "high",
    "Medium": "medium",
    "Low": "low"
}

def extract_labels(report):
    """Analisa o relatório e retorna labels correspondentes"""
    labels = []
    for severity, label in LABEL_MAPPING.items():
        if severity in report:
            labels.append(label)
    return labels if labels else ["ai-analysis"]  # fallback

def create_issue(title, body, labels=None):
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 201:
        raise Exception(f"GitHub API Error: {response.text}")
    print("✅ Issue created successfully with labels:", labels)

if __name__ == "__main__":
    # Lê o relatório gerado pelo analyze_diff.py
    with open("report.md", "r", encoding="utf-8") as f:
        report = f.read()

    labels = extract_labels(report)
    create_issue(
        title="🤖 AI Commit Analysis Report",
        body=report,
        labels=labels
    )
