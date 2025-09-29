import os
import subprocess
import json
import sys
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# ==============================================================================
# 1. CONFIGURAÇÃO E CREDENCIAIS
# ==============================================================================

# Carrega as credenciais da Google a partir de uma variável de ambiente.
# O conteúdo desta variável deve ser o JSON completo da service account.
service_account_json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if not service_account_json_str:
    sys.exit("[ERROR] A variável de ambiente GOOGLE_SERVICE_ACCOUNT_JSON não foi definida.")

try:
    creds_dict = json.loads(service_account_json_str)
    project_id = creds_dict.get("project_id")
    if not project_id:
        raise ValueError("O JSON da service account não contém 'project_id'.")
except (json.JSONDecodeError, ValueError) as e:
    sys.exit(f"[ERROR] O JSON em GOOGLE_SERVICE_ACCOUNT_JSON é inválido: {e}")

# Cria as credenciais e obtém um token de acesso
credentials = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
if not credentials.valid:
    credentials.refresh(Request())
ACCESS_TOKEN = credentials.token

# Configurações do GitHub
GH_TOKEN = os.getenv("GH_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
if not GH_TOKEN or not REPO:
    sys.exit("[ERROR] GH_TOKEN ou GITHUB_REPOSITORY não foram definidos.")

# Mapeamento de severidade para labels do GitHub
LABEL_MAPPING = {
    "Critical": "critical",
    "High": "high",
    "Medium": "medium",
    "Low": "low"
}

# Prompt de sistema para guiar a análise da IA
SYSTEM_PROMPT = """
Você é um revisor de código sênior especialista em .NET e C#. Sua tarefa é analisar um 'git diff' e identificar potenciais problemas, bugs, vulnerabilidades de segurança, problemas de performance ou desvios das boas práticas.

Formate sua resposta OBRIGATORIAMENTE em Markdown, usando a seguinte estrutura:

## 🤖 Relatório de Análise de Commit

### Pontos de Atenção
Liste aqui os problemas encontrados, classificando-os por severidade. Para cada ponto, descreva o problema, sugira uma solução e indique o arquivo e a linha.

- **Critical:** (Problemas que podem causar falhas críticas, perda de dados ou vulnerabilidades de segurança graves. Ex: Injeção de SQL, senhas hardcoded, loops infinitos).
- **High:** (Problemas que podem levar a bugs significativos, exceções não tratadas, ou degradação de performance. Ex: Falta de validação de input, uso de `Thread.Sleep` em código assíncrono).
- **Medium:** (Desvios de boas práticas, código difícil de manter ou "code smells". Ex: Nomes de variáveis confusos, métodos muito longos, comentários desatualizados).
- **Low:** (Sugestões menores de estilo ou limpeza de código. Ex: Uso de `var` inconsistente, linhas em branco desnecessárias).

Se nenhum problema for encontrado, responda com "Nenhum problema significativo encontrado na análise.".
"""


# ==============================================================================
# 2. FUNÇÕES PRINCIPAIS
# ==============================================================================

def get_commit_diff():
    """Captura as diferenças (diff) do último commit."""
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"], text=True, stderr=subprocess.PIPE)
        if not diff.strip():
            print("[INFO] Nenhum 'diff' detectado. Pode ser um commit de merge sem alterações.")
            return None
        return diff
    except subprocess.CalledProcessError:
        print("[WARN] Não foi possível obter o 'diff'. Pode ser o primeiro commit do repositório.")
        return None

def analyze_with_gemini(diff_content):
    """Envia o diff para a API do Gemini e retorna a análise formatada."""
    print("[INFO] Enviando 'diff' para análise do Gemini...")
    
    # Endpoint correto para a API Generative Language (Gemini)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={ACCESS_TOKEN}"

    # Payload no formato correto para o endpoint :generateContent
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": "Analise o seguinte git diff:\n\n```diff\n" + diff_content + "\n```"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }
    
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        
        result = response.json()
        # Extrai o texto da resposta, navegando pela estrutura correta
        content = result['candidates'][0]['content']['parts'][0]['text']
        print("[INFO] Análise recebida do Gemini com sucesso.")
        return content

    except requests.RequestException as e:
        print(f"[ERROR] Falha ao chamar a API do Gemini: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"[ERROR] Resposta da API: {e.response.text}", file=sys.stderr)
        return "## 🚨 Erro na Análise\n\nNão foi possível gerar o relatório de análise via Gemini."
    except (KeyError, IndexError) as e:
        print(f"[ERROR] Formato de resposta inesperado do Gemini: {e}", file=sys.stderr)
        print(f"[DEBUG] Resposta completa: {result}")
        return "## 🚨 Erro na Análise\n\nOcorreu um erro ao processar a resposta do Gemini."

def create_github_issue(title, body):
    """Cria uma issue no repositório do GitHub com labels baseados no corpo."""
    print("[INFO] Criando issue no GitHub...")
    
    # Extrai labels com base nas palavras-chave de severidade no relatório
    labels = [label for severity, label in LABEL_MAPPING.items() if severity in body]
    if not labels:
        labels.append("ai-analysis") # Label padrão se nenhuma severidade for encontrada

    api_url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"title": title, "body": body, "labels": list(set(labels))} # Usa set para evitar labels duplicados

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        print(f"[SUCCESS] Issue criada com sucesso com os labels: {labels}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Falha ao criar a issue no GitHub: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"[ERROR] Resposta da API: {e.response.text}", file=sys.stderr)
        sys.exit(1)


# ==============================================================================
# 3. EXECUÇÃO PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    commit_diff = get_commit_diff()
    
    if commit_diff:
        analysis_report = analyze_with_gemini(commit_diff)
        create_github_issue(
            title="🤖 Relatório de Análise de Commit por IA",
            body=analysis_report
        )
    else:
        print("[INFO] Finalizando o script pois não há alterações para analisar.")
