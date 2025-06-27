/**
 * Sistema de Ecocardiograma - Grupo Vidah
 * Gerenciamento de Assinatura Digital
 */

class SignaturePadManager {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.isDrawing = false;
        this.hasSignature = false;
        this.strokes = [];
        this.currentStroke = [];
        
        // Configurações padrão
        this.options = {
            penColor: options.penColor || '#000000',
            penWidth: options.penWidth || 2,
            backgroundColor: options.backgroundColor || '#ffffff',
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.attachEvents();
        this.clear();
    }
    
    setupCanvas() {
        // Configurar tamanho do canvas
        const rect = this.canvas.getBoundingClientRect();
        const devicePixelRatio = window.devicePixelRatio || 1;
        
        this.canvas.width = rect.width * devicePixelRatio;
        this.canvas.height = rect.height * devicePixelRatio;
        
        this.ctx.scale(devicePixelRatio, devicePixelRatio);
        
        // Configurar estilo do contexto
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.strokeStyle = this.options.penColor;
        this.ctx.lineWidth = this.options.penWidth;
        
        // Estilo do canvas
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
    }
    
    attachEvents() {
        // Eventos de mouse
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('mouseleave', this.handleMouseUp.bind(this));
        
        // Eventos de toque (mobile)
        this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this));
        this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this));
        this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this));
        
        // Prevenir scroll em mobile
        this.canvas.addEventListener('touchstart', e => e.preventDefault());
        this.canvas.addEventListener('touchmove', e => e.preventDefault());
        
        // Redimensionamento da janela
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    getEventPos(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        let clientX, clientY;
        
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX;
            clientY = e.clientY;
        }
        
        return {
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY
        };
    }
    
    startDrawing(pos) {
        this.isDrawing = true;
        this.currentStroke = [pos];
        this.ctx.beginPath();
        this.ctx.moveTo(pos.x, pos.y);
    }
    
    draw(pos) {
        if (!this.isDrawing) return;
        
        this.currentStroke.push(pos);
        this.ctx.lineTo(pos.x, pos.y);
        this.ctx.stroke();
        this.hasSignature = true;
    }
    
    stopDrawing() {
        if (!this.isDrawing) return;
        
        this.isDrawing = false;
        
        if (this.currentStroke.length > 0) {
            this.strokes.push([...this.currentStroke]);
            this.currentStroke = [];
        }
        
        this.ctx.beginPath();
        this.triggerChange();
    }
    
    // Eventos de mouse
    handleMouseDown(e) {
        const pos = this.getEventPos(e);
        this.startDrawing(pos);
    }
    
    handleMouseMove(e) {
        const pos = this.getEventPos(e);
        this.draw(pos);
    }
    
    handleMouseUp(e) {
        this.stopDrawing();
    }
    
    // Eventos de toque
    handleTouchStart(e) {
        const pos = this.getEventPos(e);
        this.startDrawing(pos);
    }
    
    handleTouchMove(e) {
        const pos = this.getEventPos(e);
        this.draw(pos);
    }
    
    handleTouchEnd(e) {
        this.stopDrawing();
    }
    
    handleResize() {
        // Salvar assinatura atual
        const imageData = this.hasSignature ? this.toDataURL() : null;
        
        // Reconfigurar canvas
        this.setupCanvas();
        
        // Restaurar assinatura se existia
        if (imageData) {
            this.fromDataURL(imageData);
        }
    }
    
    clear() {
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.strokes = [];
        this.currentStroke = [];
        this.hasSignature = false;
        this.triggerChange();
    }
    
    undo() {
        if (this.strokes.length === 0) return;
        
        this.strokes.pop();
        this.redraw();
        this.triggerChange();
    }
    
    redraw() {
        this.clear();
        
        this.strokes.forEach(stroke => {
            if (stroke.length === 0) return;
            
            this.ctx.beginPath();
            this.ctx.moveTo(stroke[0].x, stroke[0].y);
            
            stroke.forEach((point, index) => {
                if (index > 0) {
                    this.ctx.lineTo(point.x, point.y);
                }
            });
            
            this.ctx.stroke();
        });
        
        this.hasSignature = this.strokes.length > 0;
    }
    
    isEmpty() {
        return !this.hasSignature;
    }
    
    toDataURL(type = 'image/png', quality = 1.0) {
        return this.canvas.toDataURL(type, quality);
    }
    
    toBlob(callback, type = 'image/png', quality = 1.0) {
        this.canvas.toBlob(callback, type, quality);
    }
    
    fromDataURL(dataURL) {
        const img = new Image();
        img.onload = () => {
            this.clear();
            this.ctx.drawImage(img, 0, 0);
            this.hasSignature = true;
            this.triggerChange();
        };
        img.src = dataURL;
    }
    
    getImageData() {
        return this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    }
    
    putImageData(imageData) {
        this.ctx.putImageData(imageData, 0, 0);
        this.hasSignature = true;
        this.triggerChange();
    }
    
    // Configurar cor da caneta
    setPenColor(color) {
        this.options.penColor = color;
        this.ctx.strokeStyle = color;
    }
    
    // Configurar largura da caneta
    setPenWidth(width) {
        this.options.penWidth = width;
        this.ctx.lineWidth = width;
    }
    
    // Configurar cor de fundo
    setBackgroundColor(color) {
        this.options.backgroundColor = color;
        this.redraw();
    }
    
    // Eventos personalizados
    triggerChange() {
        const event = new CustomEvent('signaturechange', {
            detail: {
                isEmpty: this.isEmpty(),
                dataURL: this.hasSignature ? this.toDataURL() : null
            }
        });
        this.canvas.dispatchEvent(event);
    }
    
    // Adicionar listener para mudanças na assinatura
    onChange(callback) {
        this.canvas.addEventListener('signaturechange', callback);
    }
    
    // Remover listener
    offChange(callback) {
        this.canvas.removeEventListener('signaturechange', callback);
    }
    
    // Exportar para base64 (sem prefixo data:image/png;base64,)
    toBase64() {
        const dataURL = this.toDataURL();
        return dataURL.split(',')[1];
    }
    
    // Importar de base64
    fromBase64(base64) {
        const dataURL = 'data:image/png;base64,' + base64;
        this.fromDataURL(dataURL);
    }
    
    // Validar se a assinatura tem conteúdo suficiente
    isValid() {
        if (!this.hasSignature) return false;
        
        // Verificar se há pelo menos alguns pontos desenhados
        const totalPoints = this.strokes.reduce((total, stroke) => total + stroke.length, 0);
        return totalPoints >= 10; // Mínimo de 10 pontos
    }
    
    // Obter informações da assinatura
    getSignatureInfo() {
        return {
            isEmpty: this.isEmpty(),
            isValid: this.isValid(),
            strokeCount: this.strokes.length,
            totalPoints: this.strokes.reduce((total, stroke) => total + stroke.length, 0),
            dimensions: {
                width: this.canvas.width,
                height: this.canvas.height
            }
        };
    }
    
    // Destruir o signature pad
    destroy() {
        // Remover todos os event listeners
        this.canvas.removeEventListener('mousedown', this.handleMouseDown);
        this.canvas.removeEventListener('mousemove', this.handleMouseMove);
        this.canvas.removeEventListener('mouseup', this.handleMouseUp);
        this.canvas.removeEventListener('mouseleave', this.handleMouseUp);
        this.canvas.removeEventListener('touchstart', this.handleTouchStart);
        this.canvas.removeEventListener('touchmove', this.handleTouchMove);
        this.canvas.removeEventListener('touchend', this.handleTouchEnd);
        window.removeEventListener('resize', this.handleResize);
        
        // Limpar canvas
        this.clear();
        
        // Limpar referências
        this.canvas = null;
        this.ctx = null;
        this.strokes = null;
        this.currentStroke = null;
    }
}

// Função de conveniência para inicializar um signature pad
function initializeSignaturePad(canvasId, options = {}) {
    return new SignaturePadManager(canvasId, options);
}

// Função para redimensionar canvas automaticamente
function autoResizeCanvas(canvas) {
    const observer = new ResizeObserver(entries => {
        for (let entry of entries) {
            const { width, height } = entry.contentRect;
            const devicePixelRatio = window.devicePixelRatio || 1;
            
            canvas.width = width * devicePixelRatio;
            canvas.height = height * devicePixelRatio;
            
            const ctx = canvas.getContext('2d');
            ctx.scale(devicePixelRatio, devicePixelRatio);
            
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';
        }
    });
    
    observer.observe(canvas);
    return observer;
}

// Função para validar assinatura
function validateSignature(signaturePad, options = {}) {
    const defaultOptions = {
        minStrokes: 1,
        minPoints: 10,
        showAlert: true,
        alertMessage: 'Por favor, adicione uma assinatura válida.'
    };
    
    const config = { ...defaultOptions, ...options };
    const info = signaturePad.getSignatureInfo();
    
    const isValid = !info.isEmpty && 
                   info.strokeCount >= config.minStrokes && 
                   info.totalPoints >= config.minPoints;
    
    if (!isValid && config.showAlert) {
        alert(config.alertMessage);
    }
    
    return isValid;
}

// Função para salvar assinatura
function saveSignature(signaturePad, format = 'base64') {
    if (signaturePad.isEmpty()) {
        throw new Error('Não há assinatura para salvar');
    }
    
    switch (format.toLowerCase()) {
        case 'base64':
            return signaturePad.toBase64();
        case 'dataurl':
            return signaturePad.toDataURL();
        case 'blob':
            return new Promise(resolve => {
                signaturePad.toBlob(resolve);
            });
        default:
            throw new Error('Formato não suportado: ' + format);
    }
}

// Função para carregar assinatura
function loadSignature(signaturePad, data, format = 'base64') {
    switch (format.toLowerCase()) {
        case 'base64':
            signaturePad.fromBase64(data);
            break;
        case 'dataurl':
            signaturePad.fromDataURL(data);
            break;
        default:
            throw new Error('Formato não suportado: ' + format);
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.SignaturePadManager = SignaturePadManager;
    window.initializeSignaturePad = initializeSignaturePad;
    window.autoResizeCanvas = autoResizeCanvas;
    window.validateSignature = validateSignature;
    window.saveSignature = saveSignature;
    window.loadSignature = loadSignature;
}

// Exportar para Node.js (se disponível)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SignaturePadManager,
        initializeSignaturePad,
        autoResizeCanvas,
        validateSignature,
        saveSignature,
        loadSignature
    };
}
