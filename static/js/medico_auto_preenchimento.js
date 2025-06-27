/**
 * Sistema de Ecocardiograma - Grupo Vidah
 * Auto-preenchimento e Gestão de Médicos
 */

$(document).ready(function() {
    initializeMedicoAutoComplete();
    loadMedicoSelecionado();
    setupMedicoSearch();
});

function initializeMedicoAutoComplete() {
    // Lista de médicos comuns no sistema
    const medicosComuns = [
        'Michel Raineri Haddad CRM:183299',
        'Dr. João Silva CRM:123456',
        'Dra. Maria Santos CRM:654321',
        'Dr. Carlos Oliveira CRM:111222',
        'Dra. Ana Costa CRM:333444'
    ];
    
    // Configurar autocomplete para médico responsável
    setupAutoComplete('#medico_usuario', medicosComuns);
    
    // Configurar autocomplete para médico solicitante
    setupAutoComplete('#medico_solicitante', medicosComuns);
    
    // Adicionar funcionalidade de busca
    setupMedicoLookup();
}

function setupAutoComplete(selector, options) {
    const input = $(selector);
    if (input.length === 0) return;
    
    // Criar container para sugestões
    const suggestionsContainer = $('<div class="medico-suggestions"></div>');
    suggestionsContainer.css({
        position: 'absolute',
        top: '100%',
        left: '0',
        right: '0',
        backgroundColor: '#fff',
        border: '1px solid #ced4da',
        borderTop: 'none',
        borderRadius: '0 0 0.375rem 0.375rem',
        maxHeight: '200px',
        overflowY: 'auto',
        zIndex: 1000,
        display: 'none'
    });
    
    // Posicionar container
    input.parent().css('position', 'relative');
    input.after(suggestionsContainer);
    
    // Event listener para input
    input.on('input', function() {
        const value = $(this).val().toLowerCase();
        
        if (value.length < 2) {
            suggestionsContainer.hide();
            return;
        }
        
        const filtered = options.filter(option => 
            option.toLowerCase().includes(value)
        );
        
        if (filtered.length > 0) {
            showSuggestions(suggestionsContainer, filtered, input);
        } else {
            suggestionsContainer.hide();
        }
    });
    
    // Esconder sugestões quando clicar fora
    $(document).on('click', function(e) {
        if (!input.is(e.target) && !suggestionsContainer.is(e.target) && 
            suggestionsContainer.has(e.target).length === 0) {
            suggestionsContainer.hide();
        }
    });
    
    // Teclas de navegação
    input.on('keydown', function(e) {
        handleSuggestionNavigation(e, suggestionsContainer, input);
    });
}

function showSuggestions(container, suggestions, input) {
    container.empty();
    
    suggestions.forEach((suggestion, index) => {
        const item = $('<div class="suggestion-item"></div>');
        item.text(suggestion);
        item.css({
            padding: '0.5rem',
            cursor: 'pointer',
            borderBottom: '1px solid #f0f0f0'
        });
        
        // Hover effect
        item.on('mouseenter', function() {
            container.find('.suggestion-item').removeClass('active');
            $(this).addClass('active');
        });
        
        // Click handler
        item.on('click', function() {
            input.val(suggestion);
            container.hide();
            input.focus();
        });
        
        container.append(item);
    });
    
    // Aplicar estilo para item ativo
    $('<style>')
        .prop('type', 'text/css')
        .html('.suggestion-item.active { background-color: #0a2853; color: white; }')
        .appendTo('head');
    
    container.show();
}

function handleSuggestionNavigation(e, container, input) {
    const items = container.find('.suggestion-item');
    const activeItem = items.filter('.active');
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            if (activeItem.length === 0) {
                items.first().addClass('active');
            } else {
                const next = activeItem.next('.suggestion-item');
                if (next.length > 0) {
                    activeItem.removeClass('active');
                    next.addClass('active');
                }
            }
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            if (activeItem.length > 0) {
                const prev = activeItem.prev('.suggestion-item');
                if (prev.length > 0) {
                    activeItem.removeClass('active');
                    prev.addClass('active');
                } else {
                    activeItem.removeClass('active');
                }
            }
            break;
            
        case 'Enter':
            e.preventDefault();
            if (activeItem.length > 0) {
                input.val(activeItem.text());
                container.hide();
            }
            break;
            
        case 'Escape':
            container.hide();
            break;
    }
}

function setupMedicoLookup() {
    // Botão para buscar médicos cadastrados
    const lookupButton = $('<button type="button" class="btn btn-outline-secondary btn-sm ms-2">');
    lookupButton.html('<i class="fas fa-search"></i>');
    lookupButton.attr('title', 'Buscar médicos cadastrados');
    
    // Adicionar botão ao lado dos campos de médico
    $('#medico_usuario, #medico_solicitante').each(function() {
        const input = $(this);
        const wrapper = $('<div class="input-group"></div>');
        
        input.wrap(wrapper);
        input.after(lookupButton.clone());
    });
    
    // Event handler para busca
    $(document).on('click', '.btn-outline-secondary', function() {
        const input = $(this).siblings('input');
        showMedicoModal(input);
    });
}

function showMedicoModal(targetInput) {
    // Criar modal se não existir
    let modal = $('#medico-lookup-modal');
    
    if (modal.length === 0) {
        modal = createMedicoModal();
    }
    
    // Armazenar referência do input alvo
    modal.data('target-input', targetInput);
    
    // Carregar lista de médicos
    loadMedicosList(modal);
    
    // Mostrar modal
    modal.modal('show');
}

function createMedicoModal() {
    const modalHtml = `
        <div class="modal fade" id="medico-lookup-modal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-user-md me-2"></i>Selecionar Médico
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <input type="text" class="form-control" id="medico-search" 
                                   placeholder="Buscar por nome ou CRM...">
                        </div>
                        <div id="medicos-list" class="list-group">
                            <div class="text-center py-3">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Carregando...</span>
                                </div>
                                <p class="mt-2">Carregando médicos...</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            Cancelar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const modal = $(modalHtml);
    $('body').append(modal);
    
    // Configurar busca em tempo real
    modal.find('#medico-search').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        filterMedicosList(modal, searchTerm);
    });
    
    return modal;
}

function loadMedicosList(modal) {
    const listContainer = modal.find('#medicos-list');
    
    // Simular carregamento da API ou usar dados locais
    setTimeout(() => {
        const medicos = getMedicosData();
        renderMedicosList(listContainer, medicos);
    }, 500);
}

function getMedicosData() {
    // Em um ambiente real, isso viria de uma API
    // Por ora, retornar dados simulados baseados no localStorage ou dados estáticos
    const medicoSelecionado = JSON.parse(localStorage.getItem('medicoSelecionado') || '{}');
    
    const medicosEstaticos = [
        {
            id: 1,
            nome: 'Michel Raineri Haddad',
            crm: 'CRM:183299',
            especialidade: 'Cardiologia',
            assinatura: true
        },
        {
            id: 2,
            nome: 'João Silva',
            crm: 'CRM:123456',
            especialidade: 'Cardiologia',
            assinatura: false
        },
        {
            id: 3,
            nome: 'Maria Santos',
            crm: 'CRM:654321',
            especialidade: 'Ecocardiografia',
            assinatura: true
        }
    ];
    
    // Adicionar médico selecionado se existir
    if (medicoSelecionado.nome) {
        const existe = medicosEstaticos.find(m => m.id === medicoSelecionado.id);
        if (!existe) {
            medicosEstaticos.unshift({
                id: medicoSelecionado.id,
                nome: medicoSelecionado.nome,
                crm: medicoSelecionado.crm || '',
                especialidade: 'Cardiologia',
                assinatura: !!medicoSelecionado.assinatura_data,
                selecionado: true
            });
        }
    }
    
    return medicosEstaticos;
}

function renderMedicosList(container, medicos) {
    container.empty();
    
    if (medicos.length === 0) {
        container.html(`
            <div class="text-center py-4">
                <i class="fas fa-user-md fa-3x text-muted mb-3"></i>
                <p class="text-muted">Nenhum médico encontrado</p>
            </div>
        `);
        return;
    }
    
    medicos.forEach(medico => {
        const item = createMedicoListItem(medico);
        container.append(item);
    });
}

function createMedicoListItem(medico) {
    const item = $(`
        <div class="list-group-item list-group-item-action medico-item" data-medico-id="${medico.id}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1">${medico.nome}
                        ${medico.selecionado ? '<span class="badge bg-success ms-2">Selecionado</span>' : ''}
                    </h6>
                    <p class="mb-1 text-muted">${medico.crm}</p>
                    <small class="text-muted">${medico.especialidade}</small>
                </div>
                <div class="text-end">
                    ${medico.assinatura ? 
                        '<i class="fas fa-signature text-success" title="Com assinatura"></i>' : 
                        '<i class="fas fa-signature text-muted" title="Sem assinatura"></i>'
                    }
                </div>
            </div>
        </div>
    `);
    
    // Click handler
    item.on('click', function() {
        const medicoCompleto = `${medico.nome} ${medico.crm}`;
        selectMedico(medicoCompleto);
    });
    
    return item;
}

function selectMedico(medicoCompleto) {
    const modal = $('#medico-lookup-modal');
    const targetInput = modal.data('target-input');
    
    if (targetInput) {
        targetInput.val(medicoCompleto);
        targetInput.trigger('change');
    }
    
    modal.modal('hide');
}

function filterMedicosList(modal, searchTerm) {
    const items = modal.find('.medico-item');
    
    items.each(function() {
        const item = $(this);
        const text = item.text().toLowerCase();
        
        if (text.includes(searchTerm)) {
            item.show();
        } else {
            item.hide();
        }
    });
}

function loadMedicoSelecionado() {
    // Carregar médico selecionado do localStorage
    const medicoSelecionado = JSON.parse(localStorage.getItem('medicoSelecionado') || '{}');
    
    if (medicoSelecionado.nome) {
        const medicoCompleto = `${medicoSelecionado.nome} ${medicoSelecionado.crm || ''}`;
        
        // Preencher campo de médico responsável se estiver vazio
        const medicoUsuario = $('#medico_usuario');
        if (medicoUsuario.length && !medicoUsuario.val()) {
            medicoUsuario.val(medicoCompleto);
        }
    }
}

function setupMedicoSearch() {
    // Funcionalidade de busca avançada
    let searchTimeout;
    
    $('.medico-search-input').on('input', function() {
        const input = $(this);
        const searchTerm = input.val();
        
        clearTimeout(searchTimeout);
        
        if (searchTerm.length >= 2) {
            searchTimeout = setTimeout(() => {
                searchMedicos(searchTerm, input);
            }, 300);
        }
    });
}

function searchMedicos(term, inputElement) {
    // Simular busca na API
    const resultados = getMedicosData().filter(medico => 
        medico.nome.toLowerCase().includes(term.toLowerCase()) ||
        medico.crm.toLowerCase().includes(term.toLowerCase())
    );
    
    showSearchResults(resultados, inputElement);
}

function showSearchResults(resultados, inputElement) {
    // Criar container de resultados se não existir
    let resultsContainer = inputElement.siblings('.search-results');
    
    if (resultsContainer.length === 0) {
        resultsContainer = $('<div class="search-results"></div>');
        resultsContainer.css({
            position: 'absolute',
            top: '100%',
            left: '0',
            right: '0',
            backgroundColor: '#fff',
            border: '1px solid #ced4da',
            borderRadius: '0 0 0.375rem 0.375rem',
            maxHeight: '200px',
            overflowY: 'auto',
            zIndex: 1000
        });
        
        inputElement.parent().css('position', 'relative');
        inputElement.after(resultsContainer);
    }
    
    // Renderizar resultados
    resultsContainer.empty();
    
    resultados.forEach(medico => {
        const item = $(`
            <div class="search-result-item p-2 border-bottom" style="cursor: pointer;">
                <div class="fw-bold">${medico.nome}</div>
                <small class="text-muted">${medico.crm} - ${medico.especialidade}</small>
            </div>
        `);
        
        item.on('click', function() {
            inputElement.val(`${medico.nome} ${medico.crm}`);
            resultsContainer.remove();
        });
        
        item.on('mouseenter', function() {
            $(this).css('backgroundColor', '#f8f9fa');
        });
        
        item.on('mouseleave', function() {
            $(this).css('backgroundColor', '#fff');
        });
        
        resultsContainer.append(item);
    });
    
    resultsContainer.show();
    
    // Esconder resultados quando clicar fora
    $(document).on('click', function(e) {
        if (!inputElement.is(e.target) && !resultsContainer.is(e.target) && 
            resultsContainer.has(e.target).length === 0) {
            resultsContainer.remove();
        }
    });
}

// Função para salvar médico selecionado
function salvarMedicoSelecionado(medico) {
    localStorage.setItem('medicoSelecionado', JSON.stringify(medico));
    
    // Notificar outros componentes
    $(document).trigger('medicoSelecionado', medico);
}

// Função para obter médico selecionado
function obterMedicoSelecionado() {
    return JSON.parse(localStorage.getItem('medicoSelecionado') || '{}');
}

// Exportar funções para uso global
window.MedicoAutoPreenchimento = {
    initializeMedicoAutoComplete,
    showMedicoModal,
    salvarMedicoSelecionado,
    obterMedicoSelecionado,
    loadMedicoSelecionado
};
