/**
 * Sistema de Laudos - JavaScript Nativo
 * Busca por diagnóstico, templates e salvamento automático
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de laudos inicializado');
    initializeLaudoSystem();
});

function initializeLaudoSystem() {
    setupDiagnosticSearch();
    setupTemplateSearch();
    setupAutoSave();
    setupFormValidation();
    setupTemplateApplication();
}

function setupDiagnosticSearch() {
    const buscaDiagnostico = document.getElementById('busca-laudo-diagnostico');
    const categoriaLaudo = document.getElementById('categoria-laudo');
    const limparBusca = document.getElementById('limpar-busca-laudo');
    
    if (buscaDiagnostico) {
        buscaDiagnostico.addEventListener('input', function() {
            const termo = this.value.trim();
            if (termo.length >= 2) {
                buscarLaudosPorDiagnostico(termo);
            } else {
                hideSearchResults();
            }
        });
    }
    
    if (categoriaLaudo) {
        categoriaLaudo.addEventListener('change', function() {
            const termo = buscaDiagnostico ? buscaDiagnostico.value.trim() : '';
            if (termo.length >= 2) {
                buscarLaudosPorDiagnostico(termo);
            }
        });
    }
    
    if (limparBusca) {
        limparBusca.addEventListener('click', function() {
            if (buscaDiagnostico) buscaDiagnostico.value = '';
            if (categoriaLaudo) categoriaLaudo.value = 'Adulto';
            hideSearchResults();
            hideSelectedTemplate();
        });
    }
}

function buscarLaudosPorDiagnostico(termo) {
    const categoria = getValue('categoria-laudo') || 'Adulto';
    
    console.log(`Buscando laudos: "${termo}" categoria: ${categoria}`);
    
    fetch(`/api/buscar-laudos-templates?diagnostico=${encodeURIComponent(termo)}&categoria=${encodeURIComponent(categoria)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySearchResults(data.templates);
            } else {
                console.error('Erro na busca:', data.message);
                displayNoResults();
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            displayNoResults();
        });
}

function displaySearchResults(templates) {
    const resultadosDiv = document.getElementById('resultados-busca-laudo');
    const listaDiv = document.getElementById('lista-templates-laudo');
    
    if (!resultadosDiv || !listaDiv) return;
    
    if (templates.length === 0) {
        displayNoResults();
        return;
    }
    
    listaDiv.innerHTML = '';
    
    templates.forEach(template => {
        const templateCard = createTemplateCard(template);
        listaDiv.appendChild(templateCard);
    });
    
    resultadosDiv.style.display = 'block';
    console.log(`${templates.length} templates encontrados`);
}

function createTemplateCard(template) {
    const div = document.createElement('div');
    div.className = 'col-md-6 mb-3';
    
    div.innerHTML = `
        <div class="card h-100 template-card" data-template-id="${template.id}">
            <div class="card-body">
                <h6 class="card-title text-primary">
                    <i class="fas fa-file-medical me-1"></i>${template.diagnostico}
                </h6>
                <p class="card-text text-muted small mb-2">
                    <i class="fas fa-tag me-1"></i>${template.categoria}
                </p>
                <p class="card-text small">
                    ${template.modo_m_bidimensional ? template.modo_m_bidimensional.substring(0, 100) + '...' : 'Template disponível'}
                </p>
                <button type="button" class="btn btn-primary btn-sm w-100 selecionar-template" 
                        data-template-id="${template.id}"
                        data-diagnostico="${template.diagnostico}">
                    <i class="fas fa-check me-1"></i>Selecionar Template
                </button>
            </div>
        </div>
    `;
    
    // Adicionar evento de clique
    const botao = div.querySelector('.selecionar-template');
    botao.addEventListener('click', function() {
        selectTemplate(template);
    });
    
    return div;
}

function selectTemplate(template) {
    // Armazenar template selecionado
    window.selectedTemplate = template;
    
    // Mostrar template selecionado
    const templateSelecionado = document.getElementById('template-selecionado');
    const nomeTemplate = document.getElementById('nome-template-selecionado');
    
    if (templateSelecionado && nomeTemplate) {
        nomeTemplate.textContent = template.diagnostico;
        templateSelecionado.style.display = 'block';
        
        // Scroll para mostrar o template selecionado
        templateSelecionado.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    console.log('Template selecionado:', template.diagnostico);
}

function setupTemplateApplication() {
    const aplicarBtn = document.getElementById('aplicar-template');
    
    if (aplicarBtn) {
        aplicarBtn.addEventListener('click', function() {
            if (window.selectedTemplate) {
                applyTemplate(window.selectedTemplate);
            }
        });
    }
}

function applyTemplate(template) {
    // Aplicar template aos campos do formulário
    setValue('modo_m_bidimensional', template.modo_m_bidimensional || '');
    setValue('doppler_convencional', template.doppler_convencional || '');
    setValue('doppler_tecidual', template.doppler_tecidual || '');
    setValue('conclusao', template.conclusao || '');
    
    // Atualizar contadores de caracteres
    updateCharCounters();
    
    // Mostrar confirmação
    showNotification('Template aplicado com sucesso!', 'success');
    
    // Esconder template selecionado
    hideSelectedTemplate();
    
    // Scroll para o primeiro campo preenchido
    const firstField = document.getElementById('modo_m_bidimensional');
    if (firstField) {
        firstField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstField.focus();
    }
    
    console.log('Template aplicado:', template.diagnostico);
}

function setupTemplateSearch() {
    const buscaTemplate = document.getElementById('busca-template-laudo');
    
    if (buscaTemplate) {
        buscaTemplate.addEventListener('input', function() {
            const termo = this.value.trim();
            if (termo.length >= 2) {
                buscarTemplatesPersonalizados(termo);
            }
        });
    }
}

function buscarTemplatesPersonalizados(termo) {
    fetch(`/api/templates-laudo?search=${encodeURIComponent(termo)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPersonalizedTemplates(data.templates);
            }
        })
        .catch(error => {
            console.error('Erro na busca de templates personalizados:', error);
        });
}

function displayPersonalizedTemplates(templates) {
    // Implementar exibição de templates personalizados
    console.log('Templates personalizados encontrados:', templates.length);
}

function setupAutoSave() {
    const form = document.getElementById('laudo-form');
    if (!form) return;
    
    const fields = form.querySelectorAll('textarea, input[type="text"]');
    
    fields.forEach(field => {
        field.addEventListener('input', debounce(function() {
            autoSaveForm();
        }, 2000));
    });
    
    // Auto-save a cada 30 segundos
    setInterval(autoSaveForm, 30000);
}

function autoSaveForm() {
    const form = document.getElementById('laudo-form');
    if (!form) return;
    
    const formData = new FormData(form);
    
    fetch(form.action || window.location.pathname, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Auto-Save': 'true'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Laudo salvo automaticamente', 'info', 2000);
        }
    })
    .catch(error => {
        console.error('Erro no auto-save:', error);
    });
}

function setupFormValidation() {
    const form = document.getElementById('laudo-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            showNotification('Por favor, preencha pelo menos uma seção do laudo', 'error');
        }
    });
    
    // Setup character counters
    setupCharCounters();
}

function validateForm() {
    const modoM = getValue('modo_m_bidimensional');
    const doppler = getValue('doppler_convencional');
    const dopplerTec = getValue('doppler_tecidual');
    const conclusao = getValue('conclusao');
    
    return modoM.trim() !== '' || doppler.trim() !== '' || 
           dopplerTec.trim() !== '' || conclusao.trim() !== '';
}

function setupCharCounters() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength') || 2000;
        const counterId = textarea.id + '-counter';
        
        // Criar contador se não existir
        let counter = document.getElementById(counterId);
        if (!counter) {
            counter = document.createElement('div');
            counter.id = counterId;
            counter.className = 'char-counter';
            textarea.parentNode.appendChild(counter);
        }
        
        // Atualizar contador
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${textarea.value.length}/${maxLength} caracteres`;
            
            if (remaining < 100) {
                counter.style.color = '#dc3545';
            } else if (remaining < 200) {
                counter.style.color = '#ffc107';
            } else {
                counter.style.color = '#6c757d';
            }
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter(); // Inicial
    });
}

function updateCharCounters() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const event = new Event('input');
        textarea.dispatchEvent(event);
    });
}

// Utility functions
function displayNoResults() {
    const resultadosDiv = document.getElementById('resultados-busca-laudo');
    const listaDiv = document.getElementById('lista-templates-laudo');
    
    if (!resultadosDiv || !listaDiv) return;
    
    listaDiv.innerHTML = `
        <div class="col-12">
            <div class="text-center py-4 text-muted">
                <i class="fas fa-search fa-2x mb-2"></i>
                <p>Nenhum template encontrado para este diagnóstico.</p>
                <small>Tente termos mais gerais ou verifique a categoria selecionada.</small>
            </div>
        </div>
    `;
    
    resultadosDiv.style.display = 'block';
}

function hideSearchResults() {
    const resultadosDiv = document.getElementById('resultados-busca-laudo');
    if (resultadosDiv) {
        resultadosDiv.style.display = 'none';
    }
}

function hideSelectedTemplate() {
    const templateSelecionado = document.getElementById('template-selecionado');
    if (templateSelecionado) {
        templateSelecionado.style.display = 'none';
    }
    window.selectedTemplate = null;
}

function getValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : '';
}

function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Funções globais para salvamento de templates
function salvarComoTemplate() {
    const nomeTemplate = prompt('Digite um nome para o template:');
    if (!nomeTemplate || nomeTemplate.trim() === '') {
        showNotification('Nome do template é obrigatório', 'error');
        return;
    }
    
    const templateData = {
        nome: nomeTemplate.trim(),
        modo_m_bidimensional: getValue('modo_m_bidimensional'),
        doppler_convencional: getValue('doppler_convencional'),
        doppler_tecidual: getValue('doppler_tecidual'),
        conclusao: getValue('conclusao'),
        categoria: getValue('categoria-laudo') || 'Adulto'
    };
    
    // Validar se há conteúdo
    if (!templateData.modo_m_bidimensional && !templateData.doppler_convencional && 
        !templateData.doppler_tecidual && !templateData.conclusao) {
        showNotification('Preencha pelo menos um campo para salvar o template', 'error');
        return;
    }
    
    fetch('/api/salvar-template-laudo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Template "${nomeTemplate}" salvo com sucesso!`, 'success');
        } else {
            showNotification(`Erro ao salvar template: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Erro ao salvar template:', error);
        showNotification('Erro ao salvar template', 'error');
    });
}

function abrirGerenciadorTemplates() {
    window.open('/templates-laudo', '_blank');
}

function buscarTemplatesLaudo() {
    const termo = getValue('busca-template-laudo');
    const categoria = getValue('filtro-categoria-template');
    
    if (!termo || termo.length < 2) {
        document.getElementById('templates-encontrados').innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="fas fa-search fa-2x mb-2"></i>
                <p>Digite pelo menos 2 caracteres para buscar</p>
            </div>
        `;
        return;
    }
    
    const params = new URLSearchParams({
        search: termo,
        categoria: categoria || ''
    });
    
    fetch(`/api/templates-laudo?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTemplatesPersonalizados(data.templates);
            } else {
                displayTemplatesPersonalizados([]);
            }
        })
        .catch(error => {
            console.error('Erro na busca de templates personalizados:', error);
            displayTemplatesPersonalizados([]);
        });
}

function displayTemplatesPersonalizados(templates) {
    const container = document.getElementById('templates-encontrados');
    
    if (templates.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="fas fa-search fa-2x mb-2"></i>
                <p>Nenhum template encontrado</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    templates.forEach(template => {
        html += `
            <div class="col-md-6 mb-2">
                <div class="card border-primary">
                    <div class="card-body p-2">
                        <h6 class="card-title mb-1">${template.nome}</h6>
                        <p class="card-text small text-muted mb-2">
                            ${template.patologia_nome || 'Template personalizado'}
                        </p>
                        <button type="button" class="btn btn-primary btn-sm w-100" 
                                onclick="aplicarTemplatePersonalizado(${template.id})">
                            <i class="fas fa-check me-1"></i>Aplicar
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function aplicarTemplatePersonalizado(templateId) {
    fetch(`/api/template-laudo-detalhes/${templateId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const template = data.template;
                
                setValue('modo_m_bidimensional', template.modo_m_bidimensional || '');
                setValue('doppler_convencional', template.doppler_convencional || '');
                setValue('doppler_tecidual', template.doppler_tecidual || '');
                setValue('conclusao', template.conclusao || '');
                
                updateCharCounters();
                showNotification(`Template "${template.nome}" aplicado com sucesso!`, 'success');
                
                // Scroll para o primeiro campo preenchido
                const firstField = document.getElementById('modo_m_bidimensional');
                if (firstField) {
                    firstField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstField.focus();
                }
            } else {
                showNotification('Erro ao carregar template', 'error');
            }
        })
        .catch(error => {
            console.error('Erro ao aplicar template:', error);
            showNotification('Erro ao aplicar template', 'error');
        });
}

// Fallback para jQuery não disponível
if (typeof $ === 'undefined') {
    console.log('Sistema de laudos usando JavaScript nativo');
}