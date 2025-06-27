/**
 * Sistema de Gerenciamento de Templates - JavaScript Nativo
 * Elimina dependência do jQuery e implementa funcionalidades completas
 */

let templatesData = [];
let currentPage = 1;
const itemsPerPage = 10;

// Inicialização do sistema
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de templates inicializado com JavaScript nativo');
    
    // Configurar event listeners
    setupEventListeners();
    
    // Carregar templates iniciais
    buscarTemplates();
});

function setupEventListeners() {
    // Botão de busca
    const btnBuscar = document.getElementById('btn-buscar');
    if (btnBuscar) {
        btnBuscar.addEventListener('click', buscarTemplates);
    }
    
    // Enter na busca
    const buscaTexto = document.getElementById('busca-texto');
    if (buscaTexto) {
        buscaTexto.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                buscarTemplates();
            }
        });
    }
    
    // Filtros
    const filtroCategoria = document.getElementById('filtro-categoria');
    const filtroMedico = document.getElementById('filtro-medico');
    const filtroFavoritos = document.getElementById('filtro-favoritos');
    const filtroPublicos = document.getElementById('filtro-publicos');
    
    [filtroCategoria, filtroMedico, filtroFavoritos, filtroPublicos].forEach(element => {
        if (element) {
            element.addEventListener('change', buscarTemplates);
        }
    });
}

function buscarTemplates() {
    const loading = document.getElementById('loading-templates');
    const container = document.getElementById('templates-container');
    
    if (loading) loading.style.display = 'block';
    if (container) container.innerHTML = '';
    
    // Coletar parâmetros de busca
    const params = new URLSearchParams();
    
    const search = document.getElementById('busca-texto')?.value?.trim();
    if (search) params.append('search', search);
    
    const categoria = document.getElementById('filtro-categoria')?.value;
    if (categoria) params.append('categoria', categoria);
    
    const medico = document.getElementById('filtro-medico')?.value;
    if (medico) params.append('medico', medico);
    
    const favoritos = document.getElementById('filtro-favoritos')?.checked;
    if (favoritos) params.append('favoritos', 'true');
    
    const publicos = document.getElementById('filtro-publicos')?.checked;
    if (publicos) params.append('publicos', 'true');
    
    // Fazer requisição
    fetch(`/api/templates-laudo?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (loading) loading.style.display = 'none';
            
            if (data.success) {
                templatesData = data.templates;
                renderizarTemplates(data.templates);
                atualizarContador(data.total);
            } else {
                mostrarErro('Erro ao buscar templates: ' + data.message);
            }
        })
        .catch(error => {
            if (loading) loading.style.display = 'none';
            console.error('Erro ao buscar templates:', error);
            mostrarErro('Erro de conexão ao buscar templates');
        });
}

function renderizarTemplates(templates) {
    const container = document.getElementById('templates-container');
    if (!container) return;
    
    if (templates.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">Nenhum template encontrado</h5>
                <p class="text-muted">Tente ajustar os filtros de busca ou criar um novo template.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    templates.forEach(template => {
        const badges = [];
        if (template.favorito) {
            badges.push('<span class="badge badge-favorito"><i class="fas fa-star me-1"></i>Favorito</span>');
        }
        if (template.publico) {
            badges.push('<span class="badge badge-publico"><i class="fas fa-globe me-1"></i>Público</span>');
        }
        
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="template-card">
                    <div class="template-header">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${template.nome}</h6>
                                <small class="text-muted">
                                    <i class="fas fa-folder me-1"></i>${template.categoria}
                                </small>
                            </div>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-outline-secondary" onclick="toggleDropdown(${template.id})">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <ul class="dropdown-menu" id="dropdown-${template.id}" style="display: none;">
                                    <li><a class="dropdown-item" href="#" onclick="editarTemplate(${template.id})">
                                        <i class="fas fa-edit me-2"></i>Editar
                                    </a></li>
                                    <li><a class="dropdown-item" href="#" onclick="duplicarTemplate(${template.id})">
                                        <i class="fas fa-copy me-2"></i>Duplicar
                                    </a></li>
                                    <li><a class="dropdown-item" href="#" onclick="excluirTemplate(${template.id}, '${template.nome}')">
                                        <i class="fas fa-trash me-2"></i>Excluir
                                    </a></li>
                                </ul>
                            </div>
                        </div>
                        ${badges.length > 0 ? '<div class="mt-2">' + badges.join(' ') + '</div>' : ''}
                    </div>
                    <div class="template-body">
                        ${template.modo_m_bidimensional ? `<p class="mb-2"><strong>Modo M:</strong> ${template.modo_m_bidimensional.substring(0, 100)}${template.modo_m_bidimensional.length > 100 ? '...' : ''}</p>` : ''}
                        ${template.conclusao ? `<p class="mb-2"><strong>Conclusão:</strong> ${template.conclusao.substring(0, 100)}${template.conclusao.length > 100 ? '...' : ''}</p>` : ''}
                        <div class="mt-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <small class="text-muted">
                                    <i class="fas fa-chart-line me-1"></i>Usado ${template.vezes_usado || 0}x
                                </small>
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>${template.created_at_formatted || 'Data não disponível'}
                                </small>
                            </div>
                            <div class="d-flex justify-content-end">
                                <button class="btn btn-sm btn-primary" onclick="visualizarTemplate(${template.id})">
                                    <i class="fas fa-eye me-1"></i>Ver Completo
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function atualizarContador(total) {
    const contador = document.getElementById('contador-templates');
    if (contador) {
        contador.textContent = total;
    }
}

function toggleDropdown(templateId) {
    const dropdown = document.getElementById(`dropdown-${templateId}`);
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        
        // Fechar todos os outros dropdowns
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.display = 'none';
        });
        
        // Toggle do dropdown atual
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
}

function abrirModalNovoTemplate() {
    const modal = document.getElementById('modalNovoTemplate');
    const form = document.getElementById('form-novo-template');
    
    if (form) form.reset();
    if (modal) {
        // Simular modal do Bootstrap
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.classList.add('modal-open');
    }
}

function fecharModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    }
}

function criarNovoTemplate() {
    const formData = {
        nome: document.getElementById('novo-nome')?.value,
        categoria: document.getElementById('novo-categoria')?.value || 'Personalizado',
        modo_m_bidimensional: document.getElementById('novo-modo-m')?.value || '',
        doppler_convencional: document.getElementById('novo-doppler')?.value || '',
        doppler_tecidual: document.getElementById('novo-tecidual')?.value || '',
        conclusao: document.getElementById('novo-conclusao')?.value || ''
    };
    
    if (!formData.nome) {
        mostrarErro('Nome do template é obrigatório');
        return;
    }
    
    fetch('/api/salvar-template-laudo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fecharModal('modalNovoTemplate');
            document.getElementById('form-novo-template')?.reset();
            buscarTemplates();
            mostrarSucesso('Template criado com sucesso!');
        } else {
            mostrarErro('Erro ao criar template: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro ao criar template:', error);
        mostrarErro('Erro de conexão ao criar template');
    });
}

function editarTemplate(templateId) {
    console.log('Editando template:', templateId);
    // Implementar edição se necessário
    mostrarInfo('Funcionalidade de edição será implementada em breve');
}

function duplicarTemplate(templateId) {
    const template = templatesData.find(t => t.id === templateId);
    if (!template) return;
    
    // Preencher modal com dados do template
    const nomeInput = document.getElementById('novo-nome');
    const modoMInput = document.getElementById('novo-modo-m');
    const dopplerInput = document.getElementById('novo-doppler');
    const tecidualInput = document.getElementById('novo-tecidual');
    const conclusaoInput = document.getElementById('novo-conclusao');
    
    if (nomeInput) nomeInput.value = template.nome + ' (Cópia)';
    if (modoMInput) modoMInput.value = template.modo_m_bidimensional || '';
    if (dopplerInput) dopplerInput.value = template.doppler_convencional || '';
    if (tecidualInput) tecidualInput.value = template.doppler_tecidual || '';
    if (conclusaoInput) conclusaoInput.value = template.conclusao || '';
    
    abrirModalNovoTemplate();
}

function excluirTemplate(templateId, nomeTemplate) {
    if (confirm(`Tem certeza que deseja excluir o template "${nomeTemplate}"?\n\nEsta ação não pode ser desfeita.`)) {
        fetch(`/api/templates-laudo/${templateId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                buscarTemplates();
                mostrarSucesso('Template excluído com sucesso!');
            } else {
                mostrarErro('Erro ao excluir template: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro ao excluir template:', error);
            mostrarErro('Erro de conexão ao excluir template');
        });
    }
}

function visualizarTemplate(templateId) {
    const template = templatesData.find(t => t.id === templateId);
    if (!template) return;
    
    // Criar modal de visualização
    const modalContent = `
        <div class="modal fade show" id="modalVisualizarTemplate" style="display: block;">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-eye me-2"></i>${template.nome}
                        </h5>
                        <button type="button" class="btn-close" onclick="fecharModal('modalVisualizarTemplate')"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Categoria:</strong> ${template.categoria || 'Não especificada'}
                            </div>
                            <div class="col-md-6">
                                <strong>Criado em:</strong> ${template.created_at_formatted || 'Data não disponível'}
                            </div>
                        </div>
                        
                        ${template.modo_m_bidimensional ? `
                        <div class="mb-3">
                            <strong>Modo M e Bidimensional:</strong>
                            <div class="border p-2 mt-1">${template.modo_m_bidimensional}</div>
                        </div>
                        ` : ''}
                        
                        ${template.doppler_convencional ? `
                        <div class="mb-3">
                            <strong>Doppler Convencional:</strong>
                            <div class="border p-2 mt-1">${template.doppler_convencional}</div>
                        </div>
                        ` : ''}
                        
                        ${template.doppler_tecidual ? `
                        <div class="mb-3">
                            <strong>Doppler Tecidual:</strong>
                            <div class="border p-2 mt-1">${template.doppler_tecidual}</div>
                        </div>
                        ` : ''}
                        
                        ${template.conclusao ? `
                        <div class="mb-3">
                            <strong>Conclusão:</strong>
                            <div class="border p-2 mt-1">${template.conclusao}</div>
                        </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="fecharModal('modalVisualizarTemplate')">Fechar</button>
                        <button type="button" class="btn btn-primary" onclick="editarTemplate(${template.id}); fecharModal('modalVisualizarTemplate');">
                            <i class="fas fa-edit me-1"></i>Editar
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-backdrop fade show"></div>
    `;
    
    // Remover modal anterior se existir
    const modalAnterior = document.getElementById('modalVisualizarTemplate');
    if (modalAnterior) {
        modalAnterior.remove();
    }
    
    // Adicionar novo modal
    document.body.insertAdjacentHTML('beforeend', modalContent);
    document.body.classList.add('modal-open');
}

function limparFiltros() {
    const elementos = [
        'busca-texto',
        'filtro-categoria',
        'filtro-medico'
    ];
    
    elementos.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) elemento.value = '';
    });
    
    const checkboxes = ['filtro-favoritos', 'filtro-publicos'];
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) checkbox.checked = false;
    });
    
    buscarTemplates();
}

// Funções de notificação
function mostrarSucesso(mensagem) {
    mostrarToast(mensagem, 'success');
}

function mostrarErro(mensagem) {
    mostrarToast(mensagem, 'error');
}

function mostrarInfo(mensagem) {
    mostrarToast(mensagem, 'info');
}

function mostrarToast(mensagem, tipo) {
    const cores = {
        success: 'bg-success',
        error: 'bg-danger', 
        info: 'bg-info'
    };
    
    const toastId = 'toast-' + Date.now();
    const toast = `
        <div class="toast align-items-center text-white ${cores[tipo]} border-0 position-fixed" 
             id="${toastId}" 
             style="top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    ${mensagem}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        onclick="document.getElementById('${toastId}').remove()"></button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toast);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            toastElement.remove();
        }
    }, 5000);
}

// Fechar dropdowns ao clicar fora
document.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});