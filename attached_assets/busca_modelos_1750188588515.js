/**
 * Script para implementação da busca em tempo real de modelos de laudos
 * e preenchimento automático dos campos do formulário
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const searchInput = document.getElementById('padroes-search-input');
    const searchButton = document.getElementById('padroes-search-btn');
    const resultsContainer = document.getElementById('padroes-results');
    
    // Campos do formulário de laudo
    const camposLaudo = {
        resumo_exame: document.getElementById('resumo_exame'),
        ritmo_cardiaco: document.getElementById('ritmo_cardiaco'),
        ventriculo_esquerdo: document.getElementById('ventriculo_esquerdo'),
        ventriculo_direito: document.getElementById('ventriculo_direito'),
        valvas: document.getElementById('valvas'),
        pericardio: document.getElementById('pericardio'),
        aorta: document.getElementById('aorta'),
        conclusao: document.getElementById('conclusao')
    };
    
    // Inicializar a busca em tempo real
    inicializarBuscaTempoReal();
    
    // Carregar alguns modelos iniciais para demonstração
    carregarModelosIniciais();
    
    /**
     * Inicializa a busca em tempo real de modelos de laudo
     */
    function inicializarBuscaTempoReal() {
        // Evento de digitação no campo de busca
        searchInput.addEventListener('input', function() {
            const termo = this.value.trim();
            
            // Só buscar se tiver pelo menos 2 caracteres
            if (termo.length >= 2) {
                buscarModelos(termo);
            } else if (termo.length === 0) {
                // Se o campo estiver vazio, mostrar alguns modelos iniciais
                carregarModelosIniciais();
            } else {
                resultsContainer.style.display = 'none';
            }
        });
        
        // Evento de clique no botão de busca
        searchButton.addEventListener('click', function() {
            const termo = searchInput.value.trim();
            if (termo.length >= 2) {
                buscarModelos(termo);
            } else if (termo.length === 0) {
                // Se o campo estiver vazio, mostrar alguns modelos iniciais
                carregarModelosIniciais();
            }
        });
    }
    
    /**
     * Carrega alguns modelos iniciais para demonstração
     */
    function carregarModelosIniciais() {
        // Modelos locais para demonstração imediata
        const modelosIniciais = [
            {
                id: 'local_normal',
                nome: 'Normal',
                tipo: 'Adulto',
                resumo_exame: 'Exame ecocardiográfico transtorácico realizado em repouso. Boa janela acústica.',
                ritmo_cardiaco: 'Ritmo sinusal durante o exame.',
                ventriculo_esquerdo: 'Dimensões normais. Espessuras parietais normais. Função sistólica global preservada.',
                ventriculo_direito: 'Dimensões e função sistólica normais.',
                valvas: 'Valvas morfologicamente normais, com abertura e fechamento adequados. Ausência de refluxos patológicos.',
                pericardio: 'Pericárdio de espessura normal, sem derrame.',
                aorta: 'Aorta de dimensões normais. Arco aórtico normal.',
                conclusao: 'Exame ecocardiográfico dentro dos limites da normalidade.'
            },
            {
                id: 'local_prolapso',
                nome: 'Prolapso Mitral',
                tipo: 'Adulto',
                resumo_exame: 'Exame ecocardiográfico transtorácico realizado em repouso. Boa janela acústica.',
                ritmo_cardiaco: 'Ritmo sinusal durante o exame.',
                ventriculo_esquerdo: 'Dimensões normais. Espessuras parietais normais. Função sistólica global preservada.',
                ventriculo_direito: 'Dimensões e função sistólica normais.',
                valvas: 'Valva mitral com prolapso do folheto posterior, com refluxo discreto. Demais valvas sem alterações.',
                pericardio: 'Pericárdio de espessura normal, sem derrame.',
                aorta: 'Aorta de dimensões normais. Arco aórtico normal.',
                conclusao: 'Prolapso de valva mitral com insuficiência discreta.'
            },
            {
                id: 'local_hipertrofica',
                nome: 'Cardiomiopatia Hipertrófica',
                tipo: 'Adulto',
                resumo_exame: 'Exame ecocardiográfico transtorácico realizado em repouso. Boa janela acústica.',
                ritmo_cardiaco: 'Ritmo sinusal durante o exame.',
                ventriculo_esquerdo: 'Hipertrofia septal assimétrica. Função sistólica global preservada.',
                ventriculo_direito: 'Dimensões e função sistólica normais.',
                valvas: 'Valvas morfologicamente normais, com abertura e fechamento adequados.',
                pericardio: 'Pericárdio de espessura normal, sem derrame.',
                aorta: 'Aorta de dimensões normais. Arco aórtico normal.',
                conclusao: 'Cardiomiopatia hipertrófica com hipertrofia septal assimétrica.'
            }
        ];
        
        exibirResultados(modelosIniciais);
    }
    
    /**
     * Busca modelos de laudo com base no termo informado
     * @param {string} termo - Termo de busca
     */
    function buscarModelos(termo) {
        // Fazer requisição AJAX para buscar modelos
        fetch(`/buscar_modelos?termo=${encodeURIComponent(termo)}`)
            .then(response => response.json())
            .then(data => {
                if (data.modelos && data.modelos.length > 0) {
                    exibirResultados(data.modelos);
                } else {
                    // Se não encontrar modelos no servidor, usar os locais que correspondam ao termo
                    const modelosLocais = [
                        {
                            id: 'local_normal',
                            nome: 'Normal',
                            tipo: 'Adulto'
                        },
                        {
                            id: 'local_prolapso',
                            nome: 'Prolapso Mitral',
                            tipo: 'Adulto'
                        },
                        {
                            id: 'local_hipertrofica',
                            nome: 'Cardiomiopatia Hipertrófica',
                            tipo: 'Adulto'
                        },
                        {
                            id: 'local_pediatrico',
                            nome: 'Persistência Canal Arterial',
                            tipo: 'Pediátrico'
                        },
                        {
                            id: 'local_amiloidose',
                            nome: 'Amiloidose Cardíaca',
                            tipo: 'Adulto'
                        }
                    ];
                    
                    const resultadosFiltrados = modelosLocais.filter(modelo => 
                        modelo.nome.toLowerCase().includes(termo.toLowerCase()) || 
                        modelo.tipo.toLowerCase().includes(termo.toLowerCase())
                    );
                    
                    exibirResultados(resultadosFiltrados);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar modelos:', error);
                // Em caso de erro, mostrar modelos locais
                carregarModelosIniciais();
            });
    }
    
    /**
     * Exibe os resultados da busca
     * @param {Array} modelos - Lista de modelos encontrados
     */
    function exibirResultados(modelos) {
        // Limpar resultados anteriores
        resultsContainer.innerHTML = '';
        
        if (modelos.length === 0) {
            resultsContainer.innerHTML = '<div class="padrao-item">Nenhum modelo encontrado</div>';
            resultsContainer.style.display = 'block';
            return;
        }
        
        // Criar elemento para cada modelo encontrado
        modelos.forEach(modelo => {
            const itemElement = document.createElement('div');
            itemElement.className = 'padrao-item';
            itemElement.innerHTML = `
                <div class="padrao-titulo">${modelo.nome}</div>
                <div class="padrao-tipo">${modelo.tipo}</div>
            `;
            
            // Adicionar evento de clique para selecionar o modelo
            itemElement.addEventListener('click', function() {
                selecionarModelo(modelo.id, modelo);
            });
            
            resultsContainer.appendChild(itemElement);
        });
        
        // Exibir resultados
        resultsContainer.style.display = 'block';
    }
    
    /**
     * Seleciona um modelo e preenche os campos do formulário
     * @param {string} modeloId - ID do modelo selecionado
     * @param {Object} modeloLocal - Dados do modelo local (opcional)
     */
    function selecionarModelo(modeloId, modeloLocal) {
        // Se for um modelo local, usar diretamente
        if (modeloLocal && modeloId.startsWith('local_')) {
            preencherCamposFormulario(modeloLocal);
            resultsContainer.style.display = 'none';
            searchInput.value = modeloLocal.nome;
            
            // Exibir notificação de sucesso
            const notification = document.getElementById('save-notification');
            notification.textContent = 'Modelo aplicado com sucesso!';
            notification.style.display = 'block';
            
            // Ocultar notificação após 3 segundos
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
            
            return;
        }
        
        // Se não for local, buscar do servidor
        fetch(`/obter_modelo/${modeloId}`)
            .then(response => response.json())
            .then(data => {
                if (data.modelo) {
                    preencherCamposFormulario(data.modelo);
                    resultsContainer.style.display = 'none';
                    searchInput.value = data.modelo.nome;
                    
                    // Exibir notificação de sucesso
                    const notification = document.getElementById('save-notification');
                    notification.textContent = 'Modelo aplicado com sucesso!';
                    notification.style.display = 'block';
                    
                    // Ocultar notificação após 3 segundos
                    setTimeout(() => {
                        notification.style.display = 'none';
                    }, 3000);
                } else {
                    console.error('Modelo não encontrado');
                }
            })
            .catch(error => {
                console.error('Erro ao obter modelo:', error);
            });
    }
    
    /**
     * Preenche os campos do formulário com os dados do modelo
     * @param {Object} modelo - Dados do modelo selecionado
     */
    function preencherCamposFormulario(modelo) {
        // Preencher cada campo do formulário
        for (const campo in camposLaudo) {
            if (modelo[campo] && camposLaudo[campo]) {
                camposLaudo[campo].value = modelo[campo];
            }
        }
    }
});
