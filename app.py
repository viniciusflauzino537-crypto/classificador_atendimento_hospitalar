<!DOCTYPE html>
<html lang="pt-BR">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HospTech - Triagem Inteligente</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
</head>

<body class="bg-light">

    <!-- NAVBAR -->
    <nav class="navbar navbar-dark bg-primary shadow-sm">
        <div class="container">

            <span class="navbar-brand mb-0 h1">
                <i class="bi bi-heart-pulse-fill me-2"></i>
                HospTech | Triagem de Saúde IA
            </span>

            <span class="badge bg-light text-primary py-2 px-3 border">
                Flask + OpenRouter
            </span>

        </div>
    </nav>

    <!-- CONTEÚDO -->
    <div class="container my-5">

        <div class="row g-4">

            <!-- FORM -->
            <div class="col-lg-6">

                <div class="card border-0 shadow-sm h-100">

                    <div class="card-header bg-white border-0 pt-4 px-4">

                        <h5 class="card-title fw-bold text-secondary">
                            <i class="bi bi-file-earmark-medical me-2"></i>
                            Prontuário de Entrada
                        </h5>

                        <p class="text-muted small">
                            Insira o relato completo dos sintomas do paciente.
                        </p>

                    </div>

                    <div class="card-body px-4 pb-4">

                        <form id="formTriagem">

                            <div class="mb-3">

                                <label for="relato" class="form-label fw-semibold text-muted">
                                    Relato de Sintomas:
                                </label>

                                <textarea
                                    class="form-control"
                                    id="relato"
                                    rows="7"
                                    placeholder="Ex: Paciente com forte dor no peito, falta de ar, suor excessivo e tontura..."
                                    required></textarea>

                            </div>

                            <button
                                type="submit"
                                id="btnEnviar"
                                class="btn btn-primary w-100 py-2 fw-bold">

                                <i class="bi bi-cpu-fill me-2"></i>
                                Processar Triagem

                            </button>

                        </form>

                        <!-- LEGENDA -->

                        <div class="mt-4">

                            <h6 class="fw-bold text-secondary mb-3">
                                <i class="bi bi-info-circle me-2"></i>
                                Legenda de Prioridades
                            </h6>

                            <div class="d-flex flex-column gap-2">

                                <div class="alert alert-danger py-2 mb-0">
                                    <strong>EMERGÊNCIA:</strong>
                                    risco imediato à vida.
                                </div>

                                <div class="alert alert-warning py-2 mb-0">
                                    <strong>URGÊNCIA:</strong>
                                    necessita atendimento rápido.
                                </div>

                                <div class="alert alert-success py-2 mb-0">
                                    <strong>POUCO URGENTE:</strong>
                                    sintomas leves ou estáveis.
                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

            <!-- RESULTADO -->
            <div class="col-lg-6">

                <div class="card border-0 shadow-sm h-100">

                    <div class="card-header bg-white border-0 pt-4 px-4">

                        <h5 class="card-title fw-bold text-secondary">
                            <i class="bi bi-clipboard2-pulse me-2"></i>
                            Resultado da Triagem
                        </h5>

                    </div>

                    <div
                        class="card-body px-4 d-flex flex-column justify-content-center align-items-center text-center"
                        id="painelResultado">

                        <!-- AGUARDANDO -->

                        <div id="estadoAguardando">

                            <i class="bi bi-robot text-muted display-1"></i>

                            <p class="text-muted mt-3">
                                Aguardando envio do prontuário para análise.
                            </p>

                        </div>

                        <!-- CARREGANDO -->

                        <div id="estadoCarregando" class="d-none">

                            <div
                                class="spinner-border text-primary"
                                style="width: 3rem; height: 3rem;"
                                role="status"></div>

                            <p class="text-primary fw-semibold mt-3">
                                A IA está analisando os sintomas...
                            </p>

                        </div>

                        <!-- SUCESSO -->

                        <div id="estadoSucesso" class="w-100 d-none text-start">

                            <!-- PRIORIDADE -->

                            <div
                                id="bordaPrioridade"
                                class="p-3 mb-3 bg-light rounded border-start border-4">

                                <h6 class="text-muted text-uppercase fw-bold small mb-1">
                                    Classificação de Risco
                                </h6>

                                <h3 class="fw-bold mb-0" id="resPrioridade">
                                    ---
                                </h3>

                            </div>

                            <!-- ESPECIALIDADE -->

                            <div class="mb-3">

                                <span class="text-muted d-block small fw-semibold">
                                    Especialidade Recomendada:
                                </span>

                                <span
                                    class="badge bg-secondary fs-6 py-2 px-3 mt-1"
                                    id="resEspecialidade">

                                    ---

                                </span>

                            </div>

                            <!-- JUSTIFICATIVA -->

                            <div class="mb-0">

                                <span class="text-muted d-block small fw-semibold">
                                    Justificativa da IA:
                                </span>

                                <p
                                    class="alert alert-info mt-2 mb-0"
                                    id="resJustificativa">

                                    ---

                                </p>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    </div>

    <!-- SCRIPT -->

    <script>

        document.getElementById('formTriagem')
            .addEventListener('submit', async (e) => {

                e.preventDefault();

                const relatoTexto =
                    document.getElementById('relato').value.trim();

                const btn =
                    document.getElementById('btnEnviar');

                const estadoAguardando =
                    document.getElementById('estadoAguardando');

                const estadoCarregando =
                    document.getElementById('estadoCarregando');

                const estadoSucesso =
                    document.getElementById('estadoSucesso');

                const painelBorda =
                    document.getElementById('bordaPrioridade');

                if (!relatoTexto) {

                    alert('Informe os sintomas do paciente.');

                    return;
                }

                estadoAguardando.classList.add('d-none');
                estadoSucesso.classList.add('d-none');
                estadoCarregando.classList.remove('d-none');

                btn.disabled = true;

                try {

                    const resposta = await fetch('/triagem/paciente', {

                        method: 'POST',

                        headers: {
                            'Content-Type': 'application/json'
                        },

                        body: JSON.stringify({
                            relato_sintomas: relatoTexto
                        })

                    });

                    const dados = await resposta.json();

                    if (!resposta.ok) {

                        throw new Error(
                            dados.erro || 'Erro ao processar triagem.'
                        );
                    }

                    painelBorda.className =
                        "p-3 mb-3 bg-light rounded border-start border-4";

                    if (dados.nivel_prioridade === 'EMERGENCIA') {

                        painelBorda.classList.add('border-danger');

                    } else if (dados.nivel_prioridade === 'URGENCIA') {

                        painelBorda.classList.add('border-warning');

                    } else {

                        painelBorda.classList.add('border-success');
                    }

                    document.getElementById('resPrioridade').innerText =
                        dados.nivel_prioridade;

                    document.getElementById('resEspecialidade').innerText =
                        dados.especialidade_recomendada;

                    document.getElementById('resJustificativa').innerText =
                        dados.justificativa_breve;

                    estadoCarregando.classList.add('d-none');

                    estadoSucesso.classList.remove('d-none');

                } catch (error) {

                    console.error(error);

                    alert(
                        error.message ||
                        'Erro crítico ao se conectar ao servidor.'
                    );

                    estadoCarregando.classList.add('d-none');

                    estadoAguardando.classList.remove('d-none');

                } finally {

                    btn.disabled = false;
                }

            });

    </script>

</body>

</html>