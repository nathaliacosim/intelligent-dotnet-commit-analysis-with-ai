# 📄 Documentação Técnica — Análise Inteligente de Commits .NET com IA (OpenAI)

## 1. 🎯 Visão Geral

Este projeto implementa um **agente automatizado** para análise inteligente de commits em **repositórios .NET** hospedados no GitHub.

Sempre que um commit é detectado, o agente:

1. Captura o **diff do código**.
2. Envia para o **OpenAI (gpt-3.5-turbo)** para análise.
3. Recebe um **relatório de possíveis problemas**.
4. Cria automaticamente uma **issue no GitHub** com labels de severidade (`Critical`, `High`, `Medium`, `Low`).

O objetivo é **melhorar a qualidade do código** e **reduzir falhas em produção**, integrando IA ao fluxo de desenvolvimento.

---

## 2. 🧱 Arquitetura do Sistema

```plaintext
Commit GitHub → GitHub Actions → Captura Diff → IA (OpenAI) → Relatório → Criação de Issue
```

### Componentes Principais

| Componente           | Responsabilidade                                     |
| -------------------- | ---------------------------------------------------- |
| **GitHub Actions**   | Detecta commits e dispara o pipeline de análise      |
| **Script de Diff**   | Extrai alterações usando `git diff` ou API do GitHub |
| **Integração IA**    | Envia diff para OpenAI e recebe o relatório          |
| **Gerador de Issue** | Cria issue no GitHub com o resultado da análise      |

---

## 3. ⚙️ Tecnologias

* **GitHub Actions** → Automação CI/CD
* **.NET (C#)** → Linguagem base do repositório
* **OpenAI API** → Análise inteligente de código
* **Python / Node.js** → Scripts de integração
* **GitHub REST API** → Criação automatizada de issues
* **GitHub Secrets** → Armazenamento seguro de tokens e chaves

---

## 4. 📂 Estrutura de Diretórios

```
.github/
└── workflows/
    └── analyze-commit.yml    # Workflow do GitHub Actions

scripts/
├── analyze_diff.py           # Captura diff e chama OpenAI
└── create_issue.py           # Cria issue no GitHub

README.md
.env.example                   # Template para variáveis de ambiente
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
        run: pip install requests python-dotenv

      - name: Executar análise
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_PAT }}
        run: python scripts/analyze_diff.py
```

### 5.2. Script de Análise (`analyze_diff.py`)

* Extrai o diff do commit com segurança (`git rev-parse HEAD~1` fallback).
* Prepara o prompt para o OpenAI.
* Envia o diff para análise de IA (com timeout e retry).
* Salva o relatório em Markdown (`report.md`).

### 5.3. Script de Criação de Issue (`create_issue.py`)

* Lê o relatório em Markdown.
* Extrai labels a partir das severidades detectadas.
* Cria uma issue no GitHub via API com retry e logging.

---

## 6. 🧠 Prompt de IA

```plaintext
Analise o seguinte diff de código .NET.
Classifique possíveis problemas como: Critical, High, Medium, Low.
Explique cada um brevemente.
Retorne o resultado em Markdown incluindo:

- Resumo das alterações
- Problemas detectados com severidade
- Sugestões de melhoria (opcional)

_Análise gerada automaticamente pelo OpenAI._
```

---

## 7. 🔐 Configuração de Secrets

No repositório GitHub, configure:

* `OPENAI_API_KEY` → Chave da API OpenAI (free tier disponível)
* `GH_PAT` → Token pessoal do GitHub com permissão **repo:issues**

---

## 8. 📋 Exemplo de Issue Gerada

```markdown
## 🔍 Relatório de Análise de Commit
**Commit:** abc123  
**Branch:** main  
**Autor:** @nathalia  

### ⚠️ Problemas Detectados
- **Critical:** Uso de `Thread.Sleep` em ambiente assíncrono  
- **High:** Falta de validação de entrada em método público  
- **Medium:** Comentários desatualizados  
- **Low:** Nome de variável pouco descritivo  

**Sugestões de melhoria:** (opcional)

_Análise gerada automaticamente pelo OpenAI._
```

---

## 9. ✅ Testes e Validação

* Commits simulados com problemas conhecidos.
* Verificação da criação correta de issues e labels.
* Ajuste iterativo do prompt da IA para maior precisão.

---

## 10. 🚀 Futuras Melhorias

* Suporte multi-linguagem além de .NET.
* Análise de Pull Requests antes do merge.
* Sugestões de correção automática.
* Integração com ferramentas de qualidade (SonarQube, CodeQL).
* Observabilidade → Monitoramento de tempo de resposta e erros da IA.