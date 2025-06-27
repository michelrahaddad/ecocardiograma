/**
 * Sistema de Ecocardiograma - Grupo Vidah
 * JavaScript para Cálculos de Parâmetros Ecocardiográficos
 */

$(document).ready(function() {
    initializeParameterCalculations();
    setupFormValidation();
    setupAutoSave();
    calculateInitialValues();
});

function initializeParameterCalculations() {
    // Campos que participam de cálculos automáticos
    const calculatedFields = {
        'superficie_corporal': calculateBodySurface,
        'relacao_atrio_esquerdo_aorta': calculateAtrioAortaRatio,
        'percentual_encurtamento': calculateShortening,
        'relacao_septo_parede_posterior': calculateSeptumWallRatio,
        'volume_diastolico_final': calculateDiastolicVolumeTeichholz,
        'volume_sistolico_final': calculateSystolicVolumeTeichholz,
        'volume_ejecao': calculateEjectionVolume,
        'fracao_ejecao': calculateEjectionFraction,
        'massa_ve': calculateLeftVentricularMass,
        'indice_massa_ve': calculateLeftVentricularMassIndex,
        'gradiente_vd_ap': calculateGradientVDAP,
        'gradiente_ve_ao': calculateGradientVEAO,
        'gradiente_ae_ve': calculateGradientAEVE,
        'gradiente_ad_vd': calculateGradientADVD,
        'pressao_sistolica_vd': calculatePSAP
    };

    // Adicionar listeners para campos que afetam cálculos
    setupCalculationListeners(calculatedFields);
    
    // Adicionar validação em tempo real
    setupRealTimeValidation();
    
    // Configurar tooltips para valores de referência
    setupReferenceTooltips();
}

function calculateInitialValues() {
    // Calcular valores que já podem ter dados preenchidos
    setTimeout(function() {
        calculateBodySurface();
        calculateAtrioAortaRatio();
        calculateShortening();
        calculateSeptumWallRatio();
        calculateDiastolicVolumeTeichholz();
        calculateSystolicVolumeTeichholz();
        calculateLeftVentricularMass();
        calculateGradientVDAP();
        calculateGradientVEAO();
        calculateGradientAEVE();
        calculateGradientADVD();
    }, 100);
}

function setupRealTimeValidation() {
    // Validação em tempo real para campos importantes
    $('input[type="number"]').on('input change', function() {
        const field = $(this);
        const value = parseFloat(field.val());
        
        if (!isNaN(value) && value > 0) {
            // Trigger calculations based on field
            const fieldId = field.attr('id');
            triggerDependentCalculations(fieldId);
        }
    });
}

function triggerDependentCalculations(fieldId) {
    // Recalcular automaticamente valores dependentes
    switch(fieldId) {
        case 'peso':
        case 'altura':
            calculateBodySurface();
            calculateLeftVentricularMassIndex();
            break;
            
        case 'atrio_esquerdo':
        case 'raiz_aorta':
            calculateAtrioAortaRatio();
            break;
            
        case 'diametro_diastolico_final_ve':
        case 'diametro_sistolico_final':
            calculateShortening();
            calculateDiastolicVolumeTeichholz();
            calculateSystolicVolumeTeichholz();
            calculateEjectionVolume();
            calculateEjectionFraction();
            calculateLeftVentricularMass();
            calculateLeftVentricularMassIndex();
            break;
            
        case 'espessura_diastolica_septo':
        case 'espessura_diastolica_ppve':
            calculateSeptumWallRatio();
            calculateLeftVentricularMass();
            calculateLeftVentricularMassIndex();
            break;
            
        case 'fluxo_pulmonar':
            calculateGradientVDAP();
            break;
            
        case 'fluxo_aortico':
            calculateGradientVEAO();
            break;
            
        case 'fluxo_mitral':
            calculateGradientAEVE();
            break;
            
        case 'fluxo_tricuspide':
            calculateGradientADVD();
            calculatePSAP();
            break;
            
        case 'gradiente_tricuspide':
            calculatePSAP();
            break;
    }
}

function setupReferenceTooltips() {
    // Adicionar tooltips para valores de referência
    $('.reference-value').each(function() {
        $(this).attr('title', 'Valores de referência normais');
    });
}

function setupFormValidation() {
    // Validação básica do formulário
    $('#parametros-form').on('submit', function(e) {
        const requiredFields = $('input[required]');
        let valid = true;
        
        requiredFields.each(function() {
            if (!$(this).val()) {
                valid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!valid) {
            e.preventDefault();
            alert('Por favor, preencha todos os campos obrigatórios.');
        }
    });
}

function setupAutoSave() {
    // Auto-save a cada 30 segundos
    setInterval(function() {
        if ($('#parametros-form').length > 0) {
            // Salvar automaticamente se houver mudanças
            saveParameters();
        }
    }, 30000);
}

function triggerDependentCalculations(fieldId) {
    // Trigger cálculos dependentes baseados no campo alterado
    switch(fieldId) {
        case 'peso':
        case 'altura':
            calculateBodySurface();
            break;
        case 'atrio_esquerdo':
        case 'raiz_aorta':
            calculateAtrioAortaRatio();
            break;
        case 'diametro_diastolico_final_ve':
            calculateShortening();
            calculateDiastolicVolumeTeichholz();
            calculateLeftVentricularMass();
            break;
        case 'diametro_sistolico_final':
            calculateShortening();
            calculateSystolicVolumeTeichholz();
            break;
        case 'espessura_diastolica_septo':
        case 'espessura_diastolica_ppve':
            calculateSeptumWallRatio();
            calculateLeftVentricularMass();
            break;
        case 'fluxo_pulmonar':
            calculateGradientVDAP();
            break;
        case 'fluxo_aortico':
            calculateGradientVEAO();
            break;
        case 'fluxo_mitral':
            calculateGradientAEVE();
            break;
        case 'fluxo_tricuspide':
            calculateGradientADVD();
            break;
    }
}

function saveParameters() {
    // Função de salvamento automático
    const formData = $('#parametros-form').serialize();
    if (formData) {
        console.log('Auto-saving parameters...');
        // Implementar salvamento via AJAX se necessário
    }
}

function setupCalculationListeners(calculatedFields) {
    // Listeners para cálculo de superfície corporal
    $('#peso, #altura').on('input blur', function() {
        calculateBodySurface();
    });

    // Listeners para relação AE/Ao
    $('#atrio_esquerdo, #raiz_aorta').on('input blur', function() {
        calculateAtrioAortaRatio();
    });

    // Listeners para % de encurtamento
    $('#diametro_diastolico_final_ve, #diametro_sistolico_final').on('input blur', function() {
        calculateShortening();
    });

    // Listeners para relação septo/parede posterior
    $('#espessura_diastolica_septo, #espessura_diastolica_ppve').on('input blur', function() {
        calculateSeptumWallRatio();
    });

    // Listeners para cálculos de Teichholz - volumes automáticos
    $('#diametro_diastolico_final_ve').on('input blur', function() {
        calculateDiastolicVolumeTeichholz();
    });
    
    $('#diametro_sistolico_final').on('input blur', function() {
        calculateSystolicVolumeTeichholz();
    });

    // Listeners para volumes e fração de ejeção
    $('#volume_diastolico_final, #volume_sistolico_final').on('input blur', function() {
        calculateEjectionVolume();
        calculateEjectionFraction();
    });

    // Listeners para massa do VE (fórmula ASE)
    $('#diametro_diastolico_final_ve, #espessura_diastolica_septo, #espessura_diastolica_ppve').on('input blur', function() {
        calculateLeftVentricularMass();
    });

    // Listeners para índice de massa VE
    $('#massa_ve, #superficie_corporal').on('input blur', function() {
        calculateLeftVentricularMassIndex();
    });

    // Listeners para gradientes automáticos baseados nas velocidades
    $('#fluxo_pulmonar').on('input blur', function() {
        calculateGradientVDAP();
    });
    
    $('#fluxo_aortico').on('input blur', function() {
        calculateGradientVEAO();
    });
    
    $('#fluxo_mitral').on('input blur', function() {
        calculateGradientAEVE();
    });
    
    $('#fluxo_tricuspide').on('input blur', function() {
        calculateGradientADVD();
    });

    // Listeners para PSAP
    $('#gradiente_tricuspide').on('input blur', function() {
        calculatePSAP();
    });
}

function calculateBodySurface() {
    const peso = parseFloat($('#peso').val());
    const altura = parseFloat($('#altura').val());
    
    if (peso && altura && peso > 0 && altura > 0) {
        // Fórmula de DuBois: BSA = 0.007184 × altura^0.725 × peso^0.425
        const bsa = 0.007184 * Math.pow(altura, 0.725) * Math.pow(peso, 0.425);
        $('#superficie_corporal').val(bsa.toFixed(2));
        
        // Recalcular índice de massa VE se massa estiver preenchida
        calculateLeftVentricularMassIndex();
        
        // Highlighting do campo atualizado
        highlightCalculatedField('#superficie_corporal');
    }
}

function calculateAtrioAortaRatio() {
    const ae = parseFloat($('#atrio_esquerdo').val());
    const ao = parseFloat($('#raiz_aorta').val());
    
    if (ae && ao && ao > 0) {
        const ratio = ae / ao;
        $('#relacao_atrio_esquerdo_aorta').val(ratio.toFixed(2));
        
        // Verificar se está normal (< 1.5)
        validateReferenceRange('#relacao_atrio_esquerdo_aorta', ratio, null, 1.5);
        highlightCalculatedField('#relacao_atrio_esquerdo_aorta');
    }
}

function calculateShortening() {
    const ddve = parseFloat($('#diametro_diastolico_final_ve').val());
    const dsve = parseFloat($('#diametro_sistolico_final').val());
    
    if (ddve && dsve && ddve > 0) {
        const shortening = ((ddve - dsve) / ddve) * 100;
        $('#percentual_encurtamento').val(shortening.toFixed(1));
        
        // Aceitar qualquer valor válido - sem restrições
        highlightCalculatedField('#percentual_encurtamento');
    }
}

function calculateSeptumWallRatio() {
    const septo = parseFloat($('#espessura_diastolica_septo').val());
    const pp = parseFloat($('#espessura_diastolica_ppve').val());
    
    if (septo && pp && pp > 0) {
        const ratio = septo / pp;
        $('#relacao_septo_parede_posterior').val(ratio.toFixed(2));
        
        // Aceitar qualquer valor válido - sem restrições
        highlightCalculatedField('#relacao_septo_parede_posterior');
    }
}

// Método de Teichholz para Volume Diastólico Final (VDF)
function calculateDiastolicVolumeTeichholz() {
    const ddve = parseFloat($('#diametro_diastolico_final_ve').val());
    
    if (ddve && ddve > 0) {
        // Converter de mm para cm para a fórmula
        const ddveCm = ddve / 10;
        // VDF = (7 × (DDVE)³) / (2.4 + DDVE)
        const vdf = (7 * Math.pow(ddveCm, 3)) / (2.4 + ddveCm);
        $('#volume_diastolico_final').val(vdf.toFixed(1));
        
        // Aceitar qualquer valor válido - sem restrições
        highlightCalculatedField('#volume_diastolico_final');
        
        // Recalcular dependentes
        calculateEjectionVolume();
        calculateEjectionFraction();
    }
}

// Método de Teichholz para Volume Sistólico Final (VSF)
function calculateSystolicVolumeTeichholz() {
    const dsve = parseFloat($('#diametro_sistolico_final').val());
    
    if (dsve && dsve > 0) {
        // Converter de mm para cm para a fórmula
        const dsveCm = dsve / 10;
        // VSF = (7 × (DSVE)³) / (2.4 + DSVE)
        const vsf = (7 * Math.pow(dsveCm, 3)) / (2.4 + dsveCm);
        $('#volume_sistolico_final').val(vsf.toFixed(1));
        
        // Aceitar qualquer valor válido - sem restrições
        highlightCalculatedField('#volume_sistolico_final');
        
        // Recalcular dependentes
        calculateEjectionVolume();
        calculateEjectionFraction();
    }
}

function calculateEjectionVolume() {
    const vdf = parseFloat($('#volume_diastolico_final').val());
    const vsf = parseFloat($('#volume_sistolico_final').val());
    
    if (vdf && vsf) {
        const ve = vdf - vsf;
        $('#volume_ejecao').val(ve.toFixed(1));
        highlightCalculatedField('#volume_ejecao');
    }
}

function calculateEjectionFraction() {
    const vdf = parseFloat($('#volume_diastolico_final').val());
    const vsf = parseFloat($('#volume_sistolico_final').val());
    
    if (vdf && vsf && vdf > 0) {
        const fe = ((vdf - vsf) / vdf) * 100;
        $('#fracao_ejecao').val(fe.toFixed(1));
        
        // Verificar se está normal (≥ 55%)
        validateReferenceRange('#fracao_ejecao', fe, 55, null);
        highlightCalculatedField('#fracao_ejecao');
    }
}

// Massa do VE usando fórmula ASE corrigida
function calculateLeftVentricularMass() {
    const ddve = parseFloat($('#diametro_diastolico_final_ve').val());
    const septo = parseFloat($('#espessura_diastolica_septo').val());
    const pp = parseFloat($('#espessura_diastolica_ppve').val());
    
    if (ddve && septo && pp) {
        // IMPORTANTE: Converter de mm para cm para a fórmula ASE
        const ddveCm = ddve / 10;  // mm → cm
        const septoCm = septo / 10;  // mm → cm
        const ppCm = pp / 10;  // mm → cm
        
        // Fórmula ASE corrigida: Massa VE = 0.8 × [1.04 × ((DDVE + Septo + PP)³ - (DDVE)³)] + 0.6
        // Todos os valores em cm conforme especificação
        const soma = ddveCm + septoCm + ppCm;
        const massa = 0.8 * (1.04 * (Math.pow(soma, 3) - Math.pow(ddveCm, 3))) + 0.6;
        
        $('#massa_ve').val(massa.toFixed(1));
        highlightCalculatedField('#massa_ve');
        
        // Recalcular índice de massa
        calculateLeftVentricularMassIndex();
    }
}

function calculateLeftVentricularMassIndex() {
    const massa = parseFloat($('#massa_ve').val());
    const bsa = parseFloat($('#superficie_corporal').val());
    
    if (massa && bsa && bsa > 0) {
        const indice = massa / bsa;
        $('#indice_massa_ve').val(indice.toFixed(1));
        
        // Valores de referência dependem do sexo
        // Para simplificar, usar valor médio (H: ≤115, M: ≤95)
        const limite = 105; // Valor médio aproximado
        validateReferenceRange('#indice_massa_ve', indice, null, limite);
        highlightCalculatedField('#indice_massa_ve');
    }
}

// Cálculo de gradientes usando equação de Bernoulli modificada
function calculateGradientVDAP() {
    const velocidade = parseFloat($('#fluxo_pulmonar').val());
    
    if (velocidade && velocidade > 0) {
        // Gradiente = 4 × (Velocidade)²
        const gradiente = 4 * Math.pow(velocidade, 2);
        $('#gradiente_vd_ap').val(gradiente.toFixed(1));
        
        validateReferenceRange('#gradiente_vd_ap', gradiente, null, 10);
        highlightCalculatedField('#gradiente_vd_ap');
    }
}

function calculateGradientVEAO() {
    const velocidade = parseFloat($('#fluxo_aortico').val());
    
    if (velocidade && velocidade > 0) {
        // Gradiente = 4 × (Velocidade Aórtica)²
        const gradiente = 4 * Math.pow(velocidade, 2);
        $('#gradiente_ve_ao').val(gradiente.toFixed(1));
        
        validateReferenceRange('#gradiente_ve_ao', gradiente, null, 10);
        highlightCalculatedField('#gradiente_ve_ao');
    }
}

function calculateGradientAEVE() {
    const velocidade = parseFloat($('#fluxo_mitral').val());
    
    if (velocidade && velocidade > 0) {
        // Gradiente = 4 × (Velocidade Mitral)²
        const gradiente = 4 * Math.pow(velocidade, 2);
        $('#gradiente_ae_ve').val(gradiente.toFixed(1));
        
        validateReferenceRange('#gradiente_ae_ve', gradiente, null, 5);
        highlightCalculatedField('#gradiente_ae_ve');
    }
}

function calculateGradientADVD() {
    const velocidade = parseFloat($('#fluxo_tricuspide').val());
    
    if (velocidade && velocidade > 0) {
        // Gradiente = 4 × (Velocidade Tricúspide)²
        const gradiente = 4 * Math.pow(velocidade, 2);
        $('#gradiente_ad_vd').val(gradiente.toFixed(1));
        $('#gradiente_tricuspide').val(gradiente.toFixed(1)); // Mesmo valor para IT
        
        validateReferenceRange('#gradiente_ad_vd', gradiente, null, 5);
        highlightCalculatedField('#gradiente_ad_vd');
        highlightCalculatedField('#gradiente_tricuspide');
        
        // Recalcular PSAP
        calculatePSAP();
    }
}

// Função removida conforme padronização médica

// Função removida conforme padronização médica

// Cálculo da PSAP com estimativa de PVC
function calculatePSAP() {
    const gradienteIT = parseFloat($('#gradiente_tricuspide').val());
    
    if (gradienteIT) {
        // Estimar PVC (Pressão Venosa Central)
        // Como não temos dados da VCI, usar valor padrão de 10 mmHg
        const pvc = 10; // mmHg (valor intermediário padrão)
        
        // PSAP = Gradiente IT + PVC
        const psap = gradienteIT + pvc;
        $('#pressao_sistolica_vd').val(psap.toFixed(1));
        
        // Verificar se está normal (< 35 mmHg)
        validateReferenceRange('#pressao_sistolica_vd', psap, null, 35);
        highlightCalculatedField('#pressao_sistolica_vd');
    }
}

function calculateRightVentricularPressure() {
    // Função mantida para compatibilidade
    calculatePSAP();
}

function validateReferenceRange(fieldId, value, min, max) {
    const field = $(fieldId);
    
    // Remover classes anteriores
    field.removeClass('normal-value abnormal-value');
    
    let isNormal = true;
    
    if (min !== null && value < min) {
        isNormal = false;
    }
    
    if (max !== null && value > max) {
        isNormal = false;
    }
    
    // Aplicar classe apropriada
    if (isNormal) {
        field.addClass('normal-value');
    } else {
        field.addClass('abnormal-value');
    }
    
    // Atualizar tooltip com informação
    updateFieldTooltip(fieldId, value, min, max, isNormal);
}

function updateFieldTooltip(fieldId, value, min, max, isNormal) {
    const field = $(fieldId);
    let tooltipText = '';
    
    if (min !== null && max !== null) {
        tooltipText = `Valor: ${value} (Normal: ${min}-${max})`;
    } else if (min !== null) {
        tooltipText = `Valor: ${value} (Normal: ≥${min})`;
    } else if (max !== null) {
        tooltipText = `Valor: ${value} (Normal: ≤${max})`;
    }
    
    if (!isNormal) {
        tooltipText += ' - FORA DOS LIMITES NORMAIS';
    }
    
    field.attr('title', tooltipText);
}

function highlightCalculatedField(fieldId) {
    const field = $(fieldId);
    
    // Efeito visual temporário para indicar que o campo foi calculado
    field.addClass('calculated-highlight');
    
    setTimeout(() => {
        field.removeClass('calculated-highlight');
    }, 2000);
}

function setupRealTimeValidation() {
    // Validação de campos numéricos
    $('input[type="number"]').on('input', function() {
        const value = parseFloat($(this).val());
        const min = parseFloat($(this).attr('min'));
        const max = parseFloat($(this).attr('max'));
        
        if (value < min || value > max) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    // Validação de campos obrigatórios
    $('input[required], select[required]').on('blur', function() {
        if (!$(this).val()) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
}

function setupReferenceTooltips() {
    // Configurar tooltips para todos os campos com valores de referência
    const referenceRanges = {
        'frequencia_cardiaca': '60-100 bpm',
        'atrio_esquerdo': '2,7-3,8 cm',
        'raiz_aorta': '2,1-3,4 cm',
        'relacao_atrio_esquerdo_aorta': '<1,5',
        'aorta_ascendente': '<3,8 cm',
        'diametro_ventricular_direito': '0,7-2,3 cm',
        'diametro_basal_vd': '2,5-4,1 cm',
        'diametro_diastolico_final_ve': '3,5-5,6 cm',
        'diametro_sistolico_final': '2,1-4,0 cm',
        'percentual_encurtamento': '25-45%',
        'espessura_diastolica_septo': '0,6-1,1 cm',
        'espessura_diastolica_ppve': '0,6-1,1 cm',
        'relacao_septo_parede_posterior': '<1,3',
        'volume_diastolico_final': '67-155 mL',
        'volume_sistolico_final': '22-58 mL',
        'fracao_ejecao': '≥55%',
        'relacao_e_a': '0,8-1,5',
        'tempo_desaceleracao_e': '150-220 ms',
        'relacao_e_e_linha': '<14',
        'pressao_sistolica_vd': '<35 mmHg'
    };
    
    Object.keys(referenceRanges).forEach(fieldId => {
        const field = $('#' + fieldId);
        if (field.length) {
            field.attr('title', 'Valor de referência: ' + referenceRanges[fieldId]);
            field.tooltip();
        }
    });
}

function setupAutoSave() {
    let autoSaveTimer;
    
    // Auto-save a cada 30 segundos quando há alterações
    $('input, select, textarea').on('input change', function() {
        clearTimeout(autoSaveTimer);
        
        autoSaveTimer = setTimeout(() => {
            saveParametersAjax();
        }, 30000);
    });
}

function saveParametersAjax() {
    const formData = $('#parametros-form').serialize();
    
    $.ajax({
        url: window.location.href,
        method: 'POST',
        data: formData,
        success: function(response) {
            showAutoSaveIndicator('success');
        },
        error: function() {
            showAutoSaveIndicator('error');
        }
    });
}

function showAutoSaveIndicator(type) {
    const indicator = $('<div class="auto-save-indicator"></div>');
    
    if (type === 'success') {
        indicator.html('<i class="fas fa-check-circle text-success"></i> Salvo automaticamente');
    } else {
        indicator.html('<i class="fas fa-exclamation-triangle text-warning"></i> Erro no salvamento automático');
    }
    
    indicator.css({
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: 'white',
        padding: '10px 15px',
        borderRadius: '5px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        zIndex: 9999
    });
    
    $('body').append(indicator);
    
    setTimeout(() => {
        indicator.fadeOut(() => {
            indicator.remove();
        });
    }, 3000);
}

function setupFormValidation() {
    $('#parametros-form').on('submit', function(e) {
        let isValid = true;
        
        // Validar campos numéricos críticos
        const criticalFields = [
            'frequencia_cardiaca',
            'diametro_diastolico_final_ve',
            'diametro_sistolico_final',
            'fracao_ejecao'
        ];
        
        criticalFields.forEach(fieldId => {
            const field = $('#' + fieldId);
            const value = parseFloat(field.val());
            
            if (!value || value <= 0) {
                field.addClass('is-invalid');
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Por favor, verifique os campos obrigatórios e valores inválidos antes de continuar.');
            
            // Scroll para o primeiro campo inválido
            $('html, body').animate({
                scrollTop: $('.is-invalid').first().offset().top - 100
            }, 500);
        }
    });
}

function calculateInitialValues() {
    // Calcular valores iniciais se os campos já estiverem preenchidos
    setTimeout(function() {
        calculateBodySurface();
        calculateAtrioAortaRatio();
        calculateShortening();
        calculateSeptumWallRatio();
        calculateDiastolicVolumeTeichholz();
        calculateSystolicVolumeTeichholz();
        calculateEjectionVolume();
        calculateEjectionFraction();
        calculateLeftVentricularMass();
        calculateLeftVentricularMassIndex();
        calculateGradientVDAP();
        calculateGradientVEAO();
        calculateGradientAEVE();
        calculateGradientADVD();
        calculatePSAP();
    }, 100);
}

// Utility functions
function formatNumber(value, decimals = 2) {
    return parseFloat(value).toFixed(decimals);
}

function isValidNumber(value) {
    return !isNaN(value) && isFinite(value) && value !== null;
}

// CSS para highlight temporário
$(document).ready(function() {
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .calculated-highlight {
                background-color: #fff3cd !important;
                border-color: #ffc107 !important;
                transition: all 0.3s ease;
            }
            
            .normal-value {
                border-left: 3px solid #28a745 !important;
            }
            
            .abnormal-value {
                border-left: 3px solid #dc3545 !important;
                background-color: #f8d7da !important;
            }
            
            .auto-save-indicator {
                animation: slideInRight 0.3s ease-out;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `)
        .appendTo('head');
});

// Export functions for external use
window.EcoParametros = {
    calculateBodySurface,
    calculateAtrioAortaRatio,
    calculateShortening,
    calculateEjectionFraction,
    validateReferenceRange,
    saveParametersAjax
};
