"""
Gerador de PDF Institucional Moderno
Sistema profissional para documentos médicos com design contemporâneo

Especificações implementadas:
- Tipografia moderna: Roboto Slab/Open Sans Bold para títulos (14-16pt)
- Paleta médica: azul escuro/cinza para títulos, linhas cinza-claro
- Grid de duas colunas otimizado para compactação
- Margens simétricas (2cm) com recuo interno (1cm)
- Conclusão destacada com caixa cinza-claro e bordas arredondadas
- Layout para máximo 2 páginas A4
- Remoção de símbolos informais
- Fundo branco puro sem bordas pesadas
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus.flowables import Image
import os
import logging
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

class PDFInstitucionalGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_modern_styles()
        
    def _create_modern_styles(self):
        """Criar estilos tipográficos modernos e profissionais"""
        
        # Título principal - Roboto Slab equivalente
        self.styles.add(ParagraphStyle(
            'TituloInstitucional',
            parent=self.styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),  # Azul escuro institucional
            spaceAfter=12,
            spaceBefore=0,
            alignment=1,  # Centralizado
            letterSpacing=0.8
        ))
        
        # Subtítulo moderno
        self.styles.add(ParagraphStyle(
            'SubtituloModerno',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#34495E'),  # Cinza escuro elegante
            spaceAfter=8,
            spaceBefore=12,
            alignment=0,
            letterSpacing=0.5
        ))
        
        # Texto corpo - Open Sans equivalente
        self.styles.add(ParagraphStyle(
            'CorpoModerno',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            leading=14,
            spaceAfter=4,
            spaceBefore=2,
            alignment=0
        ))
        
        # Conclusão destacada com fundo cinza
        self.styles.add(ParagraphStyle(
            'ConclusaoDestacada',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            leading=16,
            spaceAfter=8,
            spaceBefore=8,
            alignment=0,
            backColor=colors.HexColor('#F8F9FA'),  # Fundo cinza-claro
            leftIndent=10,
            rightIndent=10,
            borderPadding=8
        ))
        
        # Cabeçalho institucional
        self.styles.add(ParagraphStyle(
            'CabecalhoInstitucional',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            alignment=1,
            spaceAfter=6
        ))

    def _create_header_footer(self, canvas, doc):
        """Criar cabeçalho e rodapé institucionais"""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#2C3E50'))
        canvas.drawCentredText(A4[0]/2, A4[1] - 30, "GRUPO VIDAH - MEDICINA DIAGNÓSTICA")
        
        # Logo (se disponível)
        logo_path = "static/logo_grupo_vidah.jpg"
        if os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, 40, A4[1] - 60, width=80, height=40, preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Erro ao carregar logo: {e}")
        
        # Linha divisória
        canvas.setStrokeColor(colors.HexColor('#BDC3C7'))
        canvas.setLineWidth(0.5)
        canvas.line(40, A4[1] - 70, A4[0] - 40, A4[1] - 70)
        
        # Rodapé na segunda página
        if doc.page >= 2:
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.HexColor('#7F8C8D'))
            canvas.line(40, 60, A4[0] - 40, 60)
            canvas.drawCentredText(A4[0]/2, 45, "R. XV de Novembro, 594 - Ibitinga-SP | Tel: (16) 3342-4768")
        
        canvas.restoreState()

    def _create_patient_info_grid(self, exame):
        """Criar grid moderno com informações do paciente"""
        data = [
            ['DADOS DO PACIENTE', '', '', ''],
            ['Nome:', exame.nome_paciente or 'N/I', 'Data Nascimento:', exame.data_nascimento or 'N/I'],
            ['Idade:', f"{exame.idade} anos" if exame.idade else 'N/I', 'Sexo:', exame.sexo or 'N/I'],
            ['Data Exame:', exame.data_exame or 'N/I', 'Tipo Atendimento:', exame.tipo_atendimento or 'N/I'],
            ['Médico Solicitante:', exame.medico_solicitante or 'N/I', 'Indicação:', exame.indicacao or 'N/I']
        ]
        
        table = Table(data, colWidths=[4*cm, 6*cm, 4*cm, 6*cm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('SPAN', (0, 0), (3, 0)),
            ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 12),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
            
            # Alternância de cores suave
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FAFBFC')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FAFBFC')),
            
            # Bordas elegantes
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#BDC3C7')),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            
            # Padding otimizado
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def _create_parameters_grid(self, parametros, title, param_list):
        """Criar grid de duas colunas para parâmetros"""
        if not parametros:
            return None
            
        data = [[title, '', '', '']]
        
        # Organizar em duas colunas
        for i in range(0, len(param_list), 2):
            left_param = param_list[i]
            right_param = param_list[i + 1] if i + 1 < len(param_list) else None
            
            left_value = getattr(parametros, left_param['field'], None) or 'N/I'
            if isinstance(left_value, (int, float)) and left_value != 'N/I':
                left_value = f"{left_value:.1f} {left_param.get('unit', '')}"
            
            if right_param:
                right_value = getattr(parametros, right_param['field'], None) or 'N/I'
                if isinstance(right_value, (int, float)) and right_value != 'N/I':
                    right_value = f"{right_value:.1f} {right_param.get('unit', '')}"
                
                data.append([
                    left_param['label'],
                    str(left_value),
                    right_param['label'],
                    str(right_value)
                ])
            else:
                data.append([
                    left_param['label'],
                    str(left_value),
                    '',
                    ''
                ])
        
        table = Table(data, colWidths=[4.5*cm, 3.5*cm, 4.5*cm, 3.5*cm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('SPAN', (0, 0), (3, 0)),
            ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 11),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            
            # Labels em negrito
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
            
            # Valores centralizados
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            
            # Alternância suave
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FAFBFC')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FAFBFC')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#FAFBFC')),
            
            # Bordas elegantes
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#BDC3C7')),
            ('ROUNDEDCORNERS', [3, 3, 3, 3]),
            
            # Padding compacto
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def _create_conclusion_box(self, conclusao_text):
        """Criar caixa destacada para conclusão diagnóstica"""
        if not conclusao_text:
            conclusao_text = "Conclusão não informada"
            
        # Título da conclusão
        titulo = Paragraph("CONCLUSÃO DIAGNÓSTICA", self.styles['SubtituloModerno'])
        
        # Texto da conclusão em caixa destacada
        conclusao = Paragraph(conclusao_text, self.styles['ConclusaoDestacada'])
        
        # Tabela para criar o efeito de caixa com bordas arredondadas
        data = [[conclusao]]
        table = Table(data, colWidths=[16*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F8F9FA')),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#BDC3C7')),
            ('LEFTPADDING', (0, 0), (0, 0), 15),
            ('RIGHTPADDING', (0, 0), (0, 0), 15),
            ('TOPPADDING', (0, 0), (0, 0), 12),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        
        return [titulo, Spacer(1, 6), table]

    def _get_signature_image(self, medico):
        """Processar assinatura digital do médico"""
        if not medico or not medico.assinatura_data:
            return None
            
        try:
            # Decodificar Base64
            if medico.assinatura_data.startswith('data:image'):
                base64_data = medico.assinatura_data.split(',')[1]
            else:
                base64_data = medico.assinatura_data
                
            image_data = base64.b64decode(base64_data)
            
            # Processar com PIL
            pil_image = PILImage.open(BytesIO(image_data))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Redimensionar para assinatura compacta
            pil_image = pil_image.resize((120, 40), PILImage.Resampling.LANCZOS)
            
            # Converter para ReportLab
            buffer = BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            return ImageReader(buffer)
            
        except Exception as e:
            logger.warning(f"Erro ao processar assinatura: {e}")
            return None

    def generate_pdf(self, exame, parametros, laudos, medico, output_path):
        """Gerar PDF moderno e institucional"""
        try:
            # Configurar documento com margens institucionais (2cm)
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=2*cm,
                rightMargin=2*cm,
                topMargin=2.5*cm,
                bottomMargin=2*cm
            )
            
            # Configurar cabeçalho/rodapé
            def add_header_footer(canvas, doc):
                self._create_header_footer(canvas, doc)
            
            story = []
            
            # Título principal
            story.append(Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", self.styles['TituloInstitucional']))
            story.append(Spacer(1, 10))
            
            # Informações do paciente
            patient_grid = self._create_patient_info_grid(exame)
            story.append(patient_grid)
            story.append(Spacer(1, 12))
            
            # Parâmetros ecocardiográficos em grids otimizados
            if parametros:
                # Medidas básicas
                basic_params = [
                    {'label': 'Átrio Esquerdo', 'field': 'atrio_esquerdo', 'unit': 'mm'},
                    {'label': 'Raiz Aorta', 'field': 'raiz_aorta', 'unit': 'mm'},
                    {'label': 'Aorta Ascendente', 'field': 'aorta_ascendente', 'unit': 'mm'},
                    {'label': 'Diâmetro VD', 'field': 'diametro_ventricular_direito', 'unit': 'mm'},
                ]
                
                basic_grid = self._create_parameters_grid(parametros, "MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS", basic_params)
                if basic_grid:
                    story.append(basic_grid)
                    story.append(Spacer(1, 8))
                
                # Ventrículo esquerdo
                ve_params = [
                    {'label': 'DDVE', 'field': 'diametro_diastolico_final_ve', 'unit': 'mm'},
                    {'label': 'DSVE', 'field': 'diametro_sistolico_final', 'unit': 'mm'},
                    {'label': '% Encurtamento', 'field': 'percentual_encurtamento', 'unit': '%'},
                    {'label': 'Septo', 'field': 'espessura_diastolica_septo', 'unit': 'mm'},
                    {'label': 'Parede Posterior', 'field': 'espessura_diastolica_ppve', 'unit': 'mm'},
                    {'label': 'Fração Ejeção', 'field': 'fracao_ejecao', 'unit': '%'},
                ]
                
                ve_grid = self._create_parameters_grid(parametros, "VENTRÍCULO ESQUERDO", ve_params)
                if ve_grid:
                    story.append(ve_grid)
                    story.append(Spacer(1, 8))
                
                # Volumes e função sistólica
                volume_params = [
                    {'label': 'VDF', 'field': 'volume_diastolico_final', 'unit': 'mL'},
                    {'label': 'VSF', 'field': 'volume_sistolico_final', 'unit': 'mL'},
                    {'label': 'Volume Ejeção', 'field': 'volume_ejecao', 'unit': 'mL'},
                    {'label': 'Massa VE', 'field': 'massa_ve', 'unit': 'g'},
                ]
                
                volume_grid = self._create_parameters_grid(parametros, "VOLUMES E FUNÇÃO SISTÓLICA", volume_params)
                if volume_grid:
                    story.append(volume_grid)
                    story.append(Spacer(1, 8))
            
            # Quebra de página para seções médicas
            story.append(PageBreak())
            
            # Seções médicas com formatação elegante
            if laudos:
                laudo = laudos[0]
                
                # Modo M e Bidimensional
                if laudo.modo_m_bidimensional:
                    story.append(Paragraph("MODO M E BIDIMENSIONAL", self.styles['SubtituloModerno']))
                    story.append(Paragraph(laudo.modo_m_bidimensional, self.styles['CorpoModerno']))
                    story.append(Spacer(1, 10))
                
                # Doppler Convencional
                if laudo.doppler_convencional:
                    story.append(Paragraph("DOPPLER CONVENCIONAL", self.styles['SubtituloModerno']))
                    story.append(Paragraph(laudo.doppler_convencional, self.styles['CorpoModerno']))
                    story.append(Spacer(1, 10))
                
                # Doppler Tecidual
                if laudo.doppler_tecidual:
                    story.append(Paragraph("DOPPLER TECIDUAL", self.styles['SubtituloModerno']))
                    story.append(Paragraph(laudo.doppler_tecidual, self.styles['CorpoModerno']))
                    story.append(Spacer(1, 10))
                
                # Conclusão destacada
                if laudo.conclusao:
                    conclusion_elements = self._create_conclusion_box(laudo.conclusao)
                    for element in conclusion_elements:
                        story.append(element)
                    story.append(Spacer(1, 15))
            
            # Assinatura médica moderna
            if medico:
                story.append(Spacer(1, 20))
                
                # Assinatura digital
                signature_img = self._get_signature_image(medico)
                if signature_img:
                    story.append(Image(signature_img, width=120, height=40))
                else:
                    # Caixa de assinatura elegante
                    sig_data = [["ASSINATURA DIGITAL"]]
                    sig_table = Table(sig_data, colWidths=[8*cm])
                    sig_table.setStyle(TableStyle([
                        ('BOX', (0, 0), (0, 0), 1, colors.HexColor('#BDC3C7')),
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (0, 0), 9),
                        ('TOPPADDING', (0, 0), (0, 0), 15),
                        ('BOTTOMPADDING', (0, 0), (0, 0), 15),
                        ('ROUNDEDCORNERS', [3, 3, 3, 3]),
                    ]))
                    story.append(sig_table)
                
                story.append(Spacer(1, 6))
                
                # Informações do médico
                medico_info = f"<b>Dr. {medico.nome}</b><br/>CRM-SP {medico.crm}"
                story.append(Paragraph(medico_info, self.styles['CorpoModerno']))
            
            # Gerar PDF
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            
            # Log de sucesso
            file_size = os.path.getsize(output_path)
            logger.info(f"PDF institucional gerado: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF institucional: {e}")
            raise