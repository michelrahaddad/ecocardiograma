// Script para gerenciar a integração da assinatura digital do médico no laudo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de laudo
    const assinaturaContainer = document.getElementById('signature-pad');
    if (!assinaturaContainer) return;
    
    // Buscar médico atual via AJAX
    fetch('/medico_atual')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.medico) {
                const medico = data.medico;
                
                // Preencher o campo de médico responsável
                const campoMedicoResponsavel = document.getElementById('medico_responsavel');
                if (campoMedicoResponsavel) {
                    campoMedicoResponsavel.value = medico.nome;
                }
                
                // Preencher o campo de CRM
                const campoCrmMedico = document.getElementById('crm_medico');
                if (campoCrmMedico) {
                    campoCrmMedico.value = `CRM: ${medico.crm}`;
                }
                
                // Preencher assinatura digital
                if (medico.assinatura_data) {
                    const signatureDataInput = document.getElementById('signature_data');
                    if (signatureDataInput) {
                        signatureDataInput.value = medico.assinatura_data;
                        
                        // Exibir a assinatura no canvas
                        const canvas = document.getElementById('signature-pad');
                        if (canvas) {
                            const ctx = canvas.getContext('2d');
                            const img = new Image();
                            img.onload = function() {
                                // Limpar o canvas primeiro
                                ctx.clearRect(0, 0, canvas.width, canvas.height);
                                // Desenhar a imagem
                                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                            };
                            img.src = medico.assinatura_data;
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Erro ao carregar dados do médico:', error);
        });
    
    // Botão para selecionar outro médico
    const btnSelecionarMedico = document.getElementById('btn-selecionar-medico');
    if (btnSelecionarMedico) {
        btnSelecionarMedico.addEventListener('click', function() {
            window.location.href = '/cadastro_medico';
        });
    }
});
