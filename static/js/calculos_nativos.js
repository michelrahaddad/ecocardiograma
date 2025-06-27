/**
 * Sistema de Cálculos Automáticos - JavaScript Nativo
 * Substituição completa do jQuery para cálculos de ecocardiograma
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando cálculos...');
    initializeNativeCalculations();
});

function initializeNativeCalculations() {
    console.log('Inicializando cálculos com JavaScript nativo...');
    
    // Configurar listeners nativos
    setupNativeListeners();
    
    // Executar cálculos iniciais
    setTimeout(function() {
        executeAllCalculations();
        console.log('Cálculos iniciais executados');
    }, 500);
}

function setupNativeListeners() {
    console.log('Configurando listeners nativos...');
    
    // Superfície corporal
    const peso = document.getElementById('peso');
    const altura = document.getElementById('altura');
    if (peso) peso.addEventListener('input', calculateBodySurface);
    if (altura) altura.addEventListener('input', calculateBodySurface);
    
    // Relação AE/Ao
    const ae = document.getElementById('atrio_esquerdo');
    const ao = document.getElementById('raiz_aorta');
    if (ae) ae.addEventListener('input', calculateAtrioAortaRatio);
    if (ao) ao.addEventListener('input', calculateAtrioAortaRatio);
    
    // Percentual de encurtamento
    const ddve = document.getElementById('diametro_diastolico_final_ve');
    const dsve = document.getElementById('diametro_sistolico_final');
    if (ddve) {
        ddve.addEventListener('input', function() {
            calculateShortening();
            calculateDiastolicVolumeTeichholz();
            calculateLeftVentricularMass();
        });
    }
    if (dsve) {
        dsve.addEventListener('input', function() {
            calculateShortening();
            calculateSystolicVolumeTeichholz();
        });
    }
    
    // Relação septo/parede posterior
    const septo = document.getElementById('espessura_diastolica_septo');
    const pp = document.getElementById('espessura_diastolica_ppve');
    if (septo) {
        septo.addEventListener('input', function() {
            calculateSeptumWallRatio();
            calculateLeftVentricularMass();
        });
    }
    if (pp) {
        pp.addEventListener('input', function() {
            calculateSeptumWallRatio();
            calculateLeftVentricularMass();
        });
    }
    
    // Gradientes
    const fluxoPulmonar = document.getElementById('fluxo_pulmonar');
    const fluxoAortico = document.getElementById('fluxo_aortico');
    const fluxoMitral = document.getElementById('fluxo_mitral');
    const fluxoTricuspide = document.getElementById('fluxo_tricuspide');
    
    if (fluxoPulmonar) fluxoPulmonar.addEventListener('input', calculateGradientVDAP);
    if (fluxoAortico) fluxoAortico.addEventListener('input', calculateGradientVEAO);
    if (fluxoMitral) fluxoMitral.addEventListener('input', calculateGradientAEVE);
    if (fluxoTricuspide) {
        fluxoTricuspide.addEventListener('input', function() {
            calculateGradientADVD();
            calculatePSAP();
        });
    }
    
    console.log('Listeners nativos configurados');
}

function executeAllCalculations() {
    console.log('Executando todos os cálculos...');
    
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
    calculatePSAP();
    
    console.log('Todos os cálculos executados');
}

function calculateBodySurface() {
    const peso = parseFloat(getValue('peso'));
    const altura = parseFloat(getValue('altura'));
    
    if (peso && altura && peso > 0 && altura > 0) {
        // Fórmula de DuBois: BSA = 0.007184 × altura^0.725 × peso^0.425
        const bsa = 0.007184 * Math.pow(altura, 0.725) * Math.pow(peso, 0.425);
        setValue('superficie_corporal', bsa.toFixed(2));
        console.log(`Superfície Corporal: ${bsa.toFixed(2)} m²`);
        
        // Recalcular índice de massa VE
        calculateLeftVentricularMassIndex();
    }
}

function calculateAtrioAortaRatio() {
    const ae = parseFloat(getValue('atrio_esquerdo'));
    const ao = parseFloat(getValue('raiz_aorta'));
    
    if (ae && ao && ao > 0) {
        const ratio = ae / ao;
        setValue('relacao_atrio_esquerdo_aorta', ratio.toFixed(2));
        console.log(`Relação AE/Ao: ${ratio.toFixed(2)}`);
    }
}

function calculateShortening() {
    const ddve = parseFloat(getValue('diametro_diastolico_final_ve'));
    const dsve = parseFloat(getValue('diametro_sistolico_final'));
    
    if (ddve && dsve && ddve > 0) {
        const shortening = ((ddve - dsve) / ddve) * 100;
        setValue('percentual_encurtamento', shortening.toFixed(1));
        console.log(`% Encurtamento: ${shortening.toFixed(1)}%`);
    }
}

function calculateSeptumWallRatio() {
    const septo = parseFloat(getValue('espessura_diastolica_septo'));
    const pp = parseFloat(getValue('espessura_diastolica_ppve'));
    
    if (septo && pp && pp > 0) {
        const ratio = septo / pp;
        setValue('relacao_septo_parede_posterior', ratio.toFixed(2));
        console.log(`Relação Septo/PP: ${ratio.toFixed(2)}`);
    }
}

function calculateDiastolicVolumeTeichholz() {
    const ddve = parseFloat(getValue('diametro_diastolico_final_ve'));
    
    if (ddve && ddve > 0) {
        // Converter de mm para cm
        const ddveCm = ddve / 10;
        // VDF = (7 × (DDVE)³) / (2.4 + DDVE)
        const vdf = (7 * Math.pow(ddveCm, 3)) / (2.4 + ddveCm);
        setValue('volume_diastolico_final', vdf.toFixed(1));
        console.log(`VDF (Teichholz): ${vdf.toFixed(1)} mL`);
        
        // Recalcular dependentes
        calculateEjectionVolume();
        calculateEjectionFraction();
    }
}

function calculateSystolicVolumeTeichholz() {
    const dsve = parseFloat(getValue('diametro_sistolico_final'));
    
    if (dsve && dsve > 0) {
        // Converter de mm para cm
        const dsveCm = dsve / 10;
        // VSF = (7 × (DSVE)³) / (2.4 + DSVE)
        const vsf = (7 * Math.pow(dsveCm, 3)) / (2.4 + dsveCm);
        setValue('volume_sistolico_final', vsf.toFixed(1));
        console.log(`VSF (Teichholz): ${vsf.toFixed(1)} mL`);
        
        // Recalcular dependentes
        calculateEjectionVolume();
        calculateEjectionFraction();
    }
}

function calculateEjectionVolume() {
    const vdf = parseFloat(getValue('volume_diastolico_final'));
    const vsf = parseFloat(getValue('volume_sistolico_final'));
    
    if (vdf && vsf) {
        const ve = vdf - vsf;
        setValue('volume_ejecao', ve.toFixed(1));
        console.log(`Volume Ejeção: ${ve.toFixed(1)} mL, FE: ${((ve/vdf)*100).toFixed(1)}%`);
    }
}

function calculateEjectionFraction() {
    const vdf = parseFloat(getValue('volume_diastolico_final'));
    const vsf = parseFloat(getValue('volume_sistolico_final'));
    
    if (vdf && vsf && vdf > 0) {
        const fe = ((vdf - vsf) / vdf) * 100;
        setValue('fracao_ejecao', fe.toFixed(1));
    }
}

function calculateLeftVentricularMass() {
    const ddve = parseFloat(getValue('diametro_diastolico_final_ve'));
    const septo = parseFloat(getValue('espessura_diastolica_septo'));
    const pp = parseFloat(getValue('espessura_diastolica_ppve'));
    
    if (ddve && septo && pp) {
        // Converter de mm para cm
        const ddveCm = ddve / 10;
        const septoCm = septo / 10;
        const ppCm = pp / 10;
        
        // Fórmula ASE corrigida
        const soma = ddveCm + septoCm + ppCm;
        const massa = 0.8 * (1.04 * (Math.pow(soma, 3) - Math.pow(ddveCm, 3))) + 0.6;
        
        setValue('massa_ve', massa.toFixed(1));
        console.log(`Massa VE: ${massa.toFixed(1)} g`);
        
        calculateLeftVentricularMassIndex();
    }
}

function calculateLeftVentricularMassIndex() {
    const massa = parseFloat(getValue('massa_ve'));
    const bsa = parseFloat(getValue('superficie_corporal'));
    
    if (massa && bsa && bsa > 0) {
        const indice = massa / bsa;
        setValue('indice_massa_ve', indice.toFixed(1));
        console.log(`Índice Massa VE: ${indice.toFixed(1)} g/m²`);
    }
}

function calculateGradientVDAP() {
    const velocidade = parseFloat(getValue('fluxo_pulmonar'));
    
    if (velocidade && velocidade > 0) {
        const gradiente = 4 * Math.pow(velocidade, 2);
        setValue('gradiente_vd_ap', gradiente.toFixed(1));
        console.log(`Gradiente VD→AP: ${gradiente.toFixed(1)} mmHg`);
    }
}

function calculateGradientVEAO() {
    const velocidade = parseFloat(getValue('fluxo_aortico'));
    
    if (velocidade && velocidade > 0) {
        const gradiente = 4 * Math.pow(velocidade, 2);
        setValue('gradiente_ve_ao', gradiente.toFixed(1));
        console.log(`Gradiente VE→AO: ${gradiente.toFixed(1)} mmHg`);
    }
}

function calculateGradientAEVE() {
    const velocidade = parseFloat(getValue('fluxo_mitral'));
    
    if (velocidade && velocidade > 0) {
        const gradiente = 4 * Math.pow(velocidade, 2);
        setValue('gradiente_ae_ve', gradiente.toFixed(1));
        console.log(`Gradiente AE→VE: ${gradiente.toFixed(1)} mmHg`);
    }
}

function calculateGradientADVD() {
    const velocidade = parseFloat(getValue('fluxo_tricuspide'));
    
    if (velocidade && velocidade > 0) {
        const gradiente = 4 * Math.pow(velocidade, 2);
        setValue('gradiente_ad_vd', gradiente.toFixed(1));
        console.log(`Gradiente AD→VD/IT: ${gradiente.toFixed(1)} mmHg`);
    }
}

function calculatePSAP() {
    const gradienteTricuspide = parseFloat(getValue('gradiente_tricuspide'));
    
    if (gradienteTricuspide && gradienteTricuspide > 0) {
        // PSAP = Gradiente tricúspide + PVC estimada (10 mmHg)
        const psap = gradienteTricuspide + 10;
        setValue('pressao_sistolica_vd', psap.toFixed(1));
        console.log(`PSAP: ${psap.toFixed(1)} mmHg`);
    } else {
        // Calcular a partir do fluxo tricúspide se disponível
        const fluxoTricuspide = parseFloat(getValue('fluxo_tricuspide'));
        if (fluxoTricuspide && fluxoTricuspide > 0) {
            const gradiente = 4 * Math.pow(fluxoTricuspide, 2);
            const psap = gradiente + 10;
            setValue('pressao_sistolica_vd', psap.toFixed(1));
            console.log(`PSAP: ${psap.toFixed(1)} mmHg`);
        }
    }
}

// Funções auxiliares
function getValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : '';
}

function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
        // Destacar campo calculado
        highlightField(element);
    }
}

function highlightField(element) {
    if (element) {
        element.style.backgroundColor = '#e3f2fd';
        element.style.borderColor = '#2196f3';
        setTimeout(function() {
            element.style.backgroundColor = '';
            element.style.borderColor = '';
        }, 2000);
    }
}

// Fallback para quando jQuery não está disponível
if (typeof $ === 'undefined') {
    console.log('jQuery não disponível, usando apenas JavaScript nativo');
}