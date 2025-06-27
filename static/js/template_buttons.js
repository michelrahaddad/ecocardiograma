/**
 * Sistema de Botões de Template - JavaScript Nativo
 * Implementa todos os botões de template da página de laudos
 */

// Templates predefinidos para cada seção
const TEMPLATES = {
    // Modo M e Bidimensional
    modo_m_normal: {
        text: "Átrio esquerdo, raiz da aorta, ventrículo esquerdo e direito com dimensões normais. Função sistólica do ventrículo esquerdo preservada (FE > 55%). Espessuras parietais dentro dos limites da normalidade. Movimento valvar normal.",
        field: "modo_m_bidimensional"
    },
    modo_m_alterado: {
        text: "Alterações estruturais observadas no modo M e bidimensional. Dimensões cavitárias alteradas em relação aos valores de referência. Função sistólica do ventrículo esquerdo com alterações. Espessuras parietais alteradas.",
        field: "modo_m_bidimensional"
    },
    modo_m_hipertrofia: {
        text: "Hipertrofia ventricular esquerda caracterizada por aumento das espessuras parietais (septo e/ou parede posterior > 11mm). Dimensões cavitárias podem estar preservadas ou reduzidas. Função sistólica preservada.",
        field: "modo_m_bidimensional"
    },
    
    // Doppler Convencional
    doppler_normal: {
        text: "Fluxos transvalvares sem alterações significativas. Ausência de refluxos valvares significativos. Gradientes pressóricos normais. Padrão de enchimento ventricular normal. Velocidades dentro dos limites da normalidade.",
        field: "doppler_convencional"
    },
    doppler_disfuncao: {
        text: "Padrão de disfunção diastólica caracterizado por alterações no enchimento ventricular. Relação E/A alterada. Tempo de desaceleração modificado. Possível elevação das pressões de enchimento do ventrículo esquerdo.",
        field: "doppler_convencional"
    },
    doppler_insuficiencia: {
        text: "Presença de refluxos valvares. Insuficiência identificada com graus variáveis de severidade. Repercussão hemodinâmica avaliada através dos gradientes e volumes cavitários. Avaliação quantitativa dos refluxos.",
        field: "doppler_convencional"
    },
    
    // Doppler Tecidual
    tecidual_normal: {
        text: "Velocidades do anel mitral (e' > 8 cm/s) e relação E/e' < 14, compatíveis com função diastólica normal. Velocidades sistólicas do anel tricúspide preservadas. Padrão de relaxamento normal.",
        field: "doppler_tecidual"
    },
    tecidual_alterado: {
        text: "Velocidades do anel mitral reduzidas (e' < 8 cm/s) sugestivas de disfunção diastólica. Relação E/e' elevada indicando possível aumento das pressões de enchimento. Alterações no padrão de relaxamento ventricular.",
        field: "doppler_tecidual"
    },
    
    // Conclusão
    conclusao_normal: {
        text: "Ecocardiograma bidimensional com doppler colorido e tecidual dentro dos limites da normalidade para a idade.",
        field: "conclusao"
    },
    conclusao_alteracoes: {
        text: "Ecocardiograma bidimensional com doppler colorido e tecidual demonstrando alterações estruturais e/ou funcionais conforme descrito acima.",
        field: "conclusao"
    },
    conclusao_acompanhamento: {
        text: "Ecocardiograma bidimensional com doppler colorido e tecidual demonstrando alterações que necessitam acompanhamento cardiológico regular e monitorização ecocardiográfica periódica.",
        field: "conclusao"
    }
};

// Inicialização do sistema de botões
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando sistema de botões de template...');
    setupTemplateButtons();
});

function setupTemplateButtons() {
    // Buscar todos os botões de template
    const templateButtons = document.querySelectorAll('.template-btn');
    
    templateButtons.forEach(button => {
        const templateKey = button.getAttribute('data-template');
        
        if (templateKey && TEMPLATES[templateKey]) {
            // Remover listeners antigos se existirem
            button.removeEventListener('click', handleTemplateClick);
            
            // Adicionar novo listener
            button.addEventListener('click', function(e) {
                e.preventDefault();
                handleTemplateClick(templateKey, button);
            });
            
            console.log(`Botão configurado: ${templateKey}`);
        }
    });
    
    console.log(`${templateButtons.length} botões de template configurados`);
}

function handleTemplateClick(templateKey, buttonElement) {
    const template = TEMPLATES[templateKey];
    
    if (!template) {
        console.error('Template não encontrado:', templateKey);
        return;
    }
    
    // Aplicar o template ao campo correspondente
    applyTemplateToField(template.field, template.text);
    
    // Feedback visual no botão
    showButtonFeedback(buttonElement);
    
    // Atualizar contador de caracteres
    updateCharCounter(template.field);
    
    // Scroll para o campo
    scrollToField(template.field);
    
    console.log(`Template aplicado: ${templateKey} -> ${template.field}`);
}

function applyTemplateToField(fieldId, text) {
    const field = document.getElementById(fieldId);
    
    if (!field) {
        console.error('Campo não encontrado:', fieldId);
        return;
    }
    
    // Aplicar o texto ao campo
    field.value = text;
    
    // Trigger events para auto-save e validação
    field.dispatchEvent(new Event('input', { bubbles: true }));
    field.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Focus no campo
    field.focus();
}

function showButtonFeedback(button) {
    // Salvar classes originais
    const originalClasses = button.className;
    
    // Aplicar feedback visual
    button.classList.remove('btn-outline-info', 'btn-outline-warning', 'btn-outline-danger', 'btn-outline-success', 'btn-outline-secondary');
    button.classList.add('btn-success');
    
    // Adicionar ícone de sucesso temporário
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check me-1"></i>' + button.textContent;
    
    // Restaurar após 2 segundos
    setTimeout(() => {
        button.className = originalClasses;
        button.innerHTML = originalText;
    }, 2000);
}

function updateCharCounter(fieldId) {
    const field = document.getElementById(fieldId);
    const counterId = fieldId.replace('_', '_count').replace('bidimensional', 'count');
    const counter = document.getElementById(counterId);
    
    if (field && counter) {
        const length = field.value.length;
        counter.textContent = length;
        
        // Atualizar cor do contador baseado no limite
        const maxLength = field.getAttribute('maxlength') || 1000;
        const percentage = (length / maxLength) * 100;
        
        if (percentage > 90) {
            counter.style.color = '#dc3545'; // Vermelho
        } else if (percentage > 75) {
            counter.style.color = '#ffc107'; // Amarelo
        } else {
            counter.style.color = '#6c757d'; // Cinza
        }
    }
}

function scrollToField(fieldId) {
    const field = document.getElementById(fieldId);
    
    if (field) {
        // Scroll suave para o campo
        field.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
        
        // Pequeno delay para garantir que o scroll terminou antes do focus
        setTimeout(() => {
            field.focus();
        }, 500);
    }
}

// Função para adicionar template personalizado (futura implementação)
function addCustomTemplate(key, text, fieldId) {
    TEMPLATES[key] = {
        text: text,
        field: fieldId
    };
    
    console.log(`Template personalizado adicionado: ${key}`);
}

// Função para obter todos os templates disponíveis
function getAvailableTemplates() {
    return Object.keys(TEMPLATES);
}

// Função para aplicar template por chave (API pública)
function applyTemplate(templateKey) {
    const template = TEMPLATES[templateKey];
    
    if (template) {
        applyTemplateToField(template.field, template.text);
        updateCharCounter(template.field);
        scrollToField(template.field);
        
        // Mostrar notificação de sucesso
        showNotification('Template aplicado com sucesso!', 'success');
    } else {
        console.error('Template não encontrado:', templateKey);
        showNotification('Template não encontrado', 'error');
    }
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        info: '#17a2b8',
        warning: '#ffc107'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 12px 20px;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-weight: 500;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remover após 3 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Exportar funções para uso global
window.applyTemplate = applyTemplate;
window.setupTemplateButtons = setupTemplateButtons;
window.getAvailableTemplates = getAvailableTemplates;

console.log('Sistema de botões de template carregado com sucesso');