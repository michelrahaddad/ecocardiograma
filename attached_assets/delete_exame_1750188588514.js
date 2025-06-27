// Script para gerenciar a exclusão de exames
document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal
    const modal = document.getElementById('delete-modal');
    const closeModal = document.querySelector('.close-modal');
    const cancelDelete = document.getElementById('cancel-delete');
    const confirmDelete = document.getElementById('confirm-delete');
    const deleteButtons = document.querySelectorAll('.delete-exam-btn');
    
    // Variável para armazenar o ID do exame a ser excluído
    let exameIdToDelete = null;
    
    // Função para abrir o modal
    function openModal(exameId, pacienteNome, exameData) {
        exameIdToDelete = exameId;
        
        // Preencher informações no modal
        document.getElementById('modal-paciente-nome').textContent = pacienteNome;
        document.getElementById('modal-exame-data').textContent = exameData;
        
        // Exibir o modal
        modal.style.display = 'block';
    }
    
    // Função para fechar o modal
    function closeModalFunc() {
        modal.style.display = 'none';
        exameIdToDelete = null;
    }
    
    // Adicionar evento de clique aos botões de exclusão
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const exameId = this.getAttribute('data-id');
            const pacienteNome = this.getAttribute('data-paciente');
            const exameData = this.getAttribute('data-data');
            
            openModal(exameId, pacienteNome, exameData);
        });
    });
    
    // Eventos para fechar o modal
    if (closeModal) {
        closeModal.addEventListener('click', closeModalFunc);
    }
    
    if (cancelDelete) {
        cancelDelete.addEventListener('click', closeModalFunc);
    }
    
    // Evento para confirmar a exclusão
    if (confirmDelete) {
        confirmDelete.addEventListener('click', function() {
            if (exameIdToDelete) {
                // Criar um formulário para enviar a solicitação POST
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/excluir_exame/${exameIdToDelete}`;
                document.body.appendChild(form);
                form.submit();
            }
        });
    }
    
    // Fechar o modal se o usuário clicar fora dele
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModalFunc();
        }
    });
});
