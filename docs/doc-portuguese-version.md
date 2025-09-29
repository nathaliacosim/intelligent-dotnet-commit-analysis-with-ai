# 📄 Documentação Técnica — Análise Inteligente de Commits .NET com AI (Gemini)

## 1. 🎯 Visão Geral

Este projeto implementa um **agente automatizado** para análise inteligente de commits em repositórios **.NET** hospedados no GitHub.

Sempre que um commit é detectado, o agente:

1. Captura o **diff do código**.
2. Envia para o **Gemini AI** para análise.
3. Recebe um **relatório com potenciais problemas**.
4. Cria automaticamente uma **issue no GitHub** com labels de severidade (`Crítica`, `Alta`, `Média`, `Baixa`).

O objetivo é **melhorar a qualidade do código** e **reduzir falhas em produção**, integrando AI ao fluxo de desenvolvimento.

---

## 2. 🧱 Arquitetura do Sistema

```plaintext
Commit GitHub → GitHub Actions → Captura Diff → AI (Gemini) → Relatório → Cria Issue
```

### Componentes Principais

| Componente            | Responsabilidade                                    |
| --------------------- | --------------------------------------------------- |
| **GitHub Actions**    | Detecta commits e dispara a pipeline de análise     |
| **Script de Diff**    | Extrai alterações usando `git diff` ou GitHub API   |
| **Integração AI**     | Envia o diff para a API Gemini e recebe o relatório |
| **Gerador de Issues** | Cria a issue no GitHub com os resultados da análise |

---

## 3. ⚙️ Tecnologias

* **GitHub Actions** → Automação CI/CD
* **.NET (C#)** → Linguagem base do repositório
* **Gemini AI / Vertex AI** → Análise inteligente de código
* **Python / Node.js** → Scripts de integração
* **GitHub REST API** → Criação automatizada de issues
* **GitHub Secrets** → Armazenamento seguro de chaves e tokens

---

## 4. 📂 Estrutura de Diretórios

```
.github/
└── workflows/
    └── analyze-commit.yml    # Workflow do GitHub Actions

scripts/
├── analyze_diff.py           # Captura diff e chama Gemini
└── create_issue.py           # Cria a issue no GitHub

README.md
.env.example                   # Modelo de variáveis de ambiente
```

---

## 5. 🔄 Fluxo de Execução

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
      - name: Checkout do código
        uses: actions/checkout@v3
        with:
          fetch-depth: 2  # garante que HEAD~1 exista

      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Instalar dependências
        run: pip install requests google-cloud-aiplatform python-dotenv

      - name: Rodar análise
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
          GH_TOKEN: ${{ secrets.GH_PAT }}
        run: python scripts/analyze_diff.py
```

### 5.2. Script de Análise (`analyze_diff.py`)

* Extrai o diff do commit de forma segura (`git rev-parse HEAD~1` como fallback).
* Prepara o prompt para o Gemini AI.
* Envia o diff para análise AI (com timeout e retries).
* Salva um relatório em Markdown (`report.md`).

### 5.3. Script de Criação de Issue (`create_issue.py`)

* Lê o relatório em Markdown.
* Extrai labels de acordo com as severidades detectadas.
* Cria a issue no GitHub via API, com retry e logs.

---

## 6. 🧠 Prompt para AI

```plaintext
Analise o seguinte diff de código .NET.
Classifique potenciais problemas como: Crítica, Alta, Média, Baixa.
Descreva brevemente cada um.
Retorne o resultado em Markdown incluindo:

- Resumo das alterações
- Problemas detectados com severidade
- Sugestões de melhoria (opcional)

_Análise gerada automaticamente pelo Gemini AI._
```

---

## 7. 🔐 Configuração de Secrets

No repositório GitHub, configure:

* `GOOGLE_CREDENTIALS` → JSON da conta de serviço Vertex AI / Gemini
* `GH_PAT` → Token GitHub com permissão **repo:issues**

---

## 8. 📋 Exemplo de Issue Gerada

```markdown
## 🔍 Relatório de Análise de Commit
**Commit:** abc123  
**Branch:** main  
**Autor:** @nathalia  

### ⚠️ Problemas Detectados
- **Crítica:** Uso de `Thread.Sleep` em ambiente assíncrono  
- **Alta:** Falta de validação de entrada em método público  
- **Média:** Comentários desatualizados  
- **Baixa:** Nome de variável pouco descritivo  

**Sugestões de melhoria:** (opcional)

_Análise gerada automaticamente pelo Gemini AI._ 🤖
```

---

## 9. ✅ Testes e Validação

* Testes com commits simulados contendo problemas conhecidos.
* Verificação da criação correta de issues com labels.
* Ajuste iterativo do prompt para melhorar a precisão da AI.

---

## 10. 🚀 Melhorias Futuras

* Suporte multi-linguagem além de .NET
* Análise de Pull Requests antes do merge
* Sugestões automáticas de correção
* Integração com ferramentas de qualidade (SonarQube, CodeQL)
* Observabilidade → Monitoramento de tempo de resposta e erros da AI