// Script para gerenciar o preenchimento automático dos dados do médico
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos em uma página que precisa dos dados do médico
    const medicoResponsavelField = document.getElementById('medico_responsavel');
    const crmMedicoField = document.getElementById('crm_medico');
    const signaturePad = document.getElementById('signature-pad');
    
    if (!medicoResponsavelField && !crmMedicoField && !signaturePad) {
        console.log('Campos de médico não encontrados na página');
        return;
    }
    
    // Buscar médico atual via AJAX
    fetch('/medico_atual')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.medico) {
                const medico = data.medico;
                
                // Preencher campos do médico automaticamente
                if (medicoResponsavelField) {
                    medicoResponsavelField.value = medico.nome;
                }
                
                if (crmMedicoField) {
                    crmMedicoField.value = `CRM: ${medico.crm}`;
                }
                
                // Preencher assinatura digital se o elemento existir
                if (signaturePad && medico.assinatura_data) {
                    const signatureDataInput = document.getElementById('signature_data');
                    if (signatureDataInput) {
                        signatureDataInput.value = medico.assinatura_data;
                        
                        // Exibir a assinatura no canvas
                        const canvas = document.getElementById('signature-pad');
                        if (canvas) {
                            const ctx = canvas.getContext('2d');
                            const img = new Image();
                            img.onload = function() {
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
});
