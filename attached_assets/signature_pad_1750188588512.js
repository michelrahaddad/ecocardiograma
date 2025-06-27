// Arquivo para gerenciar a funcionalidade de assinatura digital
// Reescrito para garantir compatibilidade total com mouse e touch em todos os dispositivos, incluindo MacBook

document.addEventListener('DOMContentLoaded', function() {
    // Elementos da assinatura
    const canvas = document.getElementById('signature-pad');
    const clearButton = document.getElementById('clear-signature');
    const signatureDataInput = document.getElementById('signature_data');
    
    // Verificar se os elementos existem na página
    if (!canvas || !clearButton || !signatureDataInput) {
        console.log('Elementos de assinatura não encontrados na página');
        return;
    }
    
    // Configuração do canvas para alta resolução
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);
    
    // Variáveis para controle do desenho
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    const ctx = canvas.getContext('2d');
    
    // Configuração do contexto para uma linha suave
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000000';
    
    // Limpar o canvas e o campo de dados
    function clearSignature() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        signatureDataInput.value = '';
    }
    
    // Iniciar o desenho
    function startDrawing(e) {
        isDrawing = true;
        
        // Obter as coordenadas corretas para mouse ou touch
        const rect = canvas.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
        const clientY = e.clientY || (e.touches && e.touches[0] ? e.touches[0].clientY : 0);
        
        lastX = (clientX - rect.left) * ratio;
        lastY = (clientY - rect.top) * ratio;
        
        // Iniciar um novo caminho
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        
        // Prevenir comportamento padrão para evitar scrolling em dispositivos touch
        e.preventDefault();
    }
    
    // Desenhar
    function draw(e) {
        if (!isDrawing) return;
        
        // Obter as coordenadas corretas para mouse ou touch
        const rect = canvas.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
        const clientY = e.clientY || (e.touches && e.touches[0] ? e.touches[0].clientY : 0);
        
        const currentX = (clientX - rect.left) * ratio;
        const currentY = (clientY - rect.top) * ratio;
        
        // Desenhar a linha
        ctx.lineTo(currentX, currentY);
        ctx.stroke();
        
        // Atualizar as últimas coordenadas
        lastX = currentX;
        lastY = currentY;
        
        // Prevenir comportamento padrão
        e.preventDefault();
    }
    
    // Finalizar o desenho
    function stopDrawing() {
        if (isDrawing) {
            isDrawing = false;
            
            // Salvar a assinatura como imagem base64
            const signatureData = canvas.toDataURL('image/png');
            signatureDataInput.value = signatureData;
            
            // Fechar o caminho
            ctx.closePath();
        }
    }
    
    // Eventos para mouse
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // Eventos para touch
    canvas.addEventListener('touchstart', startDrawing, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    canvas.addEventListener('touchend', stopDrawing, { passive: false });
    
    // Evento para limpar a assinatura
    clearButton.addEventListener('click', clearSignature);
    
    // Restaurar assinatura se já existir
    if (signatureDataInput.value) {
        const img = new Image();
        img.onload = function() {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = signatureDataInput.value;
    }
    
    // Ajustar o tamanho do canvas quando a janela for redimensionada
    window.addEventListener('resize', function() {
        // Salvar a assinatura atual
        const currentSignature = canvas.toDataURL('image/png');
        
        // Redimensionar o canvas
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        ctx.scale(ratio, ratio);
        
        // Restaurar configurações de contexto
        ctx.lineWidth = 2.5;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        ctx.strokeStyle = '#000000';
        
        // Restaurar a assinatura
        if (currentSignature) {
            const img = new Image();
            img.onload = function() {
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.src = currentSignature;
        }
    });
    
    // Inicialização adicional para dispositivos Apple
    if (/iPad|iPhone|iPod|Macintosh/.test(navigator.userAgent)) {
        // Ajustes específicos para dispositivos Apple
        canvas.style.touchAction = 'none';
        
        // Garantir que o canvas tenha foco ao tocar
        canvas.addEventListener('touchstart', function() {
            canvas.focus();
        }, { passive: false });
        
        // Ajustes específicos para MacBook
        if (/Macintosh/.test(navigator.userAgent)) {
            // Aumentar a espessura da linha para melhor visibilidade
            ctx.lineWidth = 3;
            
            // Ajustar a sensibilidade para trackpads
            canvas.addEventListener('mousemove', function(e) {
                if (isDrawing) {
                    e.preventDefault();
                }
            });
        }
    }
    
    console.log('Inicialização da assinatura digital concluída');
});
