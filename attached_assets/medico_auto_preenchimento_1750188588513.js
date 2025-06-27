/**
 * Script para implementar o preenchimento automático do nome do médico e assinatura digital
 * quando um médico é selecionado no sistema de ecocardiograma.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de laudo
    const signaturePad = document.getElementById('signature-pad');
    const medicoResponsavelInput = document.getElementById('medico_responsavel');
    const crmMedicoInput = document.getElementById('crm_medico');
    const signatureDataInput = document.getElementById('signature_data');
    
    if (signaturePad && medicoResponsavelInput && crmMedicoInput && signatureDataInput) {
        // Estamos na página de laudo, carregar dados do médico selecionado
        const medicoSelecionado = JSON.parse(localStorage.getItem('medicoSelecionado'));
        
        if (medicoSelecionado) {
            console.log('Médico selecionado encontrado:', medicoSelecionado);
            
            // Preencher o nome do médico (apenas o nome, sem CRM)
            medicoResponsavelInput.value = medicoSelecionado.nome;
            
            // Preencher o CRM do médico
            crmMedicoInput.value = 'CRM: ' + medicoSelecionado.crm;
            
            // Carregar a assinatura digital
            if (medicoSelecionado.assinatura_data) {
                signatureDataInput.value = medicoSelecionado.assinatura_data;
                
                // Exibir a assinatura no canvas
                const ctx = signaturePad.getContext('2d');
                const img = new Image();
                img.onload = function() {
                    ctx.clearRect(0, 0, signaturePad.width, signaturePad.height);
                    ctx.drawImage(img, 0, 0, signaturePad.width, signaturePad.height);
                };
                img.src = medicoSelecionado.assinatura_data;
            }
        }
    }
    
    // Verificar se estamos na página de formulário de exame
    const medicoUsuarioInput = document.getElementById('medico_usuario');
    
    if (medicoUsuarioInput) {
        // Estamos na página de formulário de exame, carregar dados do médico selecionado
        const medicoSelecionado = JSON.parse(localStorage.getItem('medicoSelecionado'));
        
        if (medicoSelecionado) {
            console.log('Médico selecionado encontrado para formulário:', medicoSelecionado);
            
            // Preencher o nome do médico (apenas o nome, sem CRM)
            medicoUsuarioInput.value = medicoSelecionado.nome;
        }
    }
});
