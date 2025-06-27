"""
Gerador de PDF Futurista - Sistema de Ecocardiograma
Design moderno e inovador otimizado para impressão em tinta preta
"""

import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Frame
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, Polygon
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import black, white, Color
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.barcode import getCodes
from reportlab.graphics import renderPDF
from pytz import timezone
import io
import base64
from PIL import Image
import qrcode
import math

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FuturisticReportGenerator:
    """Gerador de relatórios médicos com design futurista"""
    
    def __init__(self):
        # Paleta de cores otimizada para impressão em preto
        self.colors = {
            'black': Color(0, 0, 0, 1),           # Preto principal
            'dark_gray': Color(0.2, 0.2, 0.2, 1), # Cinza escuro
            'medium_gray': Color(0.4, 0.4, 0.4, 1), # Cinza médio
            'light_gray': Color(0.7, 0.7, 0.7, 1), # Cinza claro
            'ultra_light': Color(0.9, 0.9, 0.9, 1), # Cinza ultra claro
            'white': Color(1, 1, 1, 1),           # Branco
        }
        
        # Configurar estilos futuristas
        self.styles = self._create_futuristic_styles()
        
        # Configurações da página
        self.page_width, self.page_height = A4
        self.margin = 20*mm
        
    def _create_futuristic_styles(self):
        """Criar estilos futuristas e modernos"""
        styles = {}
        
        # Título principal - futurista com mais impacto
        styles['FuturisticTitle'] = ParagraphStyle(
            'FuturisticTitle',
            fontName='Helvetica-Bold',
            fontSize=32,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=self.colors['black'],
            letterSpacing=4,
        )
        
        # Subtítulo institucional
        styles['InstitutionalSubtitle'] = ParagraphStyle(
            'InstitutionalSubtitle',
            fontName='Helvetica',
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=self.colors['medium_gray'],
            letterSpacing=1,
        )
        
        # Seção principal com design tech
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=18,
            alignment=TA_LEFT,
            textColor=self.colors['white'],
            letterSpacing=1.5,
            borderWidth=1,
            borderColor=self.colors['black'],
            borderPadding=10,
            backColor=self.colors['black'],
            leftIndent=5,
            rightIndent=5,
        )
        
        # Texto normal moderno
        styles['ModernBody'] = ParagraphStyle(
            'ModernBody',
            fontName='Helvetica',
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            textColor=self.colors['dark_gray'],
            lineSpacing=14,
        )
        
        # Conclusão destacada
        styles['ConclusionText'] = ParagraphStyle(
            'ConclusionText',
            fontName='Helvetica',
            fontSize=12,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            textColor=self.colors['black'],
            lineSpacing=16,
            leftIndent=5,
            rightIndent=5,
        )
        
        # Cabeçalho de dados
        styles['DataHeader'] = ParagraphStyle(
            'DataHeader',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=self.colors['black'],
            letterSpacing=0.5,
        )
        
        return styles

class FuturisticElement(Flowable):
    """Elementos gráficos futuristas avançados"""
    
    def __init__(self, width, height, element_type='hex_divider'):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.element_type = element_type
        
    def draw(self):
        canvas = self.canv
        
        if self.element_type == 'hex_divider':
            # Divisor hexagonal futurista
            self._draw_hex_divider(canvas)
            
        elif self.element_type == 'data_frame':
            # Frame de dados estilo HUD
            self._draw_data_frame(canvas)
            
        elif self.element_type == 'scan_line':
            # Linha de scan médico
            self._draw_scan_line(canvas)
            
        elif self.element_type == 'corner_bracket':
            # Cantos estilo interface tech
            self._draw_corner_brackets(canvas)
            
        elif self.element_type == 'grid_dots':
            # Grid de pontos de fundo
            self._draw_grid_dots(canvas)
    
    def _draw_hex_divider(self, canvas):
        """Desenhar divisor hexagonal"""
        canvas.setStrokeColor(Color(0.2, 0.2, 0.2, 1))
        canvas.setFillColor(Color(0.1, 0.1, 0.1, 1))
        canvas.setLineWidth(1)
        
        # Hexágonos pequenos como divisor
        hex_size = 8
        center_y = self.height / 2
        
        for i in range(5):
            x = 20 + i * 25
            self._draw_hexagon(canvas, x, center_y, hex_size)
            
        # Linha conectora
        canvas.setStrokeColor(Color(0.4, 0.4, 0.4, 1))
        canvas.setLineWidth(0.5)
        canvas.line(0, center_y, self.width, center_y)
    
    def _draw_data_frame(self, canvas):
        """Desenhar frame de dados estilo HUD"""
        canvas.setStrokeColor(Color(0.15, 0.15, 0.15, 1))
        canvas.setLineWidth(2)
        
        # Frame principal
        canvas.rect(0, 0, self.width, self.height, fill=0)
        
        # Cantos cortados
        corner_size = 10
        canvas.setFillColor(Color(1, 1, 1, 1))
        
        # Canto superior esquerdo cortado
        p1 = canvas.beginPath()
        p1.moveTo(0, self.height)
        p1.lineTo(corner_size, self.height)
        p1.lineTo(0, self.height - corner_size)
        p1.close()
        canvas.drawPath(p1, fill=1)
        
        # Canto inferior direito cortado
        p2 = canvas.beginPath()
        p2.moveTo(self.width, 0)
        p2.lineTo(self.width - corner_size, 0)
        p2.lineTo(self.width, corner_size)
        p2.close()
        canvas.drawPath(p2, fill=1)
        
        # Elementos decorativos
        canvas.setStrokeColor(Color(0.3, 0.3, 0.3, 1))
        canvas.setLineWidth(1)
        
        # Linhas internas
        canvas.line(15, self.height - 5, 40, self.height - 5)
        canvas.line(self.width - 40, 5, self.width - 15, 5)
    
    def _draw_scan_line(self, canvas):
        """Desenhar linha de scan médico"""
        canvas.setStrokeColor(Color(0.2, 0.2, 0.2, 1))
        canvas.setLineWidth(3)
        
        y = self.height / 2
        
        # Linha principal
        canvas.line(0, y, self.width, y)
        
        # Marcadores de scan
        for i in range(0, int(self.width), 30):
            canvas.setLineWidth(1)
            canvas.line(i, y - 3, i, y + 3)
            
        # Indicadores nas extremidades
        canvas.setFillColor(Color(0.15, 0.15, 0.15, 1))
        canvas.circle(0, y, 4, fill=1)
        canvas.circle(self.width, y, 4, fill=1)
    
    def _draw_corner_brackets(self, canvas):
        """Desenhar cantos estilo interface tech"""
        canvas.setStrokeColor(Color(0.2, 0.2, 0.2, 1))
        canvas.setLineWidth(2)
        
        bracket_size = 15
        
        # Canto superior esquerdo
        canvas.line(0, bracket_size, 0, 0)
        canvas.line(0, 0, bracket_size, 0)
        
        # Canto superior direito
        canvas.line(self.width - bracket_size, 0, self.width, 0)
        canvas.line(self.width, 0, self.width, bracket_size)
        
        # Canto inferior esquerdo
        canvas.line(0, self.height - bracket_size, 0, self.height)
        canvas.line(0, self.height, bracket_size, self.height)
        
        # Canto inferior direito
        canvas.line(self.width - bracket_size, self.height, self.width, self.height)
        canvas.line(self.width, self.height, self.width, self.height - bracket_size)
    
    def _draw_grid_dots(self, canvas):
        """Desenhar grid de pontos de fundo"""
        canvas.setFillColor(Color(0.85, 0.85, 0.85, 1))
        
        spacing = 15
        dot_size = 0.5
        
        for x in range(0, int(self.width), spacing):
            for y in range(0, int(self.height), spacing):
                canvas.circle(x, y, dot_size, fill=1)
    
    def _draw_hexagon(self, canvas, x, y, size):
        """Desenhar hexágono individual"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append((px, py))
        
        # Usar path para desenhar polígono
        p = canvas.beginPath()
        p.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            p.lineTo(px, py)
        p.close()
        canvas.drawPath(p, fill=1, stroke=1)

class ProgressBar(Flowable):
    """Barra de progresso para valores de referência"""
    
    def __init__(self, width, height, value, min_val, max_val, label=""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.label = label
    
    def draw(self):
        canvas = self.canv
        
        # Fundo da barra
        canvas.setFillColor(Color(0.9, 0.9, 0.9, 1))
        canvas.rect(0, 0, self.width, self.height, fill=1)
        
        # Calcular posição do valor
        if self.max_val > self.min_val:
            progress = (self.value - self.min_val) / (self.max_val - self.min_val)
            progress = max(0, min(1, progress))  # Limitar entre 0 e 1
            
            # Barra de progresso
            fill_width = self.width * progress
            
            # Cor baseada na posição (verde no meio, vermelho nas extremidades)
            if 0.3 <= progress <= 0.7:
                fill_color = Color(0.2, 0.2, 0.2, 1)  # Preto para valores normais
            else:
                fill_color = Color(0.5, 0.5, 0.5, 1)  # Cinza para valores alterados
                
            canvas.setFillColor(fill_color)
            canvas.rect(0, 0, fill_width, self.height, fill=1)
            
            # Marcador do valor
            canvas.setStrokeColor(Color(0, 0, 0, 1))
            canvas.setLineWidth(2)
            canvas.line(fill_width, 0, fill_width, self.height)
        
        # Bordas
        canvas.setStrokeColor(Color(0.3, 0.3, 0.3, 1))
        canvas.setLineWidth(1)
        canvas.rect(0, 0, self.width, self.height, fill=0)

class QRCodeElement(Flowable):
    """Elemento QR Code para acesso digital"""
    
    def __init__(self, data, size=50):
        Flowable.__init__(self)
        self.data = data
        self.size = size
        self.width = size
        self.height = size
    
    def draw(self):
        canvas = self.canv
        
        # Gerar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(self.data)
        qr.make(fit=True)
        
        # Converter para matriz de pontos
        matrix = qr.get_matrix()
        
        # Desenhar QR code
        canvas.setFillColor(Color(0, 0, 0, 1))
        
        cell_size = self.size / len(matrix)
        
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if cell:
                    x = j * cell_size
                    y = self.size - (i + 1) * cell_size
                    canvas.rect(x, y, cell_size, cell_size, fill=1)

class FuturisticEcoReportGenerator(FuturisticReportGenerator):
    """Gerador específico para relatórios de ecocardiograma futurista"""
    
    def generate_report(self, exame, medico_data):
        """Gerar relatório completo do exame"""
        try:
            # Nome do arquivo
            nome_paciente = exame.nome_paciente.replace(' ', '_').replace('/', '_')
            data_exame = exame.data_exame.replace('/', '')
            filename = f"laudo_eco_futuristic_{nome_paciente}_{data_exame}.pdf"
            
            # Diretório de saída
            output_dir = "/home/runner/workspace/generated_pdfs"
            os.makedirs(output_dir, exist_ok=True)
            
            pdf_path = os.path.join(output_dir, filename)
            
            logger.info(f"Iniciando geração de relatório futurista para {exame.nome_paciente}")
            
            # Criar documento
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin + 30*mm,
            )
            
            # Criar elementos do relatório
            story = self._build_futuristic_story(exame, medico_data)
            
            # Função de página personalizada
            def on_page(canvas, doc):
                self._draw_futuristic_page_template(canvas, doc, exame, medico_data)
            
            # Construir PDF
            doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
            
            # Obter tamanho do arquivo
            file_size = os.path.getsize(pdf_path)
            
            logger.info(f"Relatório futurista gerado: {pdf_path} ({file_size} bytes)")
            
            return pdf_path, file_size
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório futurista: {str(e)}")
            raise

    def _draw_futuristic_page_template(self, canvas, doc, exame, medico_data):
        """Desenhar template futurista da página"""
        canvas.saveState()
        
        # Dimensões da página
        width, height = A4
        
        # === CABEÇALHO FUTURISTA ===
        # Fundo do cabeçalho com gradiente simulado
        header_height = 80
        
        # Fundo principal do cabeçalho
        canvas.setFillColor(Color(0.15, 0.15, 0.15, 1))
        canvas.rect(0, height - header_height, width, header_height, fill=1)
        
        # Linha de acento superior
        canvas.setFillColor(Color(0, 0, 0, 1))
        canvas.rect(0, height - 8, width, 8, fill=1)
        
        # Elementos geométricos decorativos
        canvas.setFillColor(Color(0.4, 0.4, 0.4, 1))
        # Círculos decorativos
        for i in range(5):
            x = 30 + i * 40
            canvas.circle(x, height - 15, 2, fill=1)
        
        # Retângulos decorativos no canto direito
        for i in range(3):
            x = width - 50 - i * 15
            canvas.rect(x, height - 25, 10, 3, fill=1)
        
        # Texto do cabeçalho
        canvas.setFillColor(Color(1, 1, 1, 1))  # Branco
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(30, height - 45, "GRUPO VIDAH")
        
        canvas.setFont("Helvetica", 12)
        canvas.drawString(30, height - 62, "Sistema Avançado de Ecocardiograma")
        
        # Informações do lado direito
        canvas.setFont("Helvetica", 9)
        text_lines = [
            "R. XV de Novembro, 594 - Centro",
            "Ibitinga - SP, 14940-000",
            "Telefone: (16) 3342-4768"
        ]
        
        for i, line in enumerate(text_lines):
            canvas.drawRightString(width - 30, height - 30 - (i * 12), line)
        
        # === RODAPÉ FUTURISTA ===
        footer_height = 40
        
        # Fundo do rodapé
        canvas.setFillColor(Color(0.05, 0.05, 0.05, 1))
        canvas.rect(0, 0, width, footer_height, fill=1)
        
        # Linha de acento
        canvas.setFillColor(Color(0.3, 0.3, 0.3, 1))
        canvas.rect(0, footer_height - 2, width, 2, fill=1)
        
        # Elementos geométricos no rodapé
        canvas.setFillColor(Color(0.4, 0.4, 0.4, 1))
        for i in range(8):
            x = 50 + i * 80
            canvas.rect(x, 5, 30, 2, fill=1)
        
        # Texto do rodapé
        canvas.setFillColor(Color(0.7, 0.7, 0.7, 1))
        canvas.setFont("Helvetica", 8)
        
        # Data de geração
        brasilia_tz = timezone('America/Sao_Paulo')
        agora = datetime.now(brasilia_tz)
        data_geracao = agora.strftime("%d/%m/%Y às %H:%M")
        canvas.drawString(30, 15, f"Gerado em: {data_geracao}")
        
        # Número da página
        canvas.drawRightString(width - 30, 15, f"Página {doc.page} de {getattr(doc, 'numPages', 1)}")
        
        # === BORDAS DECORATIVAS ===
        # Linhas verticais decorativas
        canvas.setStrokeColor(Color(0.8, 0.8, 0.8, 1))
        canvas.setLineWidth(1)
        
        # Linha esquerda
        canvas.line(20, header_height + 20, 20, footer_height + 20)
        
        # Linha direita
        canvas.line(width - 20, header_height + 20, width - 20, footer_height + 20)
        
        canvas.restoreState()

    def _build_futuristic_story(self, exame, medico_data):
        """Construir conteúdo futurista do relatório"""
        story = []
        
        # Título principal futurista
        story.append(Spacer(1, 20))
        story.append(Paragraph("LAUDO DE ECOCARDIOGRAMA", self.styles['FuturisticTitle']))
        story.append(Paragraph("TRANSTORÁCICO", self.styles['InstitutionalSubtitle']))
        
        # Elemento decorativo futurista
        story.append(FuturisticElement(15*cm, 15*mm, 'hex_divider'))
        story.append(Spacer(1, 20))
        
        # === SEÇÃO DADOS DO PACIENTE ===
        story.append(Paragraph("◆ IDENTIFICAÇÃO DO PACIENTE", self.styles['SectionHeader']))
        
        # Card moderno de dados do paciente
        patient_data = self._create_futuristic_patient_card(exame)
        story.append(patient_data)
        story.append(Spacer(1, 20))
        
        # === DADOS ANTROPOMÉTRICOS E MEDIDAS ===
        if exame.parametros:
            story.append(Paragraph("◆ PARÂMETROS ANTROPOMÉTRICOS E ECOCARDIOGRÁFICOS", self.styles['SectionHeader']))
            story.append(Spacer(1, 10))
            
            # Tabela futurista de parâmetros
            params_table = self._create_futuristic_parameters_table(exame.parametros)
            if params_table:
                story.append(params_table)
                story.append(Spacer(1, 25))
        
        # Quebra de página para laudos
        story.append(PageBreak())
        
        # === SEÇÕES DO LAUDO ===
        if exame.laudos and len(exame.laudos) > 0:
            laudo = exame.laudos[0]
            
            # Modo M e Bidimensional
            story.append(Paragraph("◆ MODO M E BIDIMENSIONAL", self.styles['SectionHeader']))
            story.append(Spacer(1, 10))
            if laudo.modo_m_bidimensional and laudo.modo_m_bidimensional.strip():
                story.append(Paragraph(laudo.modo_m_bidimensional, self.styles['ModernBody']))
            else:
                story.append(Paragraph("Análise pendente de descrição detalhada.", self.styles['ModernBody']))
            story.append(Spacer(1, 20))
            
            # Doppler Convencional
            story.append(Paragraph("◆ DOPPLER CONVENCIONAL", self.styles['SectionHeader']))
            story.append(Spacer(1, 10))
            if laudo.doppler_convencional and laudo.doppler_convencional.strip():
                story.append(Paragraph(laudo.doppler_convencional, self.styles['ModernBody']))
            else:
                story.append(Paragraph("Avaliação Doppler pendente de análise.", self.styles['ModernBody']))
            story.append(Spacer(1, 20))
            
            # Doppler Tecidual
            story.append(Paragraph("◆ DOPPLER TECIDUAL", self.styles['SectionHeader']))
            story.append(Spacer(1, 10))
            if laudo.doppler_tecidual and laudo.doppler_tecidual.strip():
                story.append(Paragraph(laudo.doppler_tecidual, self.styles['ModernBody']))
            else:
                story.append(Paragraph("Estudo de Doppler tecidual pendente.", self.styles['ModernBody']))
            story.append(Spacer(1, 20))
            
            # Conclusão destacada
            story.append(FuturisticElement(15*cm, 8*mm, 'scan_line'))
            story.append(Spacer(1, 10))
            story.append(Paragraph("◆ CONCLUSÃO DIAGNÓSTICA", self.styles['SectionHeader']))
            story.append(Spacer(1, 10))
            if laudo.conclusao and laudo.conclusao.strip():
                story.append(Paragraph(laudo.conclusao, self.styles['ConclusionText']))
            else:
                story.append(Paragraph("Conclusão diagnóstica em análise.", self.styles['ConclusionText']))
            story.append(Spacer(1, 30))
        
        # === ASSINATURA MÉDICA ===
        signature_section = self._create_futuristic_signature(medico_data)
        story.append(signature_section)
        
        return story

    def _create_futuristic_patient_card(self, exame):
        """Criar card futurista com dados do paciente"""
        data = [
            ['PACIENTE', exame.nome_paciente],
            ['DATA DE NASCIMENTO', exame.data_nascimento],
            ['IDADE', f"{exame.idade} anos"],
            ['SEXO', exame.sexo],
            ['DATA DO EXAME', exame.data_exame],
            ['MÉDICO SOLICITANTE', exame.medico_solicitante or "Não informado"],
            ['TIPO DE ATENDIMENTO', exame.tipo_atendimento or "Particular"],
            ['INDICAÇÃO', exame.indicacao or "Avaliação ecocardiográfica"]
        ]
        
        table = Table(data, colWidths=[6*cm, 10*cm])
        
        table.setStyle(TableStyle([
            # Estilo futurista da tabela
            ('BACKGROUND', (0, 0), (0, -1), Color(0.1, 0.1, 0.1, 1)),  # Coluna esquerda escura
            ('BACKGROUND', (1, 0), (1, -1), Color(0.95, 0.95, 0.95, 1)),  # Coluna direita clara
            ('TEXTCOLOR', (0, 0), (0, -1), Color(1, 1, 1, 1)),  # Texto branco na coluna escura
            ('TEXTCOLOR', (1, 0), (1, -1), Color(0, 0, 0, 1)),  # Texto preto na coluna clara
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, Color(0.3, 0.3, 0.3, 1)),
        ]))
        
        return table

    def _create_futuristic_parameters_table(self, parametros):
        """Criar tabela futurista de parâmetros"""
        if not parametros:
            return None
            
        data = [['PARÂMETRO', 'VALOR', 'UNIDADE', 'REFERÊNCIA']]
        
        # Lista de parâmetros para exibir
        param_list = [
            ('peso', 'kg', '-'),
            ('altura', 'cm', '-'),
            ('superficie_corporal', 'm²', '1.5-2.0'),
            ('frequencia_cardiaca', 'bpm', '60-100'),
            ('atrio_esquerdo', 'mm', '27-38'),
            ('raiz_aorta', 'mm', '21-34'),
            ('relacao_atrio_esquerdo_aorta', '-', '<1.5'),
            ('diametro_diastolico_final_ve', 'mm', '35-56'),
            ('diametro_sistolico_final', 'mm', '21-40'),
            ('espessura_diastolica_septo', 'mm', '6-11'),
            ('espessura_diastolica_ppve', 'mm', '6-11'),
            ('percentual_encurtamento', '%', '25-45'),
            ('fracao_ejecao', '%', '≥55'),
            ('volume_diastolico_final', 'mL', '65-195'),
            ('volume_sistolico_final', 'mL', '22-58'),
            ('massa_ve', 'g', '67-162 (H), 55-141 (M)')
        ]
        
        # Adicionar dados existentes
        for param_name, unit, reference in param_list:
            value = getattr(parametros, param_name, None)
            if value is not None and value != '' and value != 0:
                # Formatar valor
                if isinstance(value, float):
                    value_str = f"{value:.1f}" if value != int(value) else str(int(value))
                else:
                    value_str = str(value)
                
                # Nome formatado do parâmetro
                param_display = {
                    'peso': 'Peso',
                    'altura': 'Altura',
                    'superficie_corporal': 'Superfície Corporal',
                    'frequencia_cardiaca': 'Frequência Cardíaca',
                    'atrio_esquerdo': 'Átrio Esquerdo',
                    'raiz_aorta': 'Raiz da Aorta',
                    'relacao_atrio_esquerdo_aorta': 'Relação AE/Ao',
                    'diametro_diastolico_final_ve': 'DDVE',
                    'diametro_sistolico_final': 'DSVE',
                    'espessura_diastolica_septo': 'Septo IV',
                    'espessura_diastolica_ppve': 'Parede Posterior',
                    'percentual_encurtamento': '% Encurtamento',
                    'fracao_ejecao': 'Fração de Ejeção',
                    'volume_diastolico_final': 'VDF (Teichholz)',
                    'volume_sistolico_final': 'VSF (Teichholz)',
                    'massa_ve': 'Massa VE'
                }.get(param_name, param_name.replace('_', ' ').title())
                
                data.append([param_display, value_str, unit, reference])
        
        if len(data) <= 1:
            return None
            
        table = Table(data, colWidths=[7*cm, 2.5*cm, 2*cm, 4.5*cm])
        
        # Estilo futurista da tabela
        table_style = [
            # Cabeçalho futurista
            ('BACKGROUND', (0, 0), (-1, 0), Color(0, 0, 0, 1)),
            ('TEXTCOLOR', (0, 0), (-1, 0), Color(1, 1, 1, 1)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corpo da tabela
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            
            # Bordas e preenchimento
            ('GRID', (0, 0), (-1, -1), 0.5, Color(0.4, 0.4, 0.4, 1)),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Alternância de cores nas linhas
        for i in range(2, len(data), 2):
            table_style.append(('BACKGROUND', (0, i), (-1, i), Color(0.95, 0.95, 0.95, 1)))
        
        table.setStyle(TableStyle(table_style))
        
        return table

    def _create_futuristic_signature(self, medico_data):
        """Criar seção futurista de assinatura médica"""
        elements = []
        
        # Elemento decorativo avançado
        elements.append(FuturisticElement(12*cm, 10*mm, 'corner_bracket'))
        elements.append(Spacer(1, 20))
        
        # Dados do médico
        medico_nome = medico_data.get('nome', 'Dr. Médico Responsável')
        medico_crm = medico_data.get('crm', 'CRM: XXXXX-XX')
        
        # Tabela de assinatura futurista
        signature_data = [
            ['MÉDICO RESPONSÁVEL', medico_nome],
            ['REGISTRO PROFISSIONAL', medico_crm],
            ['ASSINATURA DIGITAL', '___________________________']
        ]
        
        signature_table = Table(signature_data, colWidths=[5*cm, 9*cm])
        
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), Color(0.05, 0.05, 0.05, 1)),
            ('BACKGROUND', (1, 0), (1, -1), Color(0.98, 0.98, 0.98, 1)),
            ('TEXTCOLOR', (0, 0), (0, -1), Color(1, 1, 1, 1)),
            ('TEXTCOLOR', (1, 0), (1, -1), Color(0, 0, 0, 1)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, Color(0.2, 0.2, 0.2, 1)),
        ]))
        
        elements.append(signature_table)
        
        return KeepTogether(elements)