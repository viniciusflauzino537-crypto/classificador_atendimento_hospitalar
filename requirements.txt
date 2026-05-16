import os
import json
import requests

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ==============================================================================
# PROMPT DO SISTEMA
# ==============================================================================

PROMPT_MEDICO_SISTEMA = """
Você é um sistema de triagem hospitalar inteligente.

Analise os sintomas do paciente e responda APENAS com JSON válido.

NÃO use:
- markdown
- blocos ```json
- explicações extras
- comentários
- texto fora do JSON

Formato obrigatório:

{
  "especialidade_recomendada": "CARDIOLOGIA",
  "nivel_prioridade": "EMERGENCIA",
  "justificativa_breve": "Resumo clínico curto"
}

As prioridades permitidas são SOMENTE:
- EMERGENCIA
- URGENCIA
- POUCO_URGENTE

A especialidade deve ser escolhida de acordo com os sintomas do paciente.

Especialidades permitidas:
- CLINICO_GERAL
- CARDIOLOGIA
- ORTOPEDIA
- NEUROLOGIA
- PEDIATRIA
- GASTROENTEROLOGIA
- PNEUMOLOGIA
- DERMATOLOGIA
- OTORRINOLARINGOLOGIA
- OFTALMOLOGIA
- UROLOGIA
- GINECOLOGIA
- OBSTETRICIA
- ENDOCRINOLOGIA
- PSIQUIATRIA
- HEMATOLOGIA
- NEFROLOGIA
- REUMATOLOGIA
- INFECTOLOGIA
- ONCOLOGIA
- CIRURGIA_GERAL
- CIRURGIA_VASCULAR
- ALERGOLOGIA
- IMUNOLOGIA
- TRAUMATOLOGIA
- PROCTOLOGIA
- ANGIOLOGIA
- MEDICINA_DO_TRABALHO
- GERIATRIA

Regras:
- Em caso de dúvida clínica, escolha a MAIOR prioridade.
- A resposta deve ser exclusivamente JSON válido.
- Nunca responda fora do formato solicitado.
"""

# ==============================================================================
# HOME
# ==============================================================================

@app.route('/')
def home():
    return render_template('index.html')

# ==============================================================================
# TRIAGEM
# ==============================================================================

@app.route('/triagem/paciente', methods=['POST'])
def processar_triagem():

    try:

        # ----------------------------------------------------------------------
        # RECEBE JSON
        # ----------------------------------------------------------------------

        dados_hospital = request.get_json(silent=True)

        if not dados_hospital:

            return jsonify({
                "erro": "JSON inválido."
            }), 400

        relato = dados_hospital.get('relato_sintomas')

        if not relato:

            return jsonify({
                "erro": "Campo 'relato_sintomas' é obrigatório."
            }), 400

        # ----------------------------------------------------------------------
        # API KEY
        # ----------------------------------------------------------------------

        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:

            return jsonify({
                "erro": "Variável OPENROUTER_API_KEY não configurada."
            }), 500

        # ----------------------------------------------------------------------
        # HEADERS
        # ----------------------------------------------------------------------

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://render.com",
            "X-Title": "HospTech Triagem IA"
        }

        # ----------------------------------------------------------------------
        # PAYLOAD
        # ----------------------------------------------------------------------

        payload = {
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "system",
                    "content": PROMPT_MEDICO_SISTEMA
                },
                {
                    "role": "user",
                    "content": f"Sintomas do paciente: {relato}"
                }
            ],
            "temperature": 0,
            "max_tokens": 300
        }

        # ----------------------------------------------------------------------
        # REQUEST OPENROUTER
        # ----------------------------------------------------------------------

        resposta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        resposta.raise_for_status()

        dados_ia = resposta.json()

        # ----------------------------------------------------------------------
        # VALIDA RESPOSTA
        # ----------------------------------------------------------------------

        if 'choices' not in dados_ia:

            return jsonify({
                "erro": "Resposta inválida da IA.",
                "detalhes": dados_ia
            }), 500

        if not dados_ia['choices']:

            return jsonify({
                "erro": "Nenhuma resposta retornada pela IA."
            }), 500

        # ----------------------------------------------------------------------
        # EXTRAI TEXTO
        # ----------------------------------------------------------------------

        resultado_texto = (
            dados_ia['choices'][0]
            ['message']
            ['content']
            .strip()
        )

        # ----------------------------------------------------------------------
        # LIMPEZA DE MARKDOWN
        # ----------------------------------------------------------------------

        resultado_texto = resultado_texto.replace("\n", " ").strip()

        if "```json" in resultado_texto:
            resultado_texto = resultado_texto.replace("```json", "")

        if "```" in resultado_texto:
            resultado_texto = resultado_texto.replace("```", "")

        resultado_texto = resultado_texto.strip()

        # ----------------------------------------------------------------------
        # CONVERTE JSON
        # ----------------------------------------------------------------------

        dados_final = json.loads(resultado_texto)

        # ----------------------------------------------------------------------
        # VALIDA CAMPOS
        # ----------------------------------------------------------------------

        campos_obrigatorios = [
            "especialidade_recomendada",
            "nivel_prioridade",
            "justificativa_breve"
        ]

        for campo in campos_obrigatorios:

            if campo not in dados_final:

                raise ValueError(
                    f"Campo obrigatório ausente: {campo}"
                )

        # ----------------------------------------------------------------------
        # VALIDA PRIORIDADES
        # ----------------------------------------------------------------------

        prioridades_validas = [
            "EMERGENCIA",
            "URGENCIA",
            "POUCO_URGENTE"
        ]

        if dados_final["nivel_prioridade"] not in prioridades_validas:

            raise ValueError(
                "Prioridade inválida retornada pela IA."
            )

        # ----------------------------------------------------------------------
        # SUCESSO
        # ----------------------------------------------------------------------

        return jsonify(dados_final), 200

    # ==========================================================================
    # JSON INVÁLIDO
    # ==========================================================================

    except json.JSONDecodeError:

        fallback = {
            "especialidade_recomendada": "CLINICO_GERAL",
            "nivel_prioridade": "EMERGENCIA",
            "justificativa_breve":
                "Falha ao interpretar a resposta da IA."
        }

        return jsonify(fallback), 200

    # ==========================================================================
    # TIMEOUT
    # ==========================================================================

    except requests.Timeout:

        return jsonify({
            "erro": "Timeout ao conectar com a IA."
        }), 504

    # ==========================================================================
    # ERRO HTTP OPENROUTER
    # ==========================================================================

    except requests.HTTPError:

        return jsonify({
            "erro": "Erro HTTP da API OpenRouter.",
            "status_code": resposta.status_code,
            "detalhes": resposta.text
        }), 502

    # ==========================================================================
    # ERRO GERAL
    # ==========================================================================

    except Exception as e:

        return jsonify({
            "erro": "Erro interno do servidor.",
            "detalhes": str(e)
        }), 500

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':

    porta = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=porta,
        debug=False
    )