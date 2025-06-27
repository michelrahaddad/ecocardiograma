"""
Gerador Universal de PDF para Sistema de Ecocardiograma
Versão robusta e à prova de falhas para todos os casos de uso
"""

import os
import io
import base64
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import Color, black, white
from reportlab.platypus import Image

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalPDFGenerator:
    """Gerador universal à prova de falhas para PDFs de ecocardiograma"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 15*mm
        
        # Cores profissionais
        self.primary_color = Color(0.2, 0.4, 0.7, 1)  # Azul profissional
        self.secondary_color = Color(0.6, 0.8, 1.0, 1)  # Azul claro
        self.light_gray = Color(0.9, 0.9, 0.9, 1)
        self.dark_gray = Color(0.3, 0.3, 0.3, 1)
        
        # Estilos
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Criar estilos padronizados"""
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Title'],
            fontSize=16,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Seção
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=self.primary_color,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        styles.add(ParagraphStyle(
            name='NormalText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Nome do médico
        styles.add(ParagraphStyle(
            name='DoctorName',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def generate_pdf(self, exame, medico_data=None):
        """Gerar PDF universal com proteção contra todos os erros"""
        try:
            logger.info(f"🔄 Iniciando geração de PDF universal para: {exame.nome_paciente}")
            
            # Criar diretório
            pdf_dir = os.path.join(os.getcwd(), 'generated_pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Nome do arquivo
            data_formatada = datetime.now().strftime("%d%m%Y")
            nome_arquivo = f"laudo_eco_{exame.nome_paciente.replace(' ', '_')}_{data_formatada}.pdf"
            pdf_path = os.path.join(pdf_dir, nome_arquivo)
            
            # Criar documento
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Construir conteúdo
            story = []
            
            # 1. Cabeçalho
            story.extend(self._create_header())
            
            # 2. Dados do paciente (SEMPRE funciona)
            story.extend(self._create_patient_section(exame))
            
            # 3. Parâmetros (com proteção)
            if hasattr(exame, 'parametros') and exame.parametros:
                story.extend(self._create_parameters_section(exame.parametros))
            
            # 4. Laudos (com proteção)
            if hasattr(exame, 'laudos') and exame.laudos:
                story.extend(self._create_reports_section(exame.laudos))
            
            # 5. Assinatura (SEMPRE funciona)
            story.extend(self._create_signature_section(medico_data))
            
            # 6. Rodapé
            story.extend(self._create_footer())
            
            # Gerar PDF
            doc.build(story)
            
            # Verificar tamanho
            file_size = os.path.getsize(pdf_path)
            logger.info(f"✅ PDF universal gerado com sucesso: {pdf_path} ({file_size} bytes)")
            
            return pdf_path, file_size
            
        except Exception as e:
            logger.error(f"❌ Erro na geração universal de PDF: {e}")
            raise e
    
    def _create_header(self):
        """Criar cabeçalho padrão"""
        elements = []
        
        # Logo/Título principal
        elements.append(Paragraph("GRUPO VIDAH", self.styles['MainTitle']))
        elements.append(Paragraph("Sistema de Ecocardiograma", self.styles['NormalText']))
        elements.append(Spacer(1, 10))
        
        # Título do laudo
        elements.append(Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", self.styles['MainTitle']))
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_patient_section(self, exame):
        """Criar seção de dados do paciente (à prova de falhas)"""
        elements = []
        
        elements.append(Paragraph("DADOS DO PACIENTE", self.styles['SectionHeader']))
        
        # Dados básicos com proteção
        patient_data = []
        try:
            patient_data.append(['Nome:', getattr(exame, 'nome_paciente', 'Não informado')])
            patient_data.append(['Data de Nascimento:', getattr(exame, 'data_nascimento', 'Não informado')])
            patient_data.append(['Idade:', f"{getattr(exame, 'idade', 'N/A')} anos"])
            patient_data.append(['Sexo:', getattr(exame, 'sexo', 'Não informado')])
            patient_data.append(['Data do Exame:', getattr(exame, 'data_exame', 'Não informado')])
            patient_data.append(['Convênio:', getattr(exame, 'tipo_atendimento', 'Não informado')])
            
            if hasattr(exame, 'indicacao') and exame.indicacao:
                patient_data.append(['Indicação:', exame.indicacao])
                
        except Exception as e:
            logger.warning(f"Erro ao extrair dados do paciente: {e}")
            patient_data = [['Nome:', 'Erro na extração de dados']]
        
        # Criar tabela robusta
        if patient_data:
            try:
                patient_table = Table(patient_data, colWidths=[40*mm, 120*mm])
                patient_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TEXTCOLOR', (0, 0), (0, -1), self.primary_color),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(patient_table)
            except Exception as e:
                logger.error(f"Erro ao criar tabela de paciente: {e}")
                elements.append(Paragraph("Erro na formatação dos dados do paciente", self.styles['NormalText']))
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _create_parameters_section(self, parametros):
        """Criar seção de parâmetros (robusta)"""
        elements = []
        
        elements.append(Paragraph("DADOS ANTROPOMÉTRICOS E MEDIDAS ECOCARDIOGRÁFICAS", self.styles['SectionHeader']))
        
        try:
            # Dados antropométricos
            anthro_data = []
            if hasattr(parametros, 'peso') and parametros.peso:
                anthro_data.append(['Peso:', f"{parametros.peso} kg"])
            if hasattr(parametros, 'altura') and parametros.altura:
                anthro_data.append(['Altura:', f"{parametros.altura} m"])
            if hasattr(parametros, 'superficie_corporal') and parametros.superficie_corporal:
                anthro_data.append(['Superfície Corporal:', f"{parametros.superficie_corporal:.2f} m²"])
                
            if anthro_data:
                anthro_table = Table(anthro_data, colWidths=[40*mm, 40*mm])
                anthro_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                elements.append(anthro_table)
                elements.append(Spacer(1, 10))
            
            # Medidas principais
            main_measures = []
            if hasattr(parametros, 'atrio_esquerdo') and parametros.atrio_esquerdo:
                main_measures.append(['Átrio Esquerdo:', f"{parametros.atrio_esquerdo} mm"])
            if hasattr(parametros, 'diametro_diastolico_final_ve') and parametros.diametro_diastolico_final_ve:
                main_measures.append(['DDVE:', f"{parametros.diametro_diastolico_final_ve} mm"])
            if hasattr(parametros, 'fracao_ejecao') and parametros.fracao_ejecao:
                main_measures.append(['Fração de Ejeção:', f"{parametros.fracao_ejecao}%"])
                
            if main_measures:
                measures_table = Table(main_measures, colWidths=[50*mm, 40*mm])
                measures_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                elements.append(measures_table)
                
        except Exception as e:
            logger.error(f"Erro ao processar parâmetros: {e}")
            elements.append(Paragraph("Parâmetros ecocardiográficos em processamento", self.styles['NormalText']))
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _create_reports_section(self, laudos):
        """Criar seção de laudos (robusta)"""
        elements = []
        
        try:
            if laudos and len(laudos) > 0:
                laudo = laudos[0]
                
                # Modo M
                if hasattr(laudo, 'modo_m_bidimensional') and laudo.modo_m_bidimensional:
                    elements.append(Paragraph("MODO M E BIDIMENSIONAL", self.styles['SectionHeader']))
                    elements.append(Paragraph(laudo.modo_m_bidimensional, self.styles['NormalText']))
                    elements.append(Spacer(1, 10))
                
                # Doppler Convencional
                if hasattr(laudo, 'doppler_convencional') and laudo.doppler_convencional:
                    elements.append(Paragraph("DOPPLER CONVENCIONAL", self.styles['SectionHeader']))
                    elements.append(Paragraph(laudo.doppler_convencional, self.styles['NormalText']))
                    elements.append(Spacer(1, 10))
                
                # Doppler Tecidual
                if hasattr(laudo, 'doppler_tecidual') and laudo.doppler_tecidual:
                    elements.append(Paragraph("DOPPLER TECIDUAL", self.styles['SectionHeader']))
                    elements.append(Paragraph(laudo.doppler_tecidual, self.styles['NormalText']))
                    elements.append(Spacer(1, 10))
                
                # Conclusão
                if hasattr(laudo, 'conclusao') and laudo.conclusao:
                    elements.append(Paragraph("CONCLUSÃO", self.styles['SectionHeader']))
                    elements.append(Paragraph(laudo.conclusao, self.styles['NormalText']))
                    elements.append(Spacer(1, 10))
                    
        except Exception as e:
            logger.error(f"Erro ao processar laudos: {e}")
            elements.append(Paragraph("Laudos médicos em elaboração", self.styles['NormalText']))
        
        return elements
    
    def _create_signature_section(self, medico_data):
        """Criar seção de assinatura (sempre funciona)"""
        elements = []
        
        elements.append(Spacer(1, 20))
        
        try:
            # Se há dados do médico
            if medico_data:
                medico_nome = medico_data.get('nome', 'Médico Responsável')
                medico_crm = medico_data.get('crm', 'CRM não informado')
                assinatura_data = medico_data.get('assinatura_data')
                
                # Tentar processar assinatura digital
                if assinatura_data:
                    try:
                        logger.info(f"Processando assinatura digital para {medico_nome}")
                        
                        # Processar base64
                        if assinatura_data.startswith('data:image/png;base64,'):
                            base64_data = assinatura_data.replace('data:image/png;base64,', '')
                        else:
                            base64_data = assinatura_data
                        
                        # Decodificar e criar imagem
                        image_data = base64.b64decode(base64_data)
                        image_stream = io.BytesIO(image_data)
                        
                        # Criar imagem para o PDF
                        signature_image = Image(image_stream, width=60*mm, height=25*mm)
                        signature_image.hAlign = 'CENTER'
                        
                        # Adicionar imagem
                        elements.append(signature_image)
                        elements.append(Spacer(1, 5))
                        
                        logger.info("✅ Assinatura digital processada com sucesso!")
                        
                    except Exception as e:
                        logger.warning(f"Erro ao processar assinatura digital: {e}")
                        # Fallback para linha de assinatura
                        elements.append(Spacer(1, 30))
                        elements.append(Paragraph("_" * 40, self.styles['NormalText']))
                        elements.append(Spacer(1, 5))
                else:
                    # Linha para assinatura manual
                    elements.append(Spacer(1, 30))
                    elements.append(Paragraph("_" * 40, self.styles['NormalText']))
                    elements.append(Spacer(1, 5))
                
                # Nome e CRM do médico
                elements.append(Paragraph(medico_nome, self.styles['DoctorName']))
                elements.append(Paragraph(medico_crm, self.styles['NormalText']))
                
            else:
                # Sem dados do médico
                elements.append(Spacer(1, 30))
                elements.append(Paragraph("_" * 40, self.styles['NormalText']))
                elements.append(Spacer(1, 5))
                elements.append(Paragraph("Médico Responsável", self.styles['DoctorName']))
                
        except Exception as e:
            logger.error(f"Erro na seção de assinatura: {e}")
            # Assinatura mínima de emergência
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("_" * 40, self.styles['NormalText']))
            elements.append(Paragraph("Médico Responsável", self.styles['DoctorName']))
        
        return elements
    
    def _create_footer(self):
        """Criar rodapé padrão"""
        elements = []
        
        elements.append(Spacer(1, 20))
        
        # Linha separadora
        elements.append(Paragraph("_" * 80, self.styles['NormalText']))
        elements.append(Spacer(1, 5))
        
        # Informações do Grupo Vidah
        footer_text = """
        <para align="center">
        <b>GRUPO VIDAH</b><br/>
        R. XV de Novembro, 594 - Centro, Ibitinga - SP, 14940-000<br/>
        Telefone: (16) 3342-4768 | Email: contato@grupovidah.com.br
        </para>
        """
        
        elements.append(Paragraph(footer_text, self.styles['NormalText']))
        
        return elements


# Função principal para geração de PDF
def gerar_pdf_universal(exame, medico_data=None):
    """Função principal para gerar PDF universal"""
    try:
        generator = UniversalPDFGenerator()
        return generator.generate_pdf(exame, medico_data)
    except Exception as e:
        logger.error(f"Erro crítico na geração de PDF: {e}")
        raise e