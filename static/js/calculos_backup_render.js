/**
 * SISTEMA DE CÁLCULOS BACKUP PARA RENDER
 * Versão simplificada e robusta para ambientes restritivos
 */

// Aguardar carregamento completo
(function() {
    'use strict';
    
    console.log('🆘 BACKUP: Sistema de cálculos backup carregando...');
    
    // Esperar DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarBackup);
    } else {
        inicializarBackup();
    }
    
    function inicializarBackup() {
        console.log('🆘 BACKUP: Inicializando sistema backup');
        
        // Aguardar elementos estarem disponíveis
        setTimeout(function() {
            configurarListenersBackup();
            executarCalculosIniciais();
        }, 2000);
    }
    
    function configurarListenersBackup() {
        console.log('🆘 BACKUP: Configurando listeners');
        
        // Superfície corporal
        adicionarListener('peso', calcularSuperficieCorporal);
        adicionarListener('altura', calcularSuperficieCorporal);
        
        // Relação AE/Ao
        adicionarListener('atrio_esquerdo', calcularRelacaoAEAo);
        adicionarListener('raiz_aorta', calcularRelacaoAEAo);
        
        // Percentual encurtamento
        adicionarListener('diametro_diastolico_final_ve', function() {
            calcularEncurtamento();
            calcularVolumeTeichholz();
        });
        adicionarListener('diametro_sistolico_final', function() {
            calcularEncurtamento();
            calcularVolumeTeichholz();
        });
        
        // Volumes
        adicionarListener('volume_diastolico_final', calcularFracaoEjecao);
        adicionarListener('volume_sistolico_final', calcularFracaoEjecao);
        
        console.log('🆘 BACKUP: Listeners configurados');
    }
    
    function adicionarListener(id, funcao) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.addEventListener('input', funcao);
            elemento.addEventListener('change', funcao);
            console.log(`🆘 BACKUP: Listener adicionado para ${id}`);
        } else {
            console.warn(`🆘 BACKUP: Elemento ${id} não encontrado`);
        }
    }
    
    function calcularSuperficieCorporal() {
        const peso = obterValor('peso');
        const altura = obterValor('altura');
        
        if (peso > 0 && altura > 0) {
            const bsa = 0.007184 * Math.pow(altura, 0.725) * Math.pow(peso, 0.425);
            definirValor('superficie_corporal', bsa.toFixed(2));
            destacarCampo('superficie_corporal');
            console.log(`🆘 BACKUP: Superfície corporal = ${bsa.toFixed(2)} m²`);
        }
    }
    
    function calcularRelacaoAEAo() {
        const ae = obterValor('atrio_esquerdo');
        const ao = obterValor('raiz_aorta');
        
        if (ae > 0 && ao > 0) {
            const relacao = ae / ao;
            definirValor('relacao_atrio_esquerdo_aorta', relacao.toFixed(2));
            destacarCampo('relacao_atrio_esquerdo_aorta');
            console.log(`🆘 BACKUP: Relação AE/Ao = ${relacao.toFixed(2)}`);
        }
    }
    
    function calcularEncurtamento() {
        const ddve = obterValor('diametro_diastolico_final_ve');
        const dsve = obterValor('diametro_sistolico_final');
        
        if (ddve > 0 && dsve > 0) {
            const encurtamento = ((ddve - dsve) / ddve) * 100;
            definirValor('percentual_encurtamento', encurtamento.toFixed(1));
            destacarCampo('percentual_encurtamento');
            console.log(`🆘 BACKUP: % Encurtamento = ${encurtamento.toFixed(1)}%`);
        }
    }
    
    function calcularVolumeTeichholz() {
        const ddve = obterValor('diametro_diastolico_final_ve');
        const dsve = obterValor('diametro_sistolico_final');
        
        if (ddve > 0) {
            const ddveCm = ddve / 10;
            const vdf = (7 * Math.pow(ddveCm, 3)) / (2.4 + ddveCm);
            definirValor('volume_diastolico_final', vdf.toFixed(1));
            destacarCampo('volume_diastolico_final');
            console.log(`🆘 BACKUP: VDF = ${vdf.toFixed(1)} mL`);
        }
        
        if (dsve > 0) {
            const dsveCm = dsve / 10;
            const vsf = (7 * Math.pow(dsveCm, 3)) / (2.4 + dsveCm);
            definirValor('volume_sistolico_final', vsf.toFixed(1));
            destacarCampo('volume_sistolico_final');
            console.log(`🆘 BACKUP: VSF = ${vsf.toFixed(1)} mL`);
        }
        
        // Calcular fração de ejeção
        setTimeout(calcularFracaoEjecao, 100);
    }
    
    function calcularFracaoEjecao() {
        const vdf = obterValor('volume_diastolico_final');
        const vsf = obterValor('volume_sistolico_final');
        
        if (vdf > 0 && vsf >= 0) {
            const ve = vdf - vsf;
            const fe = (ve / vdf) * 100;
            
            definirValor('volume_ejecao', ve.toFixed(1));
            definirValor('fracao_ejecao', fe.toFixed(1));
            
            destacarCampo('volume_ejecao');
            destacarCampo('fracao_ejecao');
            
            console.log(`🆘 BACKUP: Volume Ejeção = ${ve.toFixed(1)} mL`);
            console.log(`🆘 BACKUP: Fração Ejeção = ${fe.toFixed(1)}%`);
        }
    }
    
    function executarCalculosIniciais() {
        console.log('🆘 BACKUP: Executando cálculos iniciais...');
        
        setTimeout(function() {
            calcularSuperficieCorporal();
            calcularRelacaoAEAo();
            calcularEncurtamento();
            calcularVolumeTeichholz();
            calcularFracaoEjecao();
        }, 500);
    }
    
    function obterValor(id) {
        const elemento = document.getElementById(id);
        return elemento ? parseFloat(elemento.value) || 0 : 0;
    }
    
    function definirValor(id, valor) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.value = valor;
        }
    }
    
    function destacarCampo(id) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.style.backgroundColor = '#e8f5e8';
            elemento.style.borderColor = '#28a745';
            
            setTimeout(function() {
                elemento.style.backgroundColor = '';
                elemento.style.borderColor = '';
            }, 3000);
        }
    }
    
    // Expor função para teste
    window.testarBackupCalculos = function() {
        console.log('🧪 BACKUP: Teste manual executado');
        executarCalculosIniciais();
    };
    
    console.log('🆘 BACKUP: Sistema de backup carregado completamente');
})();
