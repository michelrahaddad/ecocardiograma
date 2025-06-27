$(document).ready(function() {
    // Função para salvar os dados automaticamente
    function salvarAutomaticamente() {
        const exameId = window.location.pathname.split('/').pop();
        const formData = {};
        
        // Coletar todos os valores dos campos do formulário
        $('#parametrosForm input').each(function() {
            const id = $(this).attr('id');
            const value = $(this).val();
            
            if (id && value !== '') {
                formData[id] = value;
            }
        });
        
        // Adicionar campos calculados que podem não estar no formulário
        if ($('#massa_ve').length && $('#massa_ve').val() !== '') {
            formData['massa_ve'] = $('#massa_ve').val();
        }
        if ($('#indice_massa_ve').length && $('#indice_massa_ve').val() !== '') {
            formData['indice_massa_ve'] = $('#indice_massa_ve').val();
        }
        if ($('#fracao_ejecao').length && $('#fracao_ejecao').val() !== '') {
            formData['fracao_ejecao'] = $('#fracao_ejecao').val();
        }
        if ($('#debito_cardiaco').length && $('#debito_cardiaco').val() !== '') {
            formData['debito_cardiaco'] = $('#debito_cardiaco').val();
        }
        if ($('#indice_cardiaco').length && $('#indice_cardiaco').val() !== '') {
            formData['indice_cardiaco'] = $('#indice_cardiaco').val();
        }
        if ($('#volume_atrio_esquerdo').length && $('#volume_atrio_esquerdo').val() !== '') {
            formData['volume_atrio_esquerdo'] = $('#volume_atrio_esquerdo').val();
        }
        if ($('#diametro_basal_vd').length && $('#diametro_basal_vd').val() !== '') {
            formData['diametro_basal_vd'] = $('#diametro_basal_vd').val();
        }
        
        // Mostrar indicador de salvamento
        $('#salvamento-status').html('<span class="text-warning">Salvando...</span>');
        
        // Enviar dados para o servidor
        $.ajax({
            url: `/salvar_parametros_ajax/${exameId}`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                console.log('Dados salvos automaticamente:', response);
                // Atualizar indicador de salvamento
                $('#salvamento-status').html('<span class="text-success">Salvo com sucesso!</span>');
                // Esconder o indicador após 3 segundos
                setTimeout(function() {
                    $('#salvamento-status').html('');
                }, 3000);
            },
            error: function(error) {
                console.error('Erro ao salvar dados automaticamente:', error);
                // Mostrar erro no indicador
                $('#salvamento-status').html('<span class="text-danger">Erro ao salvar!</span>');
            }
        });
    }
    
    // Adicionar indicador de status de salvamento ao formulário
    if ($('#parametrosForm').length) {
        $('#parametrosForm').append('<div id="salvamento-status" class="text-right mt-2"></div>');
    }
    
    // Configurar salvamento automático a cada 30 segundos
    setInterval(salvarAutomaticamente, 30000);
    
    // Salvar também quando houver mudanças nos campos
    let timeoutId;
    $('#parametrosForm input').on('change', function() {
        clearTimeout(timeoutId);
        // Mostrar indicador de salvamento pendente
        $('#salvamento-status').html('<span class="text-warning">Alterações pendentes...</span>');
        timeoutId = setTimeout(salvarAutomaticamente, 2000);
    });
    
    // Adicionar feedback visual para o usuário
    $('#parametrosForm').on('submit', function() {
        // Mostrar indicador de salvamento
        $('#salvamento-status').html('<span class="text-warning">Salvando...</span>');
    });
});
