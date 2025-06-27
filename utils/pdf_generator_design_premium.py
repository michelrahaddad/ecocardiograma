"""
Gerador de PDF Premium - Design Médico Profissional
Sistema completo com melhorias de design, layout e organização dos dados
Implementa indicadores visuais, cards organizados e hierarquia de informações
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFDesignPremium:
    def __init__(self):
        """Gerador premium com design médico profissional"""
        self.page_width, self.page_height = A4
        self.margins = 2*mm  # Margens mínimas para preenchimento máximo
        self.content_width = self.page_width - 2*self.margins
        
        # LINHA VERTICAL ÚNICA - POSIÇÃO FIXA PARA ALINHAMENTO PERFEITO
        self.linha_alinhamento_vertical = self.margins  # Mesma posição para TODOS os elementos
        
        # Paleta de cores médica profissional
        self.cores = {
            'primaria': colors.HexColor('#1A365D'),      # Azul médico principal
            'secundaria': colors.HexColor('#2E5090'),    # Azul complementar
            'acento': colors.HexColor('#4CAF50'),        # Verde para status normal
            'alerta': colors.HexColor('#FF6B6B'),        # Vermelho para alterações
            'neutro': colors.HexColor('#718096'),        # Cinza neutro
            'fundo_claro': colors.HexColor('#F8FAFC'),   # Fundo suave
            'fundo_card': colors.HexColor('#EDF2F7'),    # Fundo de cards
            'borda': colors.HexColor('#E2E8F0')          # Bordas suaves
        }
        
        self.styles = self.criar_estilos_premium()
    
    def criar_estilos_premium(self):
        """Estilos tipográficos profissionais"""
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=self.cores['primaria'],
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulos de seção - ALINHAMENTO VERTICAL ÚNICO
        styles.add(ParagraphStyle(
            name='SubtituloSecao',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=self.cores['primaria'],
            alignment=TA_LEFT,
            spaceAfter=4,
            spaceBefore=6,
            fontName='Helvetica-Bold',
            leftIndent=0,  # ZERO indentação - linha vertical única
            rightIndent=0  # ZERO indentação direita
        ))
        
        # Texto médico ultra-maximizado para preenchimento total
        styles.add(ParagraphStyle(
            name='TextoMedico',
            parent=styles['Normal'],
            fontSize=16,  # Aumentado para 16px (45% de aumento)
            leading=22,   # Leading aumentado para mais preenchimento
            textColor=self.cores['neutro'],
            alignment=TA_JUSTIFY,
            spaceAfter=18,  # Espaçamento triplicado para preenchimento total
            fontName='Helvetica',
            firstLineIndent=8  # Recuo primeira linha
        ))
        
        # Texto destacado para conclusões ultra-maximizado
        styles.add(ParagraphStyle(
            name='TextoDestaque',
            parent=styles['Normal'],
            fontSize=18,  # Aumentado para 18px (50% de aumento)
            leading=24,   # Leading aumentado para máximo preenchimento
            textColor=self.cores['primaria'],
            alignment=TA_JUSTIFY,
            spaceAfter=20,  # Espaçamento máximo para preenchimento
            fontName='Helvetica-Bold',
            firstLineIndent=8  # Recuo primeira linha
        ))
        
        return styles
    
    def criar_cabecalho_premium(self):
        """Cabeçalho com logo do Grupo Vidah"""
        elementos = []
        
        # Tentar incluir o logo
        try:
            from reportlab.platypus import Image
            import os
            
            logo_path = os.path.join('static', 'logo_grupo_vidah.jpg')
            if os.path.exists(logo_path):
                # Logo com proporção correta (não distorcido)
                logo_img = Image(logo_path, width=3*cm, height=3*cm)  # Proporção quadrada correta
                
                # Centralizar logo com padding ultra-reduzido
                logo_table = Table([[logo_img]], colWidths=[19*cm])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
                ]))
                elementos.append(logo_table)
                logger.info("✅ Logo do Grupo Vidah integrado no cabeçalho (compacto)")
            else:
                # Fallback para texto se logo não encontrado
                linha1_data = [['GRUPO VIDAH - MEDICINA DIAGNÓSTICA']]
                header_table = Table(linha1_data, colWidths=[19*cm])
                header_style = [
                    ('FONTSIZE', (0, 0), (0, 0), 9),
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (0, 0), (0, 0), self.cores['primaria']),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),  # Reduzido para evitar sobreposições
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)  # Reduzido para evitar sobreposições
                ]
                header_table.setStyle(TableStyle(header_style))
                elementos.append(header_table)
        
        except Exception as e:
            logger.warning(f"Erro ao carregar logo: {e}")
            # Fallback para texto em caso de erro
            linha1_data = [['GRUPO VIDAH - MEDICINA DIAGNÓSTICA']]
            header_table = Table(linha1_data, colWidths=[19*cm])
            header_style = [
                ('FONTSIZE', (0, 0), (0, 0), 9),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 0), (0, 0), self.cores['primaria']),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),  # Reduzido para evitar sobreposições
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)  # Reduzido para evitar sobreposições
            ]
            header_table.setStyle(TableStyle(header_style))
            elementos.append(header_table)
        
        # Segunda linha: título do documento (compacto)
        linha2_data = [['LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO']]
        titulo_table = Table(linha2_data, colWidths=[19*cm])
        titulo_style = [
            ('FONTSIZE', (0, 0), (0, 0), 13),  # Reduzido para eliminar sobreposição de caracteres
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, 0), self.cores['primaria']),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),  # Reduzido de 6 para 3
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Reduzido de 6 para 3
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.cores['secundaria'])  # Linha mais fina
        ]
        titulo_table.setStyle(TableStyle(titulo_style))
        elementos.append(titulo_table)
        elementos.append(Spacer(1, 12))  # Espaçamento aumentado para melhor qualidade visual
        
        return elementos
    
    def criar_card_paciente_premium(self, exame):
        """Card de dados do paciente com design premium"""
        elementos = []
        
        # TÍTULO PADRONIZADO PARA PREENCHIMENTO MÁXIMO
        titulo_tabela = Table([["DADOS DO PACIENTE"]], colWidths=[18*cm])
        titulo_tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 16),  # Padronização uniforme
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.cores['primaria']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # ALINHAMENTO À ESQUERDA
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),  # ZERO PADDING = MESMA POSIÇÃO DAS TABELAS
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),  # Ajustado para evitar sobreposições
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)  # Ajustado para evitar sobreposições
        ]))
        elementos.append(titulo_tabela)
        
        # Informações principais em destaque
        nome = getattr(exame, 'nome_paciente', '').upper()
        info_principal = [
            ['PACIENTE:', nome],
            ['DATA NASCIMENTO:', getattr(exame, 'data_nascimento', '')],
            ['DATA DO EXAME:', getattr(exame, 'data_exame', '')]
        ]
        
        card_principal = Table(info_principal, colWidths=[4.5*cm, 13.5*cm])
        card_principal.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Fonte reduzida para evitar sobreposições
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),  # Nome em destaque
            ('BACKGROUND', (0, 0), (-1, -1), self.cores['fundo_card']),
            ('GRID', (0, 0), (-1, -1), 1, self.cores['borda']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.cores['primaria']),
            ('TEXTCOLOR', (1, 0), (1, 0), self.cores['primaria']),  # Nome destacado
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elementos.append(card_principal)
        elementos.append(Spacer(1, 2))  # Reduzido para evitar sobreposições
        
        # Informações complementares seguindo alinhamento vertical único
        idade_text = f"{getattr(exame, 'idade', '')} anos" if getattr(exame, 'idade', None) else "—"
        
        # Convertendo para formato de tabela com alinhamento vertical único
        info_complementar = [
            ['IDADE:', idade_text],
            ['SEXO:', getattr(exame, 'sexo', '')],
            ['TIPO ATENDIMENTO:', getattr(exame, 'tipo_atendimento', '')]
        ]
        
        # Tabela seguindo alinhamento vertical único (18cm largura total)
        tabela_complementar = Table(info_complementar, colWidths=[4.5*cm, 13.5*cm])
        tabela_complementar.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Fonte padronizada para 10px
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Labels em negrito
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),  # Valores normais
            ('BACKGROUND', (0, 0), (-1, -1), self.cores['fundo_claro']),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cores['borda']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.cores['primaria']),  # Labels em azul
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        # Encapsulando na tabela de alinhamento único (LEFTPADDING=0)
        tabela_alinhamento_complementar = Table([[tabela_complementar]], colWidths=[18*cm])
        tabela_alinhamento_complementar.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0)
        ]))
        
        elementos.append(tabela_alinhamento_complementar)
        elementos.append(Spacer(1, 8))  # Espaçamento aumentado entre dados paciente e antropométricos
        
        return elementos
    
    def criar_tabela_parametros_premium(self, titulo, dados_parametros, icon="📊"):
        """Tabela de parâmetros com design compacto para evitar quebras de página"""
        from reportlab.platypus import KeepTogether
        
        elementos = []
        
        # TÍTULO ALINHADO VERTICALMENTE COM AS TABELAS - SEM ÍCONES
        titulo_completo = titulo.upper()
        titulo_tabela = Table([[titulo_completo]], colWidths=[18*cm])
        titulo_tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.cores['primaria']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # ALINHAMENTO À ESQUERDA
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),  # ZERO PADDING = MESMA POSIÇÃO DAS TABELAS
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        if not dados_parametros:
            elementos.append(titulo_tabela)
            elementos.append(Paragraph("Dados não disponíveis", self.styles['TextoMedico']))
            elementos.append(Spacer(1, 2))
            return elementos
        
        # Cabeçalho da tabela sem coluna STATUS
        cabecalho = ['PARÂMETRO', 'VALOR MEDIDO', 'REFERÊNCIA NORMAL']
        dados_tabela = [cabecalho] + dados_parametros
        
        # Larguras das colunas ultra-compactas para evitar overflow
        tabela = Table(dados_tabela, colWidths=[6*cm, 4*cm, 8*cm])
        
        # Estilo da tabela com contraste pronunciado e sombreamento
        table_style = [
            # Cabeçalho com contraste aprimorado
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),  # Azul mais escuro para contraste
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            
            # Conteúdo com fonte maior para melhor preenchimento
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Nomes dos parâmetros
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            
            # Sombreamento sutil para profundidade visual
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FAFBFC')),  # Fundo levemente cinza
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),  # Listras alternadas
            
            # Bordas modernas com bordas suaves
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#E2E8F0')),  # Borda mais suave
            ('LINEBELOW', (0, 1), (-1, -2), 0.3, colors.HexColor('#E2E8F0')),  # Linhas mais suaves
            ('ROUNDEDCORNERS', [3, 3, 3, 3]),  # Cantos arredondados para modernidade
            
            # Padding compacto para 2 páginas
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduzido para compactar
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Valores centralizados
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Referências alinhadas à esquerda
        ]
        
        tabela.setStyle(TableStyle(table_style))
        
        # Agrupar título e tabela para evitar quebra de página
        secao_completa = [titulo_tabela, tabela]
        elementos.append(KeepTogether(secao_completa))
        elementos.append(Spacer(1, 0))  # Zero espaçamento entre tabelas
        
        return elementos
    
    def criar_card_medico_premium(self, titulo, conteudo, icon="🔍", destaque=False):
        """Card médico compacto com controle de quebra de texto"""
        from reportlab.platypus import KeepTogether
        
        elementos = []
        
        if not conteudo or conteudo.strip() == "":
            return elementos
        
        # TÍTULO ALINHADO VERTICALMENTE COM AS TABELAS - CARD MÉDICO SEM ÍCONES
        titulo_completo = titulo.upper()
        cor_titulo = self.cores['acento'] if destaque else self.cores['primaria']
        
        titulo_tabela = Table([[titulo_completo]], colWidths=[18*cm])
        titulo_tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), cor_titulo),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # ALINHAMENTO À ESQUERDA
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),  # ZERO PADDING = MESMA POSIÇÃO DAS TABELAS
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))
        
        # TEXTO COMO PARÁGRAFO COM QUEBRA AUTOMÁTICA + TABELA PARA ALINHAMENTO
        conteudo_style = ParagraphStyle(
            'ConteudoAlinhado',
            fontSize=11 if destaque else 10,
            fontName='Helvetica-Bold' if destaque else 'Helvetica',
            leading=16 if destaque else 14,
            leftIndent=0,  # Zero indent para alinhar com títulos
            rightIndent=0,
            spaceBefore=2,
            spaceAfter=4,
            wordWrap='CJK',  # Quebra automática de palavras
            alignment=0  # Alinhamento à esquerda
        )
        
        # Criar parágrafo com quebra automática
        conteudo_paragraph = Paragraph(conteudo, conteudo_style)
        
        # Envolver em tabela para alinhamento perfeito com títulos
        conteudo_tabela = Table([[conteudo_paragraph]], colWidths=[18*cm])
        conteudo_tabela.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # ALINHAMENTO À ESQUERDA
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),  # ZERO PADDING = MESMA POSIÇÃO DOS TÍTULOS
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
        ]))
        
        # Agrupar título e texto com alinhamento perfeito
        card_completo = [titulo_tabela, conteudo_tabela]
        elementos.append(KeepTogether(card_completo))
        elementos.append(Spacer(1, 1))  # Espaçamento mínimo para compensar espaço extra do cabeçalho
        
        return elementos
    
    def criar_assinatura_premium(self, medico):
        """Assinatura médica premium com design profissional e assinatura digital integrada"""
        elementos = []
        
        if not medico:
            return elementos
        
        # Espaçamento mínimo antes da assinatura
        elementos.append(Spacer(1, 8))
        
        # Linha divisória elegante com padding ultra-reduzido
        linha_assinatura = Table([[''] * 1], colWidths=[18*cm])
        linha_assinatura.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, self.cores['borda']),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))
        elementos.append(linha_assinatura)
        
        # Integrar assinatura digital se disponível
        assinatura_data = getattr(medico, 'assinatura_data', None)
        if assinatura_data:
            try:
                import base64
                import io
                from PIL import Image as PILImage
                from reportlab.platypus import Image
                
                # Remover prefixo data:image se presente
                if assinatura_data.startswith('data:image'):
                    assinatura_data = assinatura_data.split(',')[1]
                
                # Decodificar base64
                assinatura_bytes = base64.b64decode(assinatura_data)
                assinatura_img = PILImage.open(io.BytesIO(assinatura_bytes))
                
                # Redimensionar mantendo proporção (compacto para 2 páginas)
                largura_max = 120
                altura_max = 50
                assinatura_img.thumbnail((largura_max, altura_max), PILImage.Resampling.LANCZOS)
                
                # Converter para ReportLab
                img_buffer = io.BytesIO()
                assinatura_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Criar imagem para o PDF
                img_assinatura = Image(img_buffer, width=assinatura_img.width*0.75, height=assinatura_img.height*0.75)
                
                # Centralizar assinatura em tabela
                tabela_img = Table([[img_assinatura]], colWidths=[18*cm])
                tabela_img.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
                ]))
                elementos.append(tabela_img)
                
                logger.info("✅ Assinatura digital integrada no PDF")
                
            except Exception as e:
                logger.warning(f"Erro ao processar assinatura digital: {e}")
                # Fallback para caixa de assinatura
                caixa_assinatura = Table([['ASSINATURA DIGITAL']], colWidths=[10*cm])
                caixa_assinatura.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                elementos.append(caixa_assinatura)
        else:
            # Caixa de assinatura digital quando não há imagem
            caixa_assinatura = Table([['ASSINATURA DIGITAL']], colWidths=[10*cm])
            caixa_assinatura.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            elementos.append(caixa_assinatura)
        
        elementos.append(Spacer(1, 6))
        
        # Informações do médico (sem especialidade)
        nome_medico = getattr(medico, 'nome', 'Médico Responsável')
        crm_medico = getattr(medico, 'crm', '')
        
        assinatura_texto = [
            [f"Dr. {nome_medico}"],
            [f"CRM-SP {crm_medico}"]
        ]
        
        tabela_assinatura = Table(assinatura_texto, colWidths=[18*cm])
        tabela_assinatura.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.cores['primaria']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))
        
        elementos.append(tabela_assinatura)
        
        # Rodapé com endereço na segunda página
        elementos.append(Spacer(1, 15))
        endereco_text = "R. XV de Novembro, 594 - Ibitinga-SP | Tel: (16) 3342-4768"
        endereco_tabela = Table([[endereco_text]], colWidths=[18*cm])
        endereco_tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.cores['neutro']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, 0), (-1, 0), 1, self.cores['borda'])
        ]))
        elementos.append(endereco_tabela)
        
        return elementos
    
    def determinar_status_parametro(self, valor, min_normal, max_normal):
        """Determinar status do parâmetro baseado nos valores de referência"""
        if not valor or valor == 0:
            return "—"
        
        try:
            valor_num = float(valor)
            if min_normal <= valor_num <= max_normal:
                return "NORMAL"
            else:
                return "ALTERADO"
        except (ValueError, TypeError):
            return "—"
    
    def processar_medidas_basicas(self, parametros):
        """Processar medidas ecocardiográficas básicas"""
        if not parametros:
            return []
        
        dados = []
        
        # Átrio Esquerdo
        ae = getattr(parametros, 'atrio_esquerdo', 0)
        if ae and ae != 0:
            dados.append(['Átrio Esquerdo', f"{ae:.1f} mm", "27-38 mm"])
        
        # Raiz da Aorta
        ao = getattr(parametros, 'raiz_aorta', 0)
        if ao and ao != 0:
            dados.append(['Raiz da Aorta', f"{ao:.1f} mm", "21-34 mm"])
        
        # Relação AE/Ao
        if ae and ao and ae != 0 and ao != 0:
            relacao = ae / ao
            dados.append(['Relação AE/Ao', f"{relacao:.2f}", "< 1,5"])
        
        # Aorta Ascendente
        asc = getattr(parametros, 'aorta_ascendente', 0)
        if asc and asc != 0:
            dados.append(['Aorta Ascendente', f"{asc:.1f} mm", "< 38 mm"])
        
        # Diâmetros VD
        vd = getattr(parametros, 'diametro_ventricular_direito', 0)
        if vd and vd != 0:
            dados.append(['Diâmetro VD', f"{vd:.1f} mm", "7-23 mm"])
        
        vd_basal = getattr(parametros, 'diametro_basal_vd', 0)
        if vd_basal and vd_basal != 0:
            dados.append(['Diâmetro Basal VD', f"{vd_basal:.1f} mm", "25-41 mm"])
        
        return dados
    
    def processar_ventriculo_esquerdo(self, parametros):
        """Processar dados do ventrículo esquerdo"""
        if not parametros:
            return []
        
        dados = []
        
        # DDVE
        ddve = getattr(parametros, 'diametro_diastolico_final_ve', 0)
        if ddve and ddve != 0:
            dados.append(['DDVE', f"{ddve:.1f} mm", "35-56 mm"])
        
        # DSVE
        dsve = getattr(parametros, 'diametro_sistolico_final', 0)
        if dsve and dsve != 0:
            dados.append(['DSVE', f"{dsve:.1f} mm", "21-40 mm"])
        
        # Percentual de Encurtamento
        enc = getattr(parametros, 'percentual_encurtamento', 0)
        if enc and enc != 0:
            dados.append(['% Encurtamento', f"{enc:.1f}%", "25-45%"])
        
        # Septo
        septo = getattr(parametros, 'espessura_diastolica_septo', 0)
        if septo and septo != 0:
            dados.append(['Septo', f"{septo:.1f} mm", "6-11 mm"])
        
        # Parede Posterior
        pp = getattr(parametros, 'espessura_diastolica_ppve', 0)
        if pp and pp != 0:
            dados.append(['Parede Posterior', f"{pp:.1f} mm", "6-11 mm"])
        
        # Relação Septo/PP
        if septo and pp and septo != 0 and pp != 0:
            relacao = septo / pp
            dados.append(['Relação Septo/PP', f"{relacao:.2f}", "< 1,3"])
        
        return dados
    
    def processar_volumes_funcao(self, parametros):
        """Processar volumes e função sistólica"""
        if not parametros:
            return []
        
        dados = []
        
        # VDF
        vdf = getattr(parametros, 'volume_diastolico_final', 0)
        if vdf and vdf != 0:
            dados.append(['VDF', f"{vdf:.1f} mL", "67-155 mL"])
        
        # VSF
        vsf = getattr(parametros, 'volume_sistolico_final', 0)
        if vsf and vsf != 0:
            dados.append(['VSF', f"{vsf:.1f} mL", "22-58 mL"])
        
        # Volume de Ejeção
        ve = getattr(parametros, 'volume_ejecao', 0)
        if ve and ve != 0:
            dados.append(['Volume Ejeção', f"{ve:.1f} mL", "Calculado"])
        
        # Fração de Ejeção
        fe = getattr(parametros, 'fracao_ejecao', 0)
        if fe and fe != 0:
            dados.append(['Fração de Ejeção', f"{fe:.1f}%", "≥ 55%"])
        
        # Massa VE
        massa = getattr(parametros, 'massa_ve', 0)
        if massa and massa != 0:
            dados.append(['Massa VE', f"{massa:.1f} g", "Calculada"])
        
        # Índice de Massa VE
        indice_massa = getattr(parametros, 'indice_massa_ve', 0)
        if indice_massa and indice_massa != 0:
            dados.append(['Índice Massa VE', f"{indice_massa:.1f} g/m²", "Calculado"])
        
        return dados
    
    def processar_velocidades_fluxos(self, parametros):
        """Processar velocidades dos fluxos"""
        if not parametros:
            return []
        
        dados = []
        
        fluxos = [
            ('fluxo_pulmonar', 'Fluxo Pulmonar', 'm/s', '0,6-0,9 m/s'),
            ('fluxo_mitral', 'Fluxo Mitral', 'm/s', '0,6-1,3 m/s'),
            ('fluxo_aortico', 'Fluxo Aórtico', 'm/s', '1,0-1,7 m/s'),
            ('fluxo_tricuspide', 'Fluxo Tricúspide', 'm/s', '0,3-0,7 m/s')
        ]
        
        for campo, nome, unidade, referencia in fluxos:
            valor = getattr(parametros, campo, 0)
            if valor and valor != 0:
                dados.append([nome, f"{valor:.2f} {unidade}", referencia])
        
        return dados
    
    def processar_gradientes(self, parametros):
        """Processar gradientes"""
        if not parametros:
            return []
        
        dados = []
        
        gradientes = [
            ('gradiente_vd_ap', 'VD → AP', '<10 mmHg'),
            ('gradiente_ae_ve', 'AE → VE', '<5 mmHg'),
            ('gradiente_ve_ao', 'VE → AO', '<10 mmHg'),
            ('gradiente_ad_vd', 'AD → VD', '<5 mmHg'),
            ('gradiente_tricuspide', 'Insuf. Tricúspide', '<5 mmHg'),
        ]
        
        for campo, nome, referencia in gradientes:
            valor = getattr(parametros, campo, 0)
            if valor and valor != 0:
                dados.append([nome, f"{valor:.1f} mmHg", referencia])
        
        # PSAP
        psap = getattr(parametros, 'pressao_sistolica_vd', 0)
        if psap and psap != 0:
            dados.append(['PSAP', f"{psap:.1f} mmHg", "<35 mmHg"])
        
        return dados
    
    def gerar_pdf_premium(self, exame, parametros, laudo, medico, nome_arquivo):
        """Gerar PDF premium com design profissional"""
        try:
            # Configurar documento
            doc = SimpleDocTemplate(
                nome_arquivo,
                pagesize=A4,
                rightMargin=self.margins,
                leftMargin=self.margins,
                topMargin=self.margins,
                bottomMargin=self.margins
            )
            
            # Lista de elementos
            elementos = []
            
            # 1. Cabeçalho premium
            elementos.extend(self.criar_cabecalho_premium())
            
            # 2. Dados do paciente
            elementos.extend(self.criar_card_paciente_premium(exame))
            
            # 3. Antropometria (se houver)
            if parametros:
                peso = getattr(parametros, 'peso', 0)
                altura = getattr(parametros, 'altura', 0)
                sc = getattr(parametros, 'superficie_corporal', 0)
                fc = getattr(parametros, 'frequencia_cardiaca', 0)
                
                if any([peso, altura, sc, fc]):
                    dados_antro = []
                    if peso: dados_antro.append(['Peso', f"{peso:.1f} kg", "Medido"])
                    if altura: dados_antro.append(['Altura', f"{altura:.0f} cm", "Medido"])
                    if sc: dados_antro.append(['Superfície Corporal', f"{sc:.2f} m²", "Calculada"])
                    if fc: dados_antro.append(['Frequência Cardíaca', f"{fc:.0f} bpm", "60-100 bpm"])
                    
                    elementos.extend(self.criar_tabela_parametros_premium(
                        "Dados Antropométricos", dados_antro, "👤"
                    ))
            
            # 4. Medidas Ecocardiográficas Básicas
            dados_basicas = self.processar_medidas_basicas(parametros)
            if dados_basicas:
                elementos.extend(self.criar_tabela_parametros_premium(
                    "Medidas Ecocardiográficas Básicas", dados_basicas, "📊"
                ))
            
            # 5. Ventrículo Esquerdo
            dados_ve = self.processar_ventriculo_esquerdo(parametros)
            if dados_ve:
                elementos.extend(self.criar_tabela_parametros_premium(
                    "Ventrículo Esquerdo", dados_ve, ""
                ))
            
            # 6. Velocidades dos Fluxos (página 1)
            dados_velocidades = self.processar_velocidades_fluxos(parametros)
            if dados_velocidades:
                elementos.extend(self.criar_tabela_parametros_premium(
                    "Velocidades dos Fluxos", dados_velocidades, "🌊"
                ))
            
            # QUEBRA DE PÁGINA - Iniciar página 2 com Gradientes
            from reportlab.platypus import PageBreak
            elementos.append(PageBreak())
            
            # 7. Gradientes (início da página 2)
            dados_gradientes = self.processar_gradientes(parametros)
            if dados_gradientes:
                elementos.extend(self.criar_tabela_parametros_premium(
                    "Gradientes", dados_gradientes, "📈"
                ))
            
            # 8. Volumes e Função Sistólica (página 2)
            dados_volumes = self.processar_volumes_funcao(parametros)
            if dados_volumes:
                elementos.extend(self.criar_tabela_parametros_premium(
                    "Volumes e Função Sistólica", dados_volumes, "🔄"
                ))
            
            # TÍTULO CHAMATIVO "LAUDO ECOCARDIOGRAMA" - BEM VISÍVEL
            elementos.append(Spacer(1, 15))
            
            titulo_laudo = Table([["LAUDO ECOCARDIOGRAMA"]], colWidths=[18*cm])
            titulo_laudo.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 18),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.cores['primaria']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            elementos.append(titulo_laudo)
            elementos.append(Spacer(1, 10))
            
            # 9. Seções médicas em cards (sem quebra forçada)
            if laudo:
                # Modo M e Bidimensional
                modo_m = getattr(laudo, 'modo_m_bidimensional', '')
                if modo_m:
                    elementos.extend(self.criar_card_medico_premium(
                        "Modo M e Bidimensional", modo_m, "🔍"
                    ))
                
                # Doppler Convencional
                doppler_conv = getattr(laudo, 'doppler_convencional', '')
                if doppler_conv:
                    elementos.extend(self.criar_card_medico_premium(
                        "Doppler Convencional", doppler_conv, "📊"
                    ))
                
                # Doppler Tecidual
                doppler_tec = getattr(laudo, 'doppler_tecidual', '')
                if doppler_tec:
                    elementos.extend(self.criar_card_medico_premium(
                        "Doppler Tecidual", doppler_tec, "🎯"
                    ))
                
                # Conclusão (destacada)
                conclusao = getattr(laudo, 'conclusao', '')
                if conclusao:
                    elementos.extend(self.criar_card_medico_premium(
                        "Conclusão Diagnóstica", conclusao, "📋", destaque=True
                    ))
            
            # 10. Assinatura médica
            elementos.extend(self.criar_assinatura_premium(medico))
            
            # Gerar o PDF
            doc.build(elementos)
            
            # Verificar tamanho do arquivo
            tamanho = os.path.getsize(nome_arquivo)
            logger.info(f"PDF premium gerado: {nome_arquivo} ({tamanho} bytes)")
            
            return nome_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF premium: {str(e)}")
            raise

def gerar_pdf_design_premium(exame, medico_data):
    """Função principal para gerar PDF com design premium"""
    try:
        # Verificar se os dados necessários estão disponíveis
        if not exame:
            raise ValueError("Dados do exame não fornecidos")
        
        # Criar gerador premium
        gerador = PDFDesignPremium()
        
        # Obter parâmetros e laudos
        parametros = getattr(exame, 'parametros', None)
        laudos = getattr(exame, 'laudos', [])
        laudo = laudos[0] if laudos else None
        
        # Criar objeto médico
        class MedicoObj:
            def __init__(self, data):
                self.nome = data.get('nome', 'Médico Responsável')
                self.crm = data.get('crm', '')
                self.assinatura_data = data.get('assinatura_data', None)
        
        medico = MedicoObj(medico_data)
        
        # Nome do arquivo
        nome_paciente = getattr(exame, 'nome_paciente', 'Paciente').replace(' ', '_')
        data_hoje = __import__('datetime').datetime.now().strftime('%d%m%Y')
        nome_arquivo = f"generated_pdfs/laudo_premium_{nome_paciente}_{data_hoje}.pdf"
        
        # Garantir que o diretório existe
        os.makedirs('generated_pdfs', exist_ok=True)
        
        # Gerar PDF
        arquivo_gerado = gerador.gerar_pdf_premium(exame, parametros, laudo, medico, nome_arquivo)
        
        logger.info(f"PDF premium gerado com sucesso: {arquivo_gerado}")
        return arquivo_gerado
        
    except Exception as e:
        logger.error(f"Erro na geração do PDF premium: {str(e)}")
        raise