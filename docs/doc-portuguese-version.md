# 📄 Documentação Técnica - Análise Inteligente de Commits .NET com IA

## 1. 🎯 Visão Geral

Este projeto tem como objetivo criar um agente automatizado que, ao detectar um commit em um repositório .NET hospedado no GitHub, analisa o diff do código utilizando uma IA (como Gemini Mini) e publica um relatório de falhas em uma issue no próprio repositório.

---

## 2. 🧱 Arquitetura do Sistema

```plaintext
GitHub Commit → GitHub Actions → Captura Diff → Envia para IA → Recebe Relatório → Cria Issue
```

### Componentes:

| Componente         | Função                                                                 |
|--------------------|------------------------------------------------------------------------|
| GitHub Actions     | Detecta commits e executa o pipeline de análise                        |
| Script de Diff     | Extrai alterações do commit usando `git diff` ou GitHub API            |
| Integração IA      | Envia o diff para análise via API da Gemini Mini                       |
| Gerador de Issue   | Cria uma issue no repositório com o relatório gerado pela IA           |

---

## 3. ⚙️ Tecnologias Utilizadas

- **GitHub Actions** – CI/CD para automação
- **.NET (C#)** – Linguagem base do repositório
- **Gemini Mini API** – Motor de análise de código via IA
- **Node.js ou Python** – Scripts de integração
- **GitHub REST API** – Criação de issues automatizadas
- **Secrets** – Armazenamento seguro de tokens e chaves de API

---

## 4. 🧩 Estrutura de Diretórios

```
.github/
└── workflows/
    └── analyze-commit.yml

scripts/
└── analyze_diff.py (ou .js)
└── create_issue.py (ou .js)

README.md
```

---

## 5. 🔄 Fluxo de Execução

### 5.1. GitHub Action (`analyze-commit.yml`)
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
      - name: Checkout código
        uses: actions/checkout@v3

      - name: Instalar dependências
        run: pip install requests (ou npm install)

      - name: Executar análise
        run: python scripts/analyze_diff.py
```

### 5.2. Script de Análise (`analyze_diff.py`)
- Captura o diff do commit
- Gera prompt para IA
- Envia para Gemini Mini via API
- Recebe relatório com classificação de falhas

### 5.3. Script de Issue (`create_issue.py`)
- Formata o relatório em Markdown
- Cria uma issue via GitHub API
- Adiciona labels como `critical`, `high`, `medium`, `low`

---

## 6. 🧠 Prompt para IA

```plaintext
Analise o seguinte diff de código .NET. Classifique possíveis falhas em: crítica, alta, média e baixa. Explique cada uma brevemente. Retorne em formato Markdown.
```

---

## 7. 🔐 Configuração de Secrets

No GitHub, adicione os seguintes secrets:

- `GEMINI_API_KEY` – Chave de acesso à Gemini Mini
- `GH_TOKEN` – Token de acesso ao GitHub com permissão para criar issues

---

## 8. 📋 Exemplo de Issue Gerada

```markdown
## Relatório de Análise de Commit

**Commit:** abc123  
**Branch:** main  
**Autor:** @nathalia

### ⚠️ Falhas Detectadas
- **Crítica:** Uso de `Thread.Sleep` em ambiente assíncrono
- **Alta:** Falta de validação de entrada em método público
- **Média:** Comentários desatualizados
- **Baixa:** Nome de variável pouco descritivo

_Análise gerada automaticamente via IA._
```

---

## 9. ✅ Testes e Validação

- Commits simulados com falhas conhecidas
- Verificação da criação correta de issues
- Avaliação da precisão da IA e ajuste do prompt

---

## 10. 📈 Possíveis Evoluções

- Suporte a múltiplas linguagens além de .NET
- Análise de pull requests
- Sugestões de correção automática
- Integração com ferramentas de segurança como SonarQube