// Arquivo de cálculos para o sistema de ecocardiograma
// Implementação baseada no arquivo calculos_ecocardiograficos.py

$(document).ready(function() {
    // Função principal para calcular todos os parâmetros
    function calcularParametrosEcocardiograficos() {
        // Obter valores dos campos
        const peso_kg = parseFloat($("#peso").val()) || 0;
        const altura_cm = parseFloat($("#altura").val()) || 0;
        const FC = parseFloat($("#frequencia_cardiaca").val()) || 0;
        const AE_mm = parseFloat($("#atrio_esquerdo").val()) || 0;
        const Ao_mm = parseFloat($("#raiz_aorta").val()) || 0;
        const Ao_asc_mm = parseFloat($("#aorta_ascendente").val()) || 0;
        const VD_mm = parseFloat($("#diametro_ventricular_direito").val()) || 0;
        const VD_basal_mm = parseFloat($("#diametro_basal_vd").val()) || 0;
        const DDVE_mm = parseFloat($("#diametro_diastolico_final_ve").val()) || 0;
        const DSVE_mm = parseFloat($("#diametro_sistolico_final").val()) || 0;
        const SIV_mm = parseFloat($("#espessura_diastolica_septo").val()) || 0;
        const PP_mm = parseFloat($("#espessura_diastolica_ppve").val()) || 0;
        const vel_fluxo_pulm = parseFloat($("#fluxo_pulmonar").val()) || 0;
        const vel_fluxo_ao = parseFloat($("#fluxo_aortico").val()) || 0;
        const vel_fluxo_mitral = parseFloat($("#fluxo_mitral").val()) || 0;
        const vel_fluxo_tricuspide = parseFloat($("#fluxo_tricuspide").val()) || 0;
        const pressao_AD = parseFloat($("#pressao_atrio_direito").val()) || 0;

        // Superfície Corporal (m²)
        const SC = 0.007184 * Math.pow(peso_kg, 0.425) * Math.pow(altura_cm, 0.725);
        $("#superficie_corporal").val(SC.toFixed(2));

        // Conversão de mm para cm
        const DDVE = DDVE_mm / 10;
        const DSVE = DSVE_mm / 10;
        const SIV = SIV_mm / 10;
        const PP = PP_mm / 10;
        const AE = AE_mm / 10;
        const Ao = Ao_mm / 10;

        // Volume Diastólico Final (mL)
        const VDF = (7 * Math.pow(DDVE, 3)) / (2.4 + DDVE);
        $("#volume_diastolico_final").val(VDF.toFixed(2));

        // Volume Sistólico Final (mL)
        const VSF = (7 * Math.pow(DSVE, 3)) / (2.4 + DSVE);
        $("#volume_sistolico_final").val(VSF.toFixed(2));

        // Volume Sistólico (mL)
        const VS = VDF - VSF;
        $("#volume_sistolico").val(VS.toFixed(2));

        // Fração de Ejeção (%)
        const FE = (VS / VDF) * 100;
        $("#fracao_ejecao_teichols").val(FE.toFixed(2));
        
        // Usar a mesma fórmula para a fração de ejeção final
        $("#fracao_ejecao").val(FE.toFixed(2));

        // Débito Cardíaco (L/min)
        const DC = (VS * FC) / 1000;
        $("#debito_cardiaco").val(DC.toFixed(2));

        // Índice Cardíaco (L/min/m²)
        const IC = DC / SC;
        $("#indice_cardiaco").val(IC.toFixed(2));

        // Massa Ventricular Esquerda (g)
        const MVE = 0.8 * (1.04 * (Math.pow((DDVE + SIV + PP), 3) - Math.pow(DDVE, 3))) + 0.6;
        $("#massa_ventricular_esquerda").val(MVE.toFixed(2));
        $("#massa_ve").val(MVE.toFixed(2));

        // Índice de Massa Ventricular Esquerda (g/m²)
        const IMVE = MVE / SC;
        $("#indice_massa_ventricular_esquerda").val(IMVE.toFixed(2));
        $("#indice_massa_ve").val(IMVE.toFixed(2));

        // Relação Volume/Massa
        const rel_VM = VDF / MVE;
        $("#relacao_volume_massa").val(rel_VM.toFixed(2));

        // Relação AE/Ao
        const rel_AE_Ao = AE / Ao;
        $("#relacao_atrio_esquerdo_aorta").val(rel_AE_Ao.toFixed(2));

        // % Encurtamento
        const encurtamento = ((DDVE - DSVE) / DDVE) * 100;
        $("#percentual_encurtamento").val(encurtamento.toFixed(2));

        // Relação Septo / PP
        const rel_SIV_PP = SIV / PP;
        $("#relacao_septo_parede_posterior").val(rel_SIV_PP.toFixed(2));

        // Gradientes (todos com fórmula ΔP = 4 × V²)
        const grad_VD_AP = 4 * Math.pow(vel_fluxo_pulm, 2);
        $("#gradiente_vd_ap").val(grad_VD_AP.toFixed(2));

        const grad_VE_Ao = 4 * Math.pow(vel_fluxo_ao, 2);
        $("#gradiente_ve_ao").val(grad_VE_Ao.toFixed(2));

        const grad_AE_VE = 4 * Math.pow(vel_fluxo_mitral, 2);
        $("#gradiente_ae_ve").val(grad_AE_VE.toFixed(2));

        const grad_AD_VD = 4 * Math.pow(vel_fluxo_tricuspide, 2);
        $("#gradiente_ad_vd").val(grad_AD_VD.toFixed(2));

        // PSAP
        const PSAP = 4 * Math.pow(vel_fluxo_tricuspide, 2) + pressao_AD;
        $("#psap").val(PSAP.toFixed(2));

        // Volume do átrio esquerdo (valor calculado em outro lugar ou inserido manualmente)
        // Mantemos o campo para entrada manual
    }

    // Eventos para recalcular quando qualquer campo for alterado
    $("input[type='number'], input[type='text']").on("input", function() {
        calcularParametrosEcocardiograficos();
    });

    // Calcular inicialmente se houver dados
    calcularParametrosEcocardiograficos();

    // Remover a propriedade readonly dos campos calculados para permitir edição manual
    $(".calculated-field").prop("readonly", false);

    // Salvar automaticamente os dados a cada 30 segundos
    setInterval(function() {
        if ($("#form-parametros").length) {
            salvarParametros(false);
        }
    }, 30000);

    // Função para salvar parâmetros
    function salvarParametros(mostrarNotificacao = true) {
        const formData = $("#form-parametros").serialize();
        const exameId = $("#exame_id").val();
        
        $.ajax({
            type: "POST",
            url: "/exame/" + exameId + "/salvar_parametros",
            data: formData,
            success: function(response) {
                console.log("Dados salvos com sucesso");
                if (mostrarNotificacao) {
                    $("#save-notification").text("Parâmetros salvos com sucesso!").fadeIn().delay(2000).fadeOut();
                }
            },
            error: function(error) {
                console.error("Erro ao salvar dados:", error);
                if (mostrarNotificacao) {
                    $("#save-notification").text("Erro ao salvar parâmetros. Tentando novamente...").fadeIn();
                    
                    // Tentar novamente após 2 segundos
                    setTimeout(function() {
                        salvarParametros(mostrarNotificacao);
                    }, 2000);
                }
            }
        });
    }

    // Botões para salvar parâmetros manualmente
    $("#btn-salvar-parametros, #btn-salvar-parametros-volumes, #btn-salvar-parametros-fluxos").click(function(e) {
        e.preventDefault();
        salvarParametros(true);
    });

    // Botão para avançar para o laudo após salvar
    $("#btn-avancar-laudo").click(function(e) {
        e.preventDefault();
        const exameId = $("#exame_id").val();
        
        // Primeiro salvar os parâmetros
        const formData = $("#form-parametros").serialize();
        
        $.ajax({
            type: "POST",
            url: "/exame/" + exameId + "/salvar_parametros",
            data: formData,
            success: function(response) {
                console.log("Parâmetros salvos com sucesso, redirecionando para laudo");
                // Redirecionar para a página de laudo
                window.location.href = "/exame/" + exameId + "/laudo";
            },
            error: function(error) {
                console.error("Erro ao salvar parâmetros:", error);
                $("#save-notification").text("Erro ao salvar parâmetros. Tente novamente.").fadeIn().delay(2000).fadeOut();
            }
        });
    });

    // Navegação entre abas
    $(".tab-button").click(function() {
        const tabId = $(this).data("tab");
        
        // Remover classe active de todas as abas e botões
        $(".tab-pane").removeClass("active");
        $(".tab-button").removeClass("active");
        
        // Adicionar classe active à aba e botão clicados
        $("#" + tabId).addClass("active");
        $(this).addClass("active");
    });

    // Navegação entre abas via botões "Próximo" e "Anterior"
    $(".next-tab").click(function() {
        const nextTabId = $(this).data("next");
        $(".tab-pane").removeClass("active");
        $(".tab-button").removeClass("active");
        $("#" + nextTabId).addClass("active");
        $(".tab-button[data-tab='" + nextTabId + "']").addClass("active");
        
        // Salvar automaticamente ao mudar de aba
        salvarParametros(true);
    });
    
    $(".prev-tab").click(function() {
        const prevTabId = $(this).data("prev");
        $(".tab-pane").removeClass("active");
        $(".tab-button").removeClass("active");
        $("#" + prevTabId).addClass("active");
        $(".tab-button[data-tab='" + prevTabId + "']").addClass("active");
        
        // Salvar automaticamente ao mudar de aba
        salvarParametros(true);
    });
});
