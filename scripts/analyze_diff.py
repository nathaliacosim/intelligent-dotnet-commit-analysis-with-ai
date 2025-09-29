import os
import subprocess
import requests
import json

# Configurações
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://api.gemini-mini.fake/analyze"  # ajuste para a URL real

def get_commit_diff():
    """Captura o diff do último commit"""
    diff = subprocess.check_output(
        ["git", "diff", "HEAD~1", "HEAD"], text=True
    )
    return diff

def analyze_with_ai(diff):
    return """## Commit Analysis Report

    ### ⚠️ Issues
    - **Critical:** Mock issue - Thread.Sleep used
    - **High:** Mock issue - Missing input validation
    - **Medium:** Mock issue - Outdated comments
    - **Low:** Mock issue - Non-descriptive variable name
    """

#def analyze_with_ai(diff):
    #"""Envia o diff para a IA"""
    # headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    # payload = {
    #     "prompt": f"Analyze the following .NET code diff:\n{diff}\n\n"
    #               "Classify issues as Critical, High, Medium, Low. "
    #               "Explain briefly. Return in Markdown."
    # }

    # response = requests.post(API_URL, headers=headers, json=payload)

    # if response.status_code != 200:
    #     raise Exception(f"AI API Error: {response.text}")

    # return response.json().get("report", "")

def save_report(report):
    """Salva relatório em arquivo para ser usado depois"""
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    diff = get_commit_diff()
    report = analyze_with_ai(diff)
    save_report(report)

    # Chama script que cria issue
    subprocess.run(["python", "scripts/create_issue.py"], check=True)
