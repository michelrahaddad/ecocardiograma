"""
Sistema de Ecocardiograma - Grupo Vidah
Gerador de PDF para Laudos Médicos
"""

import os
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import Color, black, white, blue, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcocardiogramaPDFGenerator:
    """Gerador de PDF para laudos de ecocardiograma"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2*cm
        # Definir cores primeiro para usar nos estilos
        self.primary_color = Color(30/255, 64/255, 175/255)  # #1e40af - cor clara
        self.secondary_color = Color(96/255, 165/255, 250/255)  # #60a5fa - cor clara
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Criar estilos personalizados para o documento"""
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=self.primary_color,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.primary_color,
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para seções
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=white,
            backgroundColor=self.primary_color,
            spaceBefore=10,
            spaceAfter=8,
            leftIndent=5,
            rightIndent=5,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Estilo para dados do paciente
        styles.add(ParagraphStyle(
            name='PatientData',
            parent=styles['Normal'],
            fontSize=11,
            textColor=black,
            spaceBefore=5,
            spaceAfter=5,
            fontName='Helvetica'
        ))
        
        # Estilo para conclusão
        styles.add(ParagraphStyle(
            name='Conclusion',
            parent=styles['Normal'],
            fontSize=11,
            textColor=black,
            spaceBefore=10,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica-Bold',
            backgroundColor=Color(0.95, 0.95, 0.95)
        ))
        
        return styles
    
    def create_header_footer(self, canvas, doc):
        """Criar cabeçalho e rodapé personalizados"""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFillColor(self.primary_color)
        canvas.rect(0, self.height - 3*cm, self.width, 3*cm, fill=True, stroke=False)
        
        # Logo (simulado com texto por enquanto)
        canvas.setFillColor(white)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawCentredText(self.width/2, self.height - 1.5*cm, "GRUPO VIDAH")
        canvas.setFont('Helvetica', 12)
        canvas.drawCentredText(self.width/2, self.height - 2*cm, "Sistema de Ecocardiograma")
        
        # Rodapé
        canvas.setFillColor(grey)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(self.margin, 1*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(self.width - self.margin, 1*cm, f"Página {doc.page}")
        
        canvas.restoreState()
    
    def _create_patient_info_table(self, exame):
        """Criar tabela com informações do paciente"""
        data = [
            ['Paciente:', exame.nome_paciente],
            ['Data de Nascimento:', exame.data_nascimento],
            ['Idade:', f'{exame.idade} anos'],
            ['Sexo:', exame.sexo],
            ['Data do Exame:', exame.data_exame],
            ['Médico Solicitante:', exame.medico_solicitante or '-'],
            ['Tipo de Atendimento:', exame.tipo_atendimento or '-']
        ]
        
        if exame.indicacao:
            data.append(['Indicação:', exame.indicacao])
        
        table = Table(data, colWidths=[4*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), Color(0.9, 0.9, 0.9)),
            ('TEXTCOLOR', (0, 0), (0, -1), self.primary_color),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def _create_parameters_table(self, parametros):
        """Criar tabela com parâmetros ecocardiográficos"""
        if not parametros:
            return Paragraph("Parâmetros não disponíveis", self.styles['CustomNormal'])
        
        # Dados antropométricos
        anthro_data = [
            ['Parâmetro', 'Valor', 'Unidade', 'Referência'],
            ['Peso', f'{parametros.peso or "-"}', 'kg', '-'],
            ['Altura', f'{parametros.altura or "-"}', 'cm', '-'],
            ['Superfície Corporal', f'{parametros.superficie_corporal:.2f}' if parametros.superficie_corporal else '-', 'm²', '-'],
            ['Frequência Cardíaca', f'{parametros.frequencia_cardiaca or "-"}', 'bpm', '60-100']
        ]
        
        anthro_table = Table(anthro_data, colWidths=[5*cm, 3*cm, 2*cm, 3*cm])
        anthro_table.setStyle(self._get_table_style())
        
        # Medidas ecocardiográficas
        echo_data = [
            ['Parâmetro', 'Valor', 'Unidade', 'Referência'],
            ['Átrio Esquerdo', f'{parametros.atrio_esquerdo:.2f}' if parametros.atrio_esquerdo else '-', 'cm', '2,7-3,8'],
            ['Raiz da Aorta', f'{parametros.raiz_aorta:.2f}' if parametros.raiz_aorta else '-', 'cm', '2,1-3,4'],
            ['Relação AE/Ao', f'{parametros.relacao_atrio_esquerdo_aorta:.2f}' if parametros.relacao_atrio_esquerdo_aorta else '-', '-', '<1,5'],
            ['DDVE', f'{parametros.diametro_diastolico_final_ve:.2f}' if parametros.diametro_diastolico_final_ve else '-', 'cm', '3,5-5,6'],
            ['DSVE', f'{parametros.diametro_sistolico_final:.2f}' if parametros.diametro_sistolico_final else '-', 'cm', '2,1-4,0'],
            ['% Encurtamento', f'{parametros.percentual_encurtamento:.1f}' if parametros.percentual_encurtamento else '-', '%', '25-45'],
            ['Fração de Ejeção', f'{parametros.fracao_ejecao:.1f}' if parametros.fracao_ejecao else '-', '%', '≥55']
        ]
        
        echo_table = Table(echo_data, colWidths=[5*cm, 3*cm, 2*cm, 3*cm])
        echo_table.setStyle(self._get_table_style())
        
        return [anthro_table, Spacer(1, 10), echo_table]
    
    def _get_table_style(self):
        """Estilo padrão para tabelas"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALTERNATEBACKGROUND', (0, 1), (-1, -1), [white, Color(0.98, 0.98, 0.98)]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])
    
    def _create_signature_section(self, medico_selecionado):
        """Criar seção de assinatura médica"""
        elements = []
        
        if medico_selecionado and medico_selecionado.assinatura_data:
            try:
                # Decodificar assinatura base64
                signature_data = base64.b64decode(medico_selecionado.assinatura_data)
                signature_image = Image(io.BytesIO(signature_data), width=6*cm, height=3*cm)
                signature_image.hAlign = 'CENTER'
                elements.append(signature_image)
            except Exception as e:
                logger.warning(f"Erro ao processar assinatura: {e}")
                elements.append(Spacer(1, 3*cm))
        else:
            elements.append(Spacer(1, 3*cm))
        
        # Linha para assinatura
        signature_line = Table([['_' * 50]], colWidths=[8*cm])
        signature_line.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        signature_line.hAlign = 'CENTER'
        elements.append(signature_line)
        
        # Informações do médico
        if medico_selecionado:
            medico_info = f"Dr(a). {medico_selecionado.nome}<br/>{medico_selecionado.crm}"
        else:
            medico_info = "Michel Raineri Haddad<br/>CRM: 183299"
        
        medico_paragraph = Paragraph(medico_info, self.styles['CustomNormal'])
        medico_paragraph.alignment = TA_CENTER
        elements.append(medico_paragraph)
        
        return elements

def gerar_pdf_completo(exame, medico_selecionado=None):
    """Função principal para gerar PDF completo do exame"""
    try:
        # Criar diretório de saída se não existir
        output_dir = os.path.join(os.getcwd(), 'generated_pdfs')
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome do arquivo
        filename = f"laudo_eco_{exame.nome_paciente.replace(' ', '_')}_{exame.data_exame.replace('/', '')}.pdf"
        file_path = os.path.join(output_dir, filename)
        
        # Criar gerador de PDF
        generator = EcocardiogramaPDFGenerator()
        
        # Criar documento
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=generator.margin,
            leftMargin=generator.margin,
            topMargin=4*cm,
            bottomMargin=3*cm
        )
        
        # Construir conteúdo
        story = []
        
        # Título do documento
        story.append(Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", generator.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Informações do paciente
        story.append(Paragraph("DADOS DO PACIENTE", generator.styles['SectionTitle']))
        story.append(generator._create_patient_info_table(exame))
        story.append(Spacer(1, 20))
        
        # Dados antropométricos e parâmetros
        story.append(Paragraph("DADOS ANTROPOMÉTRICOS E MEDIDAS ECOCARDIOGRÁFICAS", generator.styles['SectionTitle']))
        parameters_content = generator._create_parameters_table(exame.parametros)
        if isinstance(parameters_content, list):
            story.extend(parameters_content)
        else:
            story.append(parameters_content)
        story.append(Spacer(1, 20))
        
        # Laudo médico
        if exame.laudos and len(exame.laudos) > 0:
            laudo = exame.laudos[0]
            
            if laudo.modo_m_bidimensional:
                story.append(Paragraph("MODO M E BIDIMENSIONAL", generator.styles['SectionTitle']))
                story.append(Paragraph(laudo.modo_m_bidimensional, generator.styles['CustomNormal']))
                story.append(Spacer(1, 10))
            
            if laudo.doppler_convencional:
                story.append(Paragraph("DOPPLER CONVENCIONAL", generator.styles['SectionTitle']))
                story.append(Paragraph(laudo.doppler_convencional, generator.styles['CustomNormal']))
                story.append(Spacer(1, 10))
            
            if laudo.doppler_tecidual:
                story.append(Paragraph("DOPPLER TECIDUAL", generator.styles['SectionTitle']))
                story.append(Paragraph(laudo.doppler_tecidual, generator.styles['CustomNormal']))
                story.append(Spacer(1, 10))
            
            if laudo.conclusao:
                story.append(Paragraph("CONCLUSÃO", generator.styles['SectionTitle']))
                story.append(Paragraph(laudo.conclusao, generator.styles['Conclusion']))
                story.append(Spacer(1, 10))
            
            if laudo.recomendacoes:
                story.append(Paragraph("RECOMENDAÇÕES", generator.styles['SectionTitle']))
                story.append(Paragraph(laudo.recomendacoes, generator.styles['CustomNormal']))
                story.append(Spacer(1, 20))
        
        # Assinatura médica
        story.append(Spacer(1, 30))
        signature_elements = generator._create_signature_section(medico_selecionado)
        story.extend(signature_elements)
        
        # Construir PDF
        doc.build(story, onFirstPage=generator.create_header_footer, onLaterPages=generator.create_header_footer)
        
        logger.info(f"PDF gerado com sucesso: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        raise

def gerar_pdf_simples(exame):
    """Gerar PDF simples apenas com dados básicos"""
    try:
        output_dir = os.path.join(os.getcwd(), 'generated_pdfs')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"relatorio_simples_{exame.nome_paciente.replace(' ', '_')}_{exame.data_exame.replace('/', '')}.pdf"
        file_path = os.path.join(output_dir, filename)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        story.append(Paragraph("RELATÓRIO DE ECOCARDIOGRAMA", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Dados básicos
        story.append(Paragraph(f"<b>Paciente:</b> {exame.nome_paciente}", styles['Normal']))
        story.append(Paragraph(f"<b>Data:</b> {exame.data_exame}", styles['Normal']))
        story.append(Paragraph(f"<b>Idade:</b> {exame.idade} anos", styles['Normal']))
        
        doc.build(story)
        return file_path
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF simples: {str(e)}")
        raise

# Função de conveniência para uso externo
def generate_exam_pdf(exame, medico=None, tipo='completo'):
    """Gerar PDF do exame conforme o tipo especificado"""
    if tipo == 'simples':
        return gerar_pdf_simples(exame)
    else:
        return gerar_pdf_completo(exame, medico)
