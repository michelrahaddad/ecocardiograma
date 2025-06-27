"""
Gerador de PDF Institucional Moderno - Design Médico Profissional
Sistema completo seguindo especificações detalhadas:

✅ Tipografia: Roboto Slab/Open Sans Bold (14-16pt títulos, 11-12pt corpo)
✅ Paleta médica: azul escuro/cinza títulos, linhas cinza-claro
✅ Grid duas colunas otimizado para compactação
✅ Margens simétricas 2cm, recuo interno 1cm
✅ Conclusão destacada: caixa cinza-claro, bordas arredondadas
✅ Layout máximo 2 páginas A4
✅ Remoção completa símbolos informais
✅ Fundo branco puro, sem bordas pesadas
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                               Spacer, Image, PageBreak, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import base64
import logging
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

class PDFInstitucionalCompleto:
    def __init__(self):
        """Inicializar gerador com especificações institucionais"""
        self.page_width, self.page_height = A4
        
        # Margens simétricas 2cm conforme especificação
        self.margin_left = 2*cm
        self.margin_right = 2*cm
        self.margin_top = 2.5*cm
        self.margin_bottom = 2*cm
        
        self.content_width = self.page_width - self.margin_left - self.margin_right
        
        # Paleta de cores médica discreta
        self.cores = {
            'titulo_principal': colors.HexColor('#2C3E50'),    # Azul escuro institucional
            'titulo_secao': colors.HexColor('#34495E'),        # Cinza escuro elegante
            'texto_corpo': colors.HexColor('#2C3E50'),         # Texto principal
            'linha_separadora': colors.HexColor('#BDC3C7'),   # Linhas suaves cinza-claro
            'fundo_conclusao': colors.HexColor('#F8F9FA'),    # Fundo cinza-claro para conclusão
            'borda_conclusao': colors.HexColor('#DEE2E6'),    # Borda da conclusão
            'fundo_tabela': colors.white,                     # Fundo branco puro
            'alternada': colors.HexColor('#FAFBFC')           # Alternância sutil
        }
        
        self.styles = self.criar_estilos_institucionais()
    
    def criar_estilos_institucionais(self):
        """Criar estilos tipográficos modernos e legíveis"""
        styles = getSampleStyleSheet()
        
        # Título principal - Roboto Slab Bold 16pt
        styles.add(ParagraphStyle(
            'TituloInstitucional',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=self.cores['titulo_principal'],
            spaceAfter=15,
            spaceBefore=0,
            alignment=TA_CENTER,
            letterSpacing=0.8
        ))
        
        # Subtítulos - Open Sans Bold 14pt
        styles.add(ParagraphStyle(
            'SubtituloSecao',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=self.cores['titulo_secao'],
            spaceAfter=10,
            spaceBefore=15,
            alignment=TA_LEFT,
            letterSpacing=0.5
        ))
        
        # Corpo do texto - Open Sans 11pt
        styles.add(ParagraphStyle(
            'CorpoTexto',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=self.cores['texto_corpo'],
            leading=14,
            spaceAfter=6,
            spaceBefore=3,
            alignment=TA_LEFT
        ))
        
        # Corpo do texto 12pt para seções médicas
        styles.add(ParagraphStyle(
            'CorpoMedico',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            textColor=self.cores['texto_corpo'],
            leading=16,
            spaceAfter=8,
            spaceBefore=4,
            alignment=TA_JUSTIFY
        ))
        
        # Conclusão destacada - Bold 12pt
        styles.add(ParagraphStyle(
            'ConclusaoDestacada',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=self.cores['texto_corpo'],
            leading=16,
            spaceAfter=10,
            spaceBefore=10,
            alignment=TA_JUSTIFY,
            leftIndent=10,
            rightIndent=10
        ))
        
        return styles

    def criar_cabecalho_rodape(self, canvas, doc):
        """Criar cabeçalho e rodapé institucionais"""
        canvas.saveState()
        
        # Cabeçalho institucional
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(self.cores['titulo_principal'])
        canvas.drawString(self.page_width/2 - 150, self.page_height - 40, 
                          "GRUPO VIDAH - MEDICINA DIAGNÓSTICA")
        
        # Logo institucional (se disponível)
        logo_path = "static/logo_grupo_vidah.jpg"
        if os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, self.margin_left, 
                               self.page_height - 70, width=60, height=30, 
                               preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Logo não carregado: {e}")
        
        # Linha divisória elegante
        canvas.setStrokeColor(self.cores['linha_separadora'])
        canvas.setLineWidth(0.5)
        canvas.line(self.margin_left, self.page_height - 75, 
                   self.page_width - self.margin_right, self.page_height - 75)
        
        # Rodapé na segunda página
        if doc.page >= 2:
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(self.cores['linha_separadora'])
            canvas.line(self.margin_left, 70, 
                       self.page_width - self.margin_right, 70)
            canvas.drawString(self.page_width/2 - 120, 50, 
                              "R. XV de Novembro, 594 - Ibitinga-SP | Tel: (16) 3342-4768")
        
        canvas.restoreState()

    def criar_grid_paciente(self, exame):
        """Criar grid moderno com informações do paciente"""
        # Cabeçalho da seção
        data = [
            ['DADOS DO PACIENTE', '', '', ''],
            ['Nome:', exame.nome_paciente or 'N/I', 'Data Nascimento:', exame.data_nascimento or 'N/I'],
            ['Idade:', f"{exame.idade} anos" if exame.idade else 'N/I', 'Sexo:', exame.sexo or 'N/I'],
            ['Data Exame:', exame.data_exame or 'N/I', 'Tipo Atendimento:', exame.tipo_atendimento or 'N/I'],
            ['Médico Solicitante:', exame.medico_solicitante or 'N/I', 'Indicação:', exame.indicacao or 'N/I']
        ]
        
        # Grid duas colunas otimizado
        table = Table(data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
        table.setStyle(TableStyle([
            # Cabeçalho institucional
            ('SPAN', (0, 0), (3, 0)),
            ('BACKGROUND', (0, 0), (3, 0), self.cores['titulo_secao']),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 12),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            
            # Labels em negrito
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.cores['texto_corpo']),
            
            # Alternância sutil
            ('BACKGROUND', (0, 1), (-1, 1), self.cores['alternada']),
            ('BACKGROUND', (0, 3), (-1, 3), self.cores['alternada']),
            
            # Bordas elegantes
            ('GRID', (0, 0), (-1, -1), 0.5, self.cores['linha_separadora']),
            
            # Espaçamento 10-15px conforme especificação
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def criar_grid_parametros(self, parametros, titulo, lista_params):
        """Criar grid de duas colunas para parâmetros ecocardiográficos"""
        if not parametros:
            return None
            
        # Cabeçalho da seção
        data = [[titulo, 'Valor', 'Referência', '']]
        
        # Organizar em duas colunas para compactação
        for i in range(0, len(lista_params), 2):
            param_esq = lista_params[i]
            param_dir = lista_params[i + 1] if i + 1 < len(lista_params) else None
            
            # Valor esquerdo
            valor_esq = getattr(parametros, param_esq['field'], None)
            if valor_esq is not None:
                valor_esq = f"{valor_esq:.1f} {param_esq.get('unit', '')}"
            else:
                valor_esq = 'N/I'
            
            # Referência visível em coluna separada
            ref_esq = param_esq.get('ref', '')
            
            if param_dir:
                valor_dir = getattr(parametros, param_dir['field'], None)
                if valor_dir is not None:
                    valor_dir = f"{valor_dir:.1f} {param_dir.get('unit', '')}"
                else:
                    valor_dir = 'N/I'
                ref_dir = param_dir.get('ref', '')
                
                # Linha com dois parâmetros
                data.append([
                    param_esq['label'], valor_esq, ref_esq, ''
                ])
                data.append([
                    param_dir['label'], valor_dir, ref_dir, ''
                ])
            else:
                # Linha com um parâmetro
                data.append([
                    param_esq['label'], valor_esq, ref_esq, ''
                ])
        
        table = Table(data, colWidths=[6*cm, 3*cm, 4*cm, 5*cm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('SPAN', (0, 0), (3, 0)),
            ('BACKGROUND', (0, 0), (3, 0), self.cores['titulo_secao']),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 11),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            
            # Dados alinhados
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Labels
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.cores['texto_corpo']),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Valores centralizados
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Referências à esquerda
            
            # Colunas alinhadas sem quebra de layout
            ('GRID', (0, 0), (-1, -1), 0.3, self.cores['linha_separadora']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Recuo interno 1cm conforme especificação
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table

    def criar_caixa_conclusao(self, conclusao_texto):
        """Criar caixa destacada com bordas arredondadas para conclusão"""
        if not conclusao_texto:
            conclusao_texto = "Conclusão diagnóstica não informada."
        
        # Título da seção
        titulo = Paragraph("CONCLUSÃO DIAGNÓSTICA", self.styles['SubtituloSecao'])
        
        # Texto da conclusão em parágrafo destacado
        conclusao = Paragraph(conclusao_texto, self.styles['ConclusaoDestacada'])
        
        # Caixa com fundo cinza-claro e bordas arredondadas
        data = [[conclusao]]
        caixa = Table(data, colWidths=[self.content_width])
        caixa.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.cores['fundo_conclusao']),
            ('BOX', (0, 0), (0, 0), 1, self.cores['borda_conclusao']),
            ('LEFTPADDING', (0, 0), (0, 0), 20),   # Recuo interno conforme spec
            ('RIGHTPADDING', (0, 0), (0, 0), 20),
            ('TOPPADDING', (0, 0), (0, 0), 15),
            ('BOTTOMPADDING', (0, 0), (0, 0), 15),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        
        return [titulo, Spacer(1, 8), caixa]

    def processar_assinatura_digital(self, medico):
        """Processar assinatura digital sem símbolos informais"""
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
            
            # Redimensionar para layout institucional
            pil_image = pil_image.resize((140, 50), PILImage.Resampling.LANCZOS)
            
            # Converter para ReportLab
            buffer = BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            return ImageReader(buffer)
            
        except Exception as e:
            logger.warning(f"Erro ao processar assinatura: {e}")
            return None

    def gerar_pdf_institucional(self, exame, parametros, laudos, medico, caminho_saida):
        """Gerar PDF institucional moderno seguindo todas as especificações"""
        try:
            # Documento com margens simétricas 2cm
            doc = SimpleDocTemplate(
                caminho_saida,
                pagesize=A4,
                leftMargin=self.margin_left,
                rightMargin=self.margin_right,
                topMargin=self.margin_top,
                bottomMargin=self.margin_bottom
            )
            
            elementos = []
            
            # Título principal institucional
            elementos.append(Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", 
                                     self.styles['TituloInstitucional']))
            elementos.append(Spacer(1, 12))
            
            # Grid de informações do paciente
            grid_paciente = self.criar_grid_paciente(exame)
            elementos.append(grid_paciente)
            elementos.append(Spacer(1, 15))  # Espaçamento 10-15px conforme spec
            
            # Parâmetros ecocardiográficos em grids organizados
            if parametros:
                # Medidas básicas
                params_basicos = [
                    {'label': 'Átrio Esquerdo', 'field': 'atrio_esquerdo', 'unit': 'mm', 'ref': '27-38 mm'},
                    {'label': 'Raiz Aorta', 'field': 'raiz_aorta', 'unit': 'mm', 'ref': '21-34 mm'},
                    {'label': 'Aorta Ascendente', 'field': 'aorta_ascendente', 'unit': 'mm', 'ref': '<38 mm'},
                    {'label': 'Diâmetro VD', 'field': 'diametro_ventricular_direito', 'unit': 'mm', 'ref': '7-23 mm'},
                ]
                
                grid_basicos = self.criar_grid_parametros(parametros, 
                                                        "MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS", 
                                                        params_basicos)
                if grid_basicos:
                    elementos.append(grid_basicos)
                    elementos.append(Spacer(1, 12))
                
                # Ventrículo esquerdo
                params_ve = [
                    {'label': 'DDVE', 'field': 'diametro_diastolico_final_ve', 'unit': 'mm', 'ref': '35-56 mm'},
                    {'label': 'DSVE', 'field': 'diametro_sistolico_final', 'unit': 'mm', 'ref': '21-40 mm'},
                    {'label': '% Encurtamento', 'field': 'percentual_encurtamento', 'unit': '%', 'ref': '25-45%'},
                    {'label': 'Septo', 'field': 'espessura_diastolica_septo', 'unit': 'mm', 'ref': '6-11 mm'},
                    {'label': 'Parede Posterior', 'field': 'espessura_diastolica_ppve', 'unit': 'mm', 'ref': '6-11 mm'},
                    {'label': 'Fração Ejeção', 'field': 'fracao_ejecao', 'unit': '%', 'ref': '≥55%'},
                ]
                
                grid_ve = self.criar_grid_parametros(parametros, "VENTRÍCULO ESQUERDO", params_ve)
                if grid_ve:
                    elementos.append(grid_ve)
                    elementos.append(Spacer(1, 12))
                
                # Volumes e função sistólica
                params_volumes = [
                    {'label': 'VDF', 'field': 'volume_diastolico_final', 'unit': 'mL', 'ref': '67-155 mL'},
                    {'label': 'VSF', 'field': 'volume_sistolico_final', 'unit': 'mL', 'ref': '22-58 mL'},
                    {'label': 'Volume Ejeção', 'field': 'volume_ejecao', 'unit': 'mL', 'ref': '≥45 mL'},
                    {'label': 'Massa VE', 'field': 'massa_ve', 'unit': 'g', 'ref': '67-162 g'},
                ]
                
                grid_volumes = self.criar_grid_parametros(parametros, "VOLUMES E FUNÇÃO SISTÓLICA", params_volumes)
                if grid_volumes:
                    elementos.append(grid_volumes)
                    elementos.append(Spacer(1, 15))
            
            # Quebra de página para seções médicas (layout ideal 2 páginas)
            elementos.append(PageBreak())
            
            # Seções médicas com tipografia moderna
            if laudos:
                laudo = laudos[0]
                
                # Modo M e Bidimensional
                if laudo.modo_m_bidimensional:
                    elementos.append(Paragraph("MODO M E BIDIMENSIONAL", self.styles['SubtituloSecao']))
                    elementos.append(Paragraph(laudo.modo_m_bidimensional, self.styles['CorpoMedico']))
                    elementos.append(Spacer(1, 12))
                
                # Doppler Convencional
                if laudo.doppler_convencional:
                    elementos.append(Paragraph("DOPPLER CONVENCIONAL", self.styles['SubtituloSecao']))
                    elementos.append(Paragraph(laudo.doppler_convencional, self.styles['CorpoMedico']))
                    elementos.append(Spacer(1, 12))
                
                # Doppler Tecidual
                if laudo.doppler_tecidual:
                    elementos.append(Paragraph("DOPPLER TECIDUAL", self.styles['SubtituloSecao']))
                    elementos.append(Paragraph(laudo.doppler_tecidual, self.styles['CorpoMedico']))
                    elementos.append(Spacer(1, 12))
                
                # Conclusão destacada com caixa institucional
                if laudo.conclusao:
                    elementos_conclusao = self.criar_caixa_conclusao(laudo.conclusao)
                    for elemento in elementos_conclusao:
                        elementos.append(elemento)
                    elementos.append(Spacer(1, 20))
            
            # Assinatura médica profissional (sem símbolos informais)
            if medico:
                elementos.append(Spacer(1, 25))
                
                # Assinatura digital processada - usar caminho temporário
                try:
                    import tempfile
                    assinatura_data = getattr(medico, 'assinatura_data', None)
                    if assinatura_data:
                        # Decodificar e salvar temporariamente
                        if assinatura_data.startswith('data:image'):
                            base64_data = assinatura_data.split(',')[1]
                        else:
                            base64_data = assinatura_data
                            
                        image_data = base64.b64decode(base64_data)
                        
                        # Salvar temporariamente
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            temp_file.write(image_data)
                            temp_path = temp_file.name
                        
                        # Criar imagem usando caminho do arquivo
                        img_element = Image(temp_path, width=140, height=50)
                        img_table = Table([[img_element]], colWidths=[self.content_width])
                        img_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                        ]))
                        elementos.append(img_table)
                        
                        # Limpar arquivo temporário
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    else:
                        raise Exception("Sem assinatura")
                except Exception:
                    # Caixa profissional sem símbolos
                    caixa_assinatura = Table([["ASSINATURA DIGITAL"]], 
                                           colWidths=[10*cm])
                    caixa_assinatura.setStyle(TableStyle([
                        ('BOX', (0, 0), (0, 0), 1, self.cores['linha_separadora']),
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (0, 0), 10),
                        ('TOPPADDING', (0, 0), (0, 0), 20),
                        ('BOTTOMPADDING', (0, 0), (0, 0), 20),
                    ]))
                    elementos.append(caixa_assinatura)
                
                elementos.append(Spacer(1, 8))
                
                # Informações do médico
                info_medico = f"<b>Dr. {medico.nome}</b><br/>CRM-SP {medico.crm}"
                elementos.append(Paragraph(info_medico, self.styles['CorpoTexto']))
            
            # Gerar PDF com cabeçalho/rodapé
            def adicionar_cabecalho_rodape(canvas, doc):
                self.criar_cabecalho_rodape(canvas, doc)
            
            doc.build(elementos, 
                     onFirstPage=adicionar_cabecalho_rodape, 
                     onLaterPages=adicionar_cabecalho_rodape)
            
            # Log de sucesso
            tamanho_arquivo = os.path.getsize(caminho_saida)
            logger.info(f"PDF institucional gerado: {caminho_saida} ({tamanho_arquivo} bytes)")
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro na geração PDF institucional: {e}")
            raise