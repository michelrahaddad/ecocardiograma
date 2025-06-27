// Arquivo para gerenciar os modelos de laudo pré-definidos
$(document).ready(function() {
    // Carregar modelos de laudo
    const modelos = {
        "normal": {
            titulo: "Normal",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Boa janela acústica. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com dimensões normais. Espessuras parietais normais. Função sistólica global preservada.\n\nVentrículo direito com dimensões e função sistólica normais.\n\nValvas morfologicamente normais, com abertura e fechamento adequados. Ausência de refluxos patológicos.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais. Arco aórtico normal.\n\nExame ecocardiográfico dentro dos limites da normalidade."
        },
        "hipertensao": {
            titulo: "Hipertensão",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Paciente hipertenso. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com hipertrofia concêntrica. Função sistólica global preservada.\n\nVentrículo direito com dimensões e função sistólica normais.\n\nValvas morfologicamente normais, com abertura e fechamento adequados. Insuficiência mitral discreta.\n\nPericárdio de espessura normal, sem derrame.\n\nDilatação discreta da raiz da aorta.\n\nHipertrofia concêntrica do ventrículo esquerdo. Insuficiência mitral discreta. Dilatação discreta da raiz da aorta."
        },
        "estenose_mitral": {
            titulo: "Estenose Mitral",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Paciente com histórico de doença reumática. Ritmo de fibrilação atrial durante o exame.\n\nVentrículo esquerdo com dimensões normais. Função sistólica global preservada.\n\nVentrículo direito com dimensões normais. Função sistólica preservada.\n\nValva mitral com folhetos espessados e calcificados, com mobilidade reduzida. Área valvar mitral estimada em 1.2 cm². Gradiente médio transvalvar de 12 mmHg. Insuficiência mitral discreta.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta com dimensões normais.\n\nEstenose mitral moderada de etiologia reumática. Fibrilação atrial."
        },
        "prolapso_mitral": {
            titulo: "Prolapso Mitral",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Boa janela acústica. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com dimensões normais. Função sistólica global preservada.\n\nVentrículo direito com dimensões e função sistólica normais.\n\nValva mitral com prolapso do folheto posterior. Insuficiência mitral discreta a moderada.\n\nDemais valvas morfologicamente normais, com abertura e fechamento adequados.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais.\n\nProlapso da valva mitral com insuficiência mitral discreta a moderada."
        },
        "disfuncao_sistolica": {
            titulo: "Disfunção Sistólica",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com dilatação moderada. Hipocinesia difusa. Função sistólica global reduzida (fração de ejeção estimada em 35%).\n\nVentrículo direito com dimensões normais. Função sistólica preservada.\n\nInsuficiência mitral funcional discreta a moderada. Demais valvas sem alterações significativas.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais.\n\nDilatação moderada do ventrículo esquerdo com disfunção sistólica moderada. Insuficiência mitral funcional."
        },
        "disfuncao_diastolica": {
            titulo: "Disfunção Diastólica",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com dimensões normais. Hipertrofia concêntrica discreta. Função sistólica global preservada.\n\nRelação E/A < 1, tempo de desaceleração da onda E prolongado, relação E/e' aumentada, sugerindo disfunção diastólica grau I (alteração do relaxamento).\n\nVentrículo direito com dimensões e função sistólica normais.\n\nValvas morfologicamente normais, com abertura e fechamento adequados.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais.\n\nHipertrofia concêntrica discreta do ventrículo esquerdo com disfunção diastólica grau I."
        },
        "cardiopatia_hipertrofica": {
            titulo: "Cardiopatia Hipertrófica",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com hipertrofia assimétrica, predominante em septo interventricular (espessura de 22mm). Função sistólica global preservada. Obstrução dinâmica da via de saída do ventrículo esquerdo com gradiente estimado em 45 mmHg em repouso.\n\nMovimento sistólico anterior da valva mitral. Insuficiência mitral moderada.\n\nVentrículo direito com dimensões e função sistólica normais.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais.\n\nCardiopatia hipertrófica septal assimétrica com obstrução dinâmica da via de saída do ventrículo esquerdo. Insuficiência mitral moderada."
        },
        "infarto_miocardio": {
            titulo: "Infarto do Miocárdio",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com dimensões normais. Acinesia da parede anterior e do septo anterior. Hipocinesia da parede lateral. Função sistólica global reduzida (fração de ejeção estimada em 40%).\n\nVentrículo direito com dimensões e função sistólica normais.\n\nInsuficiência mitral discreta. Demais valvas sem alterações significativas.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais.\n\nDisfunção sistólica moderada do ventrículo esquerdo com alterações segmentares da contratilidade compatíveis com infarto prévio em território da artéria descendente anterior."
        },
        "valvopatia_aortica": {
            titulo: "Valvopatia Aórtica",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Ritmo sinusal durante o exame.\n\nVentrículo esquerdo com hipertrofia concêntrica moderada. Função sistólica global preservada.\n\nValva aórtica tricúspide com folhetos espessados e calcificados, com mobilidade reduzida. Área valvar aórtica estimada em 0.9 cm². Gradiente médio transvalvar de 45 mmHg. Insuficiência aórtica discreta.\n\nVentrículo direito com dimensões e função sistólica normais.\n\nDemais valvas sem alterações significativas.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta ascendente com dilatação discreta.\n\nEstenose aórtica importante. Insuficiência aórtica discreta. Hipertrofia concêntrica moderada do ventrículo esquerdo."
        },
        "comunicacao_interatrial": {
            titulo: "Comunicação Interatrial",
            conteudo: "Exame ecocardiográfico transtorácico realizado em repouso. Ritmo sinusal durante o exame.\n\nComunicação interatrial tipo ostium secundum medindo aproximadamente 15mm, com shunt esquerda-direita.\n\nVentrículo direito com dilatação moderada. Função sistólica preservada.\n\nVentrículo esquerdo com dimensões normais. Função sistólica global preservada.\n\nValvas morfologicamente normais, com abertura e fechamento adequados.\n\nPericárdio de espessura normal, sem derrame.\n\nAorta de dimensões normais.\n\nComunicação interatrial tipo ostium secundum com shunt esquerda-direita. Dilatação moderada do ventrículo direito."
        }
    };

    // Função para carregar modelos do banco de dados
    function carregarModelosDoBanco() {
        $.ajax({
            url: '/buscar_modelo_laudo',
            type: 'GET',
            data: { termo: '' },
            success: function(response) {
                // Limpar resultados anteriores
                $('#padroes-results').empty();
                
                // Adicionar modelos do banco de dados
                if (response && response.length > 0) {
                    response.forEach(function(modelo) {
                        $('#padroes-results').append(`
                            <div class="padrao-item" data-id="db_${modelo.id}" data-conteudo="${encodeURIComponent(modelo.conteudo)}">
                                <div class="padrao-titulo">${modelo.nome}</div>
                                <div class="padrao-tipo">Modelo do banco</div>
                            </div>
                        `);
                    });
                }
                
                // Adicionar também os modelos pré-definidos
                for (const [id, modelo] of Object.entries(modelos)) {
                    $('#padroes-results').append(`
                        <div class="padrao-item" data-id="${id}">
                            <div class="padrao-titulo">${modelo.titulo}</div>
                            <div class="padrao-tipo">Modelo pré-definido</div>
                        </div>
                    `);
                }
                
                // Adicionar evento de clique para os itens
                $('.padrao-item').click(function() {
                    const modeloId = $(this).data('id');
                    const conteudoEncoded = $(this).data('conteudo');
                    
                    if (modeloId.startsWith('db_')) {
                        // É um modelo do banco de dados
                        const conteudo = conteudoEncoded ? decodeURIComponent(conteudoEncoded) : '';
                        if (conteudo) {
                            preencherCamposComModelo(conteudo);
                        } else {
                            // Se não tiver o conteúdo no data attribute, buscar do servidor
                            const dbId = modeloId.replace('db_', '');
                            buscarModeloDoBanco(dbId);
                        }
                    } else {
                        // É um modelo pré-definido
                        selecionarModelo(modeloId);
                    }
                });
            },
            error: function() {
                console.error('Erro ao carregar modelos do banco de dados');
                
                // Em caso de erro, usar apenas os modelos pré-definidos
                $('#padroes-results').empty();
                
                for (const [id, modelo] of Object.entries(modelos)) {
                    $('#padroes-results').append(`
                        <div class="padrao-item" data-id="${id}">
                            <div class="padrao-titulo">${modelo.titulo}</div>
                            <div class="padrao-tipo">Modelo pré-definido</div>
                        </div>
                    `);
                }
                
                // Adicionar evento de clique para os itens
                $('.padrao-item').click(function() {
                    const modeloId = $(this).data('id');
                    selecionarModelo(modeloId);
                });
            }
        });
    }

    // Função para buscar modelo específico do banco de dados
    function buscarModeloDoBanco(id) {
        $.ajax({
            url: `/buscar_modelo_laudo/${id}`,
            type: 'GET',
            success: function(response) {
                if (response && response.conteudo) {
                    preencherCamposComModelo(response.conteudo);
                } else {
                    alert('Erro ao carregar modelo: Conteúdo não encontrado');
                }
            },
            error: function() {
                alert('Erro ao carregar modelo do banco de dados');
            }
        });
    }

    // Função para selecionar um modelo pré-definido
    function selecionarModelo(modeloId) {
        if (modelos[modeloId]) {
            const modelo = modelos[modeloId];
            
            // Preencher os campos com o conteúdo do modelo
            preencherCamposComModelo(modelo.conteudo);
            
            // Mostrar notificação
            const notification = document.getElementById('save-notification');
            if (notification) {
                notification.textContent = `Modelo "${modelo.titulo}" aplicado com sucesso!`;
                notification.style.display = 'block';
                
                setTimeout(function() {
                    notification.style.display = 'none';
                }, 3000);
            }
        }
    }

    // Função para preencher os campos com o conteúdo do modelo
    function preencherCamposComModelo(conteudo) {
        // Dividir o conteúdo em seções
        const linhas = conteudo.split('\n');
        let resumo = '';
        let ventriculo_esquerdo = '';
        let ventriculo_direito = '';
        let valvas = '';
        let pericardio = '';
        let aorta = '';
        let conclusao = '';
        
        // Analisar o conteúdo para extrair as seções
        let secaoAtual = 'resumo';
        let conclusaoEncontrada = false;
        
        for (const linha of linhas) {
            const linhaLower = linha.toLowerCase();
            
            if (linha.trim() === '') continue;
            
            // Detectar seção de conclusão
            if (linhaLower.includes('conclus') || linhaLower.includes('conclusão') || linhaLower.includes('conclusões')) {
                secaoAtual = 'conclusao';
                conclusaoEncontrada = true;
                continue;
            }
            
            // Detectar outras seções
            if (!conclusaoEncontrada) {
                if (linhaLower.includes('ventrículo esquerdo') || linhaLower.includes('ve ') || linhaLower.includes(' ve')) {
                    secaoAtual = 'ventriculo_esquerdo';
                    ventriculo_esquerdo += linha + '\n';
                    continue;
                } else if (linhaLower.includes('ventrículo direito') || linhaLower.includes('vd ') || linhaLower.includes(' vd')) {
                    secaoAtual = 'ventriculo_direito';
                    ventriculo_direito += linha + '\n';
                    continue;
                } else if (linhaLower.includes('valva') || linhaLower.includes('valvas') || linhaLower.includes('mitral') || 
                           linhaLower.includes('aórtica') || linhaLower.includes('tricúspide') || linhaLower.includes('pulmonar')) {
                    secaoAtual = 'valvas';
                    valvas += linha + '\n';
                    continue;
                } else if (linhaLower.includes('pericárdio') || linhaLower.includes('pericardio')) {
                    secaoAtual = 'pericardio';
                    pericardio += linha + '\n';
                    continue;
                } else if (linhaLower.includes('aorta') || linhaLower.includes('arco aórtico')) {
                    secaoAtual = 'aorta';
                    aorta += linha + '\n';
                    continue;
                }
            }
            
            // Adicionar linha à seção atual
            if (secaoAtual === 'resumo') {
                resumo += linha + '\n';
            } else if (secaoAtual === 'ventriculo_esquerdo') {
                ventriculo_esquerdo += linha + '\n';
            } else if (secaoAtual === 'ventriculo_direito') {
                ventriculo_direito += linha + '\n';
            } else if (secaoAtual === 'valvas') {
                valvas += linha + '\n';
            } else if (secaoAtual === 'pericardio') {
                pericardio += linha + '\n';
            } else if (secaoAtual === 'aorta') {
                aorta += linha + '\n';
            } else if (secaoAtual === 'conclusao') {
                conclusao += linha + '\n';
            }
        }
        
        // Se não encontrou seções específicas, colocar todo o conteúdo no resumo
        if (ventriculo_esquerdo === '' && ventriculo_direito === '' && valvas === '' && 
            pericardio === '' && aorta === '' && !conclusaoEncontrada) {
            resumo = conteudo;
        }
        
        // Preencher os campos do formulário
        $('#resumo_exame').val(resumo.trim());
        $('#ventriculo_esquerdo').val(ventriculo_esquerdo.trim());
        $('#ventriculo_direito').val(ventriculo_direito.trim());
        $('#valvas').val(valvas.trim());
        $('#pericardio').val(pericardio.trim());
        $('#aorta').val(aorta.trim());
        $('#conclusao').val(conclusao.trim());
        
        // Atualizar visualização prévia
        atualizarPreview();
        
        // Fechar a lista de resultados
        $('#padroes-results').hide();
    }
    
    // Função para atualizar a visualização prévia
    function atualizarPreview() {
        const resumo = $('#resumo_exame').val();
        const ventriculoEsquerdo = $('#ventriculo_esquerdo').val();
        const ventriculoDireito = $('#ventriculo_direito').val();
        const valvas = $('#valvas').val();
        const pericardio = $('#pericardio').val();
        const aorta = $('#aorta').val();
        const conclusao = $('#conclusao').val();
        
        // Construir o texto completo dos achados
        let achadosCompleto = '';
        if (ventriculoEsquerdo) achadosCompleto += ventriculoEsquerdo + '\n\n';
        if (ventriculoDireito) achadosCompleto += ventriculoDireito + '\n\n';
        if (valvas) achadosCompleto += valvas + '\n\n';
        if (pericardio) achadosCompleto += pericardio + '\n\n';
        if (aorta) achadosCompleto += aorta + '\n\n';
        
        // Atualizar os campos de preview
        $('#preview-resumo').text(resumo || 'Sem resumo disponível');
        $('#preview-achados').text(achadosCompleto || 'Sem achados disponíveis');
        $('#preview-conclusao').text(conclusao || 'Sem conclusão disponível');
        
        // Atualizar o campo oculto de achados ecocardiográficos para salvar no banco
        $('#achados_ecocardiograficos').val(achadosCompleto);
    }
    
    // Função para pesquisar modelos
    function pesquisarModelos(termo) {
        $.ajax({
            url: '/buscar_modelo_laudo',
            type: 'GET',
            data: { termo: termo },
            success: function(response) {
                // Limpar resultados anteriores
                $('#padroes-results').empty();
                
                // Filtrar modelos pré-definidos
                const modelosFiltrados = {};
                for (const [id, modelo] of Object.entries(modelos)) {
                    if (modelo.titulo.toLowerCase().includes(termo.toLowerCase()) || 
                        modelo.conteudo.toLowerCase().includes(termo.toLowerCase())) {
                        modelosFiltrados[id] = modelo;
                    }
                }
                
                // Adicionar modelos do banco de dados que correspondem ao termo
                if (response && response.length > 0) {
                    response.forEach(function(modelo) {
                        $('#padroes-results').append(`
                            <div class="padrao-item" data-id="db_${modelo.id}" data-conteudo="${encodeURIComponent(modelo.conteudo)}">
                                <div class="padrao-titulo">${modelo.nome}</div>
                                <div class="padrao-tipo">Modelo do banco</div>
                            </div>
                        `);
                    });
                }
                
                // Adicionar modelos pré-definidos filtrados
                for (const [id, modelo] of Object.entries(modelosFiltrados)) {
                    $('#padroes-results').append(`
                        <div class="padrao-item" data-id="${id}">
                            <div class="padrao-titulo">${modelo.titulo}</div>
                            <div class="padrao-tipo">Modelo pré-definido</div>
                        </div>
                    `);
                }
                
                // Se não houver resultados
                if ($('#padroes-results').children().length === 0) {
                    $('#padroes-results').append(`
                        <div class="padrao-item">
                            <div class="padrao-titulo">Nenhum resultado encontrado</div>
                            <div class="padrao-tipo">Tente outros termos</div>
                        </div>
                    `);
                }
                
                // Adicionar evento de clique para os itens
                $('.padrao-item').click(function() {
                    const modeloId = $(this).data('id');
                    const conteudoEncoded = $(this).data('conteudo');
                    
                    if (modeloId && modeloId.startsWith('db_')) {
                        // É um modelo do banco de dados
                        const conteudo = conteudoEncoded ? decodeURIComponent(conteudoEncoded) : '';
                        if (conteudo) {
                            preencherCamposComModelo(conteudo);
                        } else {
                            // Se não tiver o conteúdo no data attribute, buscar do servidor
                            const dbId = modeloId.replace('db_', '');
                            buscarModeloDoBanco(dbId);
                        }
                    } else if (modeloId) {
                        // É um modelo pré-definido
                        selecionarModelo(modeloId);
                    }
                });
                
                // Mostrar resultados
                $('#padroes-results').show();
            },
            error: function() {
                console.error('Erro ao pesquisar modelos');
                
                // Em caso de erro, filtrar apenas os modelos pré-definidos
                $('#padroes-results').empty();
                
                const modelosFiltrados = {};
                for (const [id, modelo] of Object.entries(modelos)) {
                    if (modelo.titulo.toLowerCase().includes(termo.toLowerCase()) || 
                        modelo.conteudo.toLowerCase().includes(termo.toLowerCase())) {
                        modelosFiltrados[id] = modelo;
                    }
                }
                
                // Adicionar modelos pré-definidos filtrados
                for (const [id, modelo] of Object.entries(modelosFiltrados)) {
                    $('#padroes-results').append(`
                        <div class="padrao-item" data-id="${id}">
                            <div class="padrao-titulo">${modelo.titulo}</div>
                            <div class="padrao-tipo">Modelo pré-definido</div>
                        </div>
                    `);
                }
                
                // Se não houver resultados
                if ($('#padroes-results').children().length === 0) {
                    $('#padroes-results').append(`
                        <div class="padrao-item">
                            <div class="padrao-titulo">Nenhum resultado encontrado</div>
                            <div class="padrao-tipo">Tente outros termos</div>
                        </div>
                    `);
                }
                
                // Adicionar evento de clique para os itens
                $('.padrao-item').click(function() {
                    const modeloId = $(this).data('id');
                    if (modeloId) {
                        selecionarModelo(modeloId);
                    }
                });
                
                // Mostrar resultados
                $('#padroes-results').show();
            }
        });
    }
    
    // Inicializar eventos
    $(document).ready(function() {
        // Carregar modelos ao iniciar
        carregarModelosDoBanco();
        
        // Configurar pesquisa
        $('#padroes-search-btn').click(function() {
            const termo = $('#padroes-search-input').val().trim();
            pesquisarModelos(termo);
        });
        
        $('#padroes-search-input').keyup(function(event) {
            if (event.key === 'Enter') {
                const termo = $(this).val().trim();
                pesquisarModelos(termo);
            }
        });
        
        // Atualizar preview quando os campos são alterados
        $('#resumo_exame, #ventriculo_esquerdo, #ventriculo_direito, #valvas, #pericardio, #aorta, #conclusao').on('input', function() {
            atualizarPreview();
        });
    });
});
