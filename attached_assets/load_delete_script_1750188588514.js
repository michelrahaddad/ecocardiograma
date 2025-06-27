// Script para incluir no index.html para carregar o script de exclusão
document.addEventListener('DOMContentLoaded', function() {
    // Carregar o script de exclusão de exames
    const script = document.createElement('script');
    script.src = "{{ url_for('static', filename='js/delete_exame.js') }}";
    document.body.appendChild(script);
});
