# 📄 Technical Documentation — Intelligent .NET Commit Analysis with AI (Gemini)

## 1. 🎯 Overview

This project implements an **automated agent** for intelligent commit analysis in **.NET repositories** hosted on GitHub.

Whenever a commit is detected, the agent:

1. Captures the **code diff**.
2. Sends it to **Gemini AI** for analysis.
3. Receives a **report with potential issues**.
4. Automatically creates a **GitHub issue** with severity labels (`Critical`, `High`, `Medium`, `Low`).

The goal is to **improve code quality** and **reduce production failures** by embedding AI into the development workflow.

---

## 2. 🧱 System Architecture

```plaintext
GitHub Commit → GitHub Actions → Capture Diff → AI (Gemini) → Report → Create Issue
```

### Main Components

| Component           | Responsibility                                       |
| ------------------- | ---------------------------------------------------- |
| **GitHub Actions**  | Detects commits and triggers the analysis pipeline   |
| **Diff Script**     | Extracts changes using `git diff` or GitHub API      |
| **AI Integration**  | Sends the diff to Gemini API and receives the report |
| **Issue Generator** | Creates a GitHub issue with the analysis results     |

---

## 3. ⚙️ Technologies

* **GitHub Actions** → CI/CD automation
* **.NET (C#)** → Base repository language
* **Gemini API / Vertex AI** → Intelligent code analysis
* **Python / Node.js** → Integration scripts
* **GitHub REST API** → Automated issue creation
* **GitHub Secrets** → Secure storage for API keys and tokens

---

## 4. 📂 Directory Structure

```
.github/
└── workflows/
    └── analyze-commit.yml    # GitHub Actions workflow

scripts/
├── analyze_diff.py           # Captures diff and calls Gemini
└── create_issue.py           # Creates GitHub issue

README.md
.env.example                   # Template for environment variables
```

---

## 5. 🔄 Execution Flow

### 5.1. Workflow (`analyze-commit.yml`)

```yaml
on:
  push:
    branches:
      - main
      - develop

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 2  # ensures HEAD~1 exists

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests google-cloud-aiplatform python-dotenv

      - name: Run analysis
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
          GH_TOKEN: ${{ secrets.GH_PAT }}
        run: python scripts/analyze_diff.py
```

### 5.2. Analysis Script (`analyze_diff.py`)

* Extracts the commit diff safely (`git rev-parse HEAD~1` fallback).
* Prepares the prompt for Gemini AI.
* Sends the diff for AI analysis via **Vertex AI TextGenerationModel** (with timeout & retry).
* Saves a Markdown report (`report.md`).

### 5.3. Issue Creation Script (`create_issue.py`)

* Reads the Markdown report.
* Extracts labels from severity levels.
* Creates a GitHub issue via API with retry and logging.

---

## 6. 🧠 AI Prompt

```plaintext
Analise o seguinte diff de código .NET.
Classifique potenciais problemas como: Crítica, Alta, Média, Baixa.
Descreva brevemente cada um.
Retorne o resultado em formato Markdown incluindo:

- Resumo das alterações
- Problemas detectados com severidade
- Sugestões de melhoria (opcional)

_Análise gerada automaticamente pelo Gemini AI._
```

---

## 7. 🔐 Secrets Configuration

In GitHub repository settings, configure:

* `GOOGLE_CREDENTIALS` → JSON key for Vertex AI / Gemini service account
* `GH_PAT` → GitHub token with **repo:issues** permission

---

## 8. 📋 Example of Generated Issue

```markdown
## 🔍 Commit Analysis Report
**Commit:** abc123  
**Branch:** main  
**Author:** @nathalia  

### ⚠️ Detected Issues
- **Critical:** Uso de `Thread.Sleep` em ambiente assíncrono  
- **High:** Falta de validação de entrada em método público  
- **Medium:** Comentários desatualizados  
- **Low:** Nome de variável pouco descritivo  

**Sugestões de melhoria:** (opcional)

_Análise gerada automaticamente pelo Gemini AI._ 🤖
```

---

## 9. ✅ Testing & Validation

* Test with simulated commits containing known issues.
* Verify issue creation with correct labels.
* Iteratively adjust AI prompt for accuracy.

---

## 10. 🚀 Future Improvements

* Multi-language support beyond .NET
* Pull Request analysis before merge
* Automated fix suggestions
* Integration with quality tools (SonarQube, CodeQL)
* Observability → Monitoring AI response times and error rates