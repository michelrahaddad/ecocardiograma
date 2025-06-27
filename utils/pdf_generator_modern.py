"""
Gerador de PDF Moderno para Laudos Ecocardiográficos
Design profissional e elegante para impressão médica
"""

import os
import io
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, KeepTogether, Image, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ModernEcoReportGenerator:
    """Gerador moderno de relatórios ecocardiográficos"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 2*cm
        self.content_width = self.page_width - 2*self.margin
        
        # Cores modernas para medicina
        self.colors = {
            'primary': colors.Color(0.2, 0.4, 0.7, alpha=1),      # Azul médico
            'secondary': colors.Color(0.3, 0.6, 0.4, alpha=1),    # Verde médico
            'accent': colors.Color(0.8, 0.9, 1.0, alpha=1),       # Azul claro
            'text': colors.Color(0.2, 0.2, 0.3, alpha=1),         # Cinza escuro
            'light_gray': colors.Color(0.95, 0.95, 0.95, alpha=1), # Cinza claro
            'white': colors.white,
            'border': colors.Color(0.85, 0.85, 0.85, alpha=1)     # Cinza borda
        }
        
        self.styles = self._create_modern_styles()
        
    def _create_modern_styles(self):
        """Criar estilos modernos e profissionais"""
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            spaceBefore=20,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=self.colors['primary'],
            leftIndent=0,
            backColor=self.colors['accent'],
            borderPadding=(8, 4, 8, 4)
        ))
        
        # Estilo para texto normal
        styles.add(ParagraphStyle(
            name='ModernNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['text'],
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14
        ))
        
        # Estilo para dados do paciente
        styles.add(ParagraphStyle(
            name='PatientData',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.colors['text'],
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leftIndent=20
        ))
        
        # Estilo para conclusão
        styles.add(ParagraphStyle(
            name='Conclusion',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.colors['text'],
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=16,
            leftIndent=10,
            rightIndent=10
        ))
        
        return styles
    
    def _create_header_footer(self, canvas, doc, page_num, total_pages):
        """Criar cabeçalho e rodapé modernos"""
        canvas.saveState()
        
        # Cabeçalho moderno
        header_height = 80
        
        # Fundo do cabeçalho
        canvas.setFillColor(self.colors['primary'])
        canvas.rect(0, self.page_height - header_height, self.page_width, header_height, fill=1)
        
        # Logo e nome da instituição
        canvas.setFillColor(self.colors['white'])
        canvas.setFont('Helvetica-Bold', 20)
        canvas.drawString(self.margin, self.page_height - 35, "GRUPO VIDAH")
        
        canvas.setFont('Helvetica', 10)
        canvas.drawString(self.margin, self.page_height - 50, "Sistema de Ecocardiograma")
        
        # Endereço no cabeçalho
        canvas.setFont('Helvetica', 9)
        address_x = self.page_width - self.margin - 150
        canvas.drawRightString(self.page_width - self.margin, self.page_height - 25, 
                              "R. XV de Novembro, 594 - Centro")
        canvas.drawRightString(self.page_width - self.margin, self.page_height - 37, 
                              "Ibitinga - SP, 14940-000")
        canvas.drawRightString(self.page_width - self.margin, self.page_height - 49, 
                              "Telefone: (16) 3342-4768")
        
        # Linha separadora
        canvas.setStrokeColor(self.colors['secondary'])
        canvas.setLineWidth(2)
        canvas.line(self.margin, self.page_height - header_height - 5, 
                   self.page_width - self.margin, self.page_height - header_height - 5)
        
        # Rodapé moderno
        footer_y = 30
        
        # Linha separadora no rodapé
        canvas.setStrokeColor(self.colors['border'])
        canvas.setLineWidth(1)
        canvas.line(self.margin, footer_y + 15, self.page_width - self.margin, footer_y + 15)
        
        # Informações do rodapé
        canvas.setFillColor(self.colors['text'])
        canvas.setFont('Helvetica', 8)
        
        # Data de geração
        now = datetime.now()
        date_str = now.strftime("Gerado em: %d/%m/%Y às %H:%M")
        canvas.drawString(self.margin, footer_y, date_str)
        
        # Número da página
        canvas.drawRightString(self.page_width - self.margin, footer_y, 
                              f"Página {page_num} de {total_pages}")
        
        canvas.restoreState()
    
    def _create_patient_info_card(self, exame):
        """Criar cartão moderno com informações do paciente"""
        data = [
            ['Paciente:', exame.nome_paciente],
            ['Data de Nascimento:', exame.data_nascimento],
            ['Idade:', f"{exame.idade} anos"],
            ['Sexo:', 'Masculino' if exame.sexo == 'M' else 'Feminino'],
            ['Data do Exame:', exame.data_exame],
            ['Médico Solicitante:', exame.medico_solicitante or 'Não informado'],
            ['Tipo de Atendimento:', exame.tipo_atendimento or 'Não informado'],
            ['Indicação:', exame.indicacao or 'Não informada']
        ]
        
        table = Table(data, colWidths=[4*cm, 12*cm])
        table.setStyle(TableStyle([
            # Estilo geral
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['white']),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Labels em negrito
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),       # Valores normais
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Bordas modernas
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['primary']),
            
            # Alternância de cores
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('BACKGROUND', (0, 2), (-1, 2), self.colors['accent']),
            ('BACKGROUND', (0, 4), (-1, 4), self.colors['accent']),
            ('BACKGROUND', (0, 6), (-1, 6), self.colors['accent']),
            
            # Espaçamento interno
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_parameters_table(self, parametros, title, param_list):
        """Criar tabela moderna de parâmetros"""
        if not parametros:
            return None
            
        data = [['Parâmetro', 'Valor', 'Unidade', 'Referência']]
        
        # Adicionar dados dos parâmetros apenas se existirem
        for param_name, unit, reference in param_list:
            value = getattr(parametros, param_name, None)
            if value is not None and value != '' and value != 0:
                # Formatar valor
                if isinstance(value, float):
                    value_str = f"{value:.1f}" if value != int(value) else str(int(value))
                else:
                    value_str = str(value)
                
                # Formatar nome do parâmetro
                param_display_name = param_name.replace('_', ' ').replace('atrio esquerdo', 'Átrio Esquerdo').replace('raiz aorta', 'Raiz da Aorta')
                if 'diametro diastolico final ve' in param_name:
                    param_display_name = 'DDVE'
                elif 'diametro sistolico final' in param_name:
                    param_display_name = 'DSVE'
                elif 'espessura diastolica septo' in param_name:
                    param_display_name = 'Septo'
                elif 'espessura diastolica ppve' in param_name:
                    param_display_name = 'Parede Posterior'
                elif 'percentual encurtamento' in param_name:
                    param_display_name = '% Encurtamento'
                elif 'fracao ejecao' in param_name:
                    param_display_name = 'Fração de Ejeção'
                elif 'volume diastolico final' in param_name:
                    param_display_name = 'VDF (Teichholz)'
                elif 'volume sistolico final' in param_name:
                    param_display_name = 'VSF (Teichholz)'
                elif 'massa ve' in param_name:
                    param_display_name = 'Massa VE'
                elif 'relacao atrio esquerdo aorta' in param_name:
                    param_display_name = 'Relação AE/Ao'
                else:
                    param_display_name = param_name.replace('_', ' ').title()
                
                data.append([
                    param_display_name,
                    value_str,
                    unit,
                    reference
                ])
        
        if len(data) <= 1:  # Apenas cabeçalho ou vazio
            return None
            
        # Calcular altura das linhas dinamicamente
        num_rows = len(data)
        
        table = Table(data, colWidths=[6*cm, 3*cm, 2.5*cm, 4.5*cm])
        
        # Criar estilos de tabela dinamicamente
        table_style = [
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corpo da tabela
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Parâmetro
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Valor
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Unidade
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Referência
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['primary']),
            
            # Espaçamento
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Adicionar alternância de cores apenas para linhas que existem
        for i in range(2, num_rows, 2):  # Começar da linha 2 (índice 1 é cabeçalho)
            if i < num_rows:
                table_style.append(('BACKGROUND', (0, i), (-1, i), self.colors['light_gray']))
        
        table.setStyle(TableStyle(table_style))
        
        return table
    
    def _create_signature_section(self, medico_data):
        """Criar seção moderna de assinatura"""
        elements = []
        
        # Espaço antes da assinatura
        elements.append(Spacer(1, 30))
        
        # Linha para assinatura
        signature_table = Table([
            ['', ''],
            ['_' * 50, ''],
            [f"Dr(a). {medico_data.get('nome', 'Médico Responsável')}", ''],
            [f"CRM: {medico_data.get('crm', 'Não informado')}", '']
        ], colWidths=[10*cm, 6*cm])
        
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, 1), 12),  # Linha de assinatura
            ('FONTSIZE', (0, 2), (0, 3), 11),  # Nome e CRM
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(signature_table)
        
        # Data e local
        elements.append(Spacer(1, 20))
        now = datetime.now()
        date_location = Paragraph(
            f"<para align=center><b>São Paulo, {now.strftime('%d de %B de %Y')}</b></para>",
            self.styles['ModernNormal']
        )
        elements.append(date_location)
        
        return KeepTogether(elements)
    
    def generate_report(self, exame, medico_data=None, output_path=None):
        """Gerar relatório moderno de ecocardiograma"""
        logger.info(f"Iniciando geração de relatório moderno para {exame.nome_paciente}")
        
        if not output_path:
            filename = f"laudo_eco_{exame.nome_paciente.replace(' ', '_')}_{exame.data_exame.replace('/', '')}.pdf"
            output_dir = os.path.join(os.getcwd(), 'generated_pdfs')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
        
        # Criar documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin + 60,  # Espaço para cabeçalho
            bottomMargin=self.margin + 40  # Espaço para rodapé
        )
        
        # Elementos do documento
        story = []
        
        # Título principal
        title = Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", self.styles['ModernTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Seção de dados do paciente
        story.append(Paragraph("DADOS DO PACIENTE", self.styles['ModernSubtitle']))
        story.append(Spacer(1, 10))
        patient_card = self._create_patient_info_card(exame)
        story.append(patient_card)
        story.append(Spacer(1, 20))
        
        # Dados antropométricos e medidas ecocardiográficas (combinados)
        if exame.parametros:
            story.append(Paragraph("DADOS ANTROPOMÉTRICOS E MEDIDAS ECOCARDIOGRÁFICAS", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 10))
            
            # Combinar todos os parâmetros em uma única tabela, como no original
            all_params = [
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
            
            params_table = self._create_parameters_table(exame.parametros, "Parâmetros", all_params)
            if params_table:
                story.append(params_table)
                story.append(Spacer(1, 20))
        
        # Quebra de página se necessário
        story.append(PageBreak())
        
        # Seções do laudo - manter exatamente como no original
        if exame.laudos and len(exame.laudos) > 0:
            laudo = exame.laudos[0]
            
            # Modo M e Bidimensional - sempre incluir mesmo se vazio
            story.append(Paragraph("MODO M E BIDIMENSIONAL", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            if laudo.modo_m_bidimensional and laudo.modo_m_bidimensional.strip():
                story.append(Paragraph(laudo.modo_m_bidimensional, self.styles['ModernNormal']))
            else:
                story.append(Paragraph("&nbsp;", self.styles['ModernNormal']))  # Espaço em branco
            story.append(Spacer(1, 15))
            
            # Doppler Convencional - sempre incluir mesmo se vazio
            story.append(Paragraph("DOPPLER CONVENCIONAL", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            if laudo.doppler_convencional and laudo.doppler_convencional.strip():
                story.append(Paragraph(laudo.doppler_convencional, self.styles['ModernNormal']))
            else:
                story.append(Paragraph("&nbsp;", self.styles['ModernNormal']))  # Espaço em branco
            story.append(Spacer(1, 15))
            
            # Doppler Tecidual - sempre incluir mesmo se vazio
            story.append(Paragraph("DOPPLER TECIDUAL", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            if laudo.doppler_tecidual and laudo.doppler_tecidual.strip():
                story.append(Paragraph(laudo.doppler_tecidual, self.styles['ModernNormal']))
            else:
                story.append(Paragraph("&nbsp;", self.styles['ModernNormal']))  # Espaço em branco
            story.append(Spacer(1, 15))
            
            # Conclusão - sempre incluir mesmo se vazio
            story.append(Paragraph("CONCLUSÃO", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            if laudo.conclusao and laudo.conclusao.strip():
                story.append(Paragraph(laudo.conclusao, self.styles['Conclusion']))
            else:
                story.append(Paragraph("&nbsp;", self.styles['Conclusion']))  # Espaço em branco
            story.append(Spacer(1, 20))
        else:
            # Se não há laudo, criar seções vazias
            story.append(Paragraph("MODO M E BIDIMENSIONAL", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            story.append(Paragraph("&nbsp;", self.styles['ModernNormal']))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("DOPPLER CONVENCIONAL", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            story.append(Paragraph("&nbsp;", self.styles['ModernNormal']))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("DOPPLER TECIDUAL", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            story.append(Paragraph("&nbsp;", self.styles['ModernNormal']))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("CONCLUSÃO", self.styles['ModernSubtitle']))
            story.append(Spacer(1, 8))
            story.append(Paragraph("&nbsp;", self.styles['Conclusion']))
            story.append(Spacer(1, 20))
        
        # Assinatura do médico
        if medico_data:
            signature_section = self._create_signature_section(medico_data)
            story.append(signature_section)
        
        # Função de callback para cabeçalho e rodapé
        def on_page(canvas, doc):
            page_num = canvas.getPageNumber()
            total_pages = getattr(doc, 'page_count', 1)
            self._create_header_footer(canvas, doc, page_num, total_pages)
        
        # Construir PDF
        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
        
        # Calcular total de páginas (aproximado)
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        logger.info(f"Relatório moderno gerado: {output_path} ({file_size} bytes)")
        
        return output_path, file_size