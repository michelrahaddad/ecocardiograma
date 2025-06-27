#!/usr/bin/env python3
"""
Gerador de PDF - Design Moderno com Caixas Editáveis
Reproduz exatamente o layout da primeira imagem fornecida
"""

import io
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, white, blue, lightgrey
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image as PILImage
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFDesignModerno:
    def __init__(self):
        """Inicializar gerador com design moderno e caixas editáveis"""
        # Margens otimizadas
        self.margem_esquerda = 15 * mm
        self.margem_direita = 15 * mm
        self.margem_superior = 15 * mm
        self.margem_inferior = 15 * mm
        
        # Largura útil
        self.largura_util = A4[0] - self.margem_esquerda - self.margem_direita
        
        # Cores do design moderno
        self.cor_azul_titulo = colors.HexColor('#2E5BBA')
        self.cor_cinza_claro = colors.HexColor('#F8F9FA')
        self.cor_borda = colors.HexColor('#DEE2E6')

    def criar_estilos(self):
        """Criar estilos modernos do documento"""
        styles = getSampleStyleSheet()
        
        # Título das seções com borda azul moderna
        styles.add(ParagraphStyle(
            name='TituloSecaoModerno',
            parent=styles['Normal'],
            fontSize=12,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=self.cor_azul_titulo,
            borderPadding=8,
            backColor=white,
            leftIndent=5,
            rightIndent=5
        ))
        
        # Labels dos campos modernos
        styles.add(ParagraphStyle(
            name='LabelModerno',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6C757D'),
            alignment=TA_LEFT,
            spaceAfter=2,
            fontName='Helvetica'
        ))
        
        # Valores em caixas editáveis padronizadas
        styles.add(ParagraphStyle(
            name='ValorCaixa',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica',
            borderWidth=1,
            borderColor=self.cor_borda,
            borderPadding=8,
            backColor=self.cor_cinza_claro,
            leftIndent=4,
            rightIndent=4
        ))
        
        # Valores para campos maiores (indicação)
        styles.add(ParagraphStyle(
            name='ValorCaixaGrande',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica',
            borderWidth=1,
            borderColor=self.cor_borda,
            borderPadding=8,
            backColor=self.cor_cinza_claro,
            leftIndent=4,
            rightIndent=4
        ))
        
        # Texto médico para laudos
        styles.add(ParagraphStyle(
            name='TextoMedico',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica',
            leftIndent=10,
            rightIndent=10
        ))
        
        return styles

    def criar_cabecalho(self, styles):
        """Criar cabeçalho limpo e moderno"""
        elementos = []
        
        # Título principal
        titulo_style = ParagraphStyle(
            'TituloPrincipal',
            parent=styles['Title'],
            fontSize=20,
            textColor=self.cor_azul_titulo,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        elementos.append(Paragraph("GRUPO VIDAH", titulo_style))
        
        # Subtítulo
        subtitulo_style = ParagraphStyle(
            'SubtituloSistema',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        elementos.append(Paragraph("Sistema de Ecocardiograma", subtitulo_style))
        
        # Título do laudo
        titulo_laudo_style = ParagraphStyle(
            'TituloLaudo',
            parent=styles['Title'],
            fontSize=14,
            textColor=self.cor_azul_titulo,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        elementos.append(Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", titulo_laudo_style))
        
        return elementos

    def criar_secao_dados_paciente(self, exame, styles):
        """Criar seção de dados do paciente com layout padronizado e homogêneo"""
        elementos = []
        
        # Título da seção com borda azul
        titulo_dados = Paragraph("Dados do Paciente", styles['TituloSecaoModerno'])
        elementos.append(titulo_dados)
        elementos.append(Spacer(1, 8))
        
        # Layout padronizado em 2 colunas com caixas homogêneas
        dados_tabela = [
            # Linha 1 - Nome e Médico Solicitante
            [
                Paragraph("Nome:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'nome_paciente', '') or "", styles['ValorCaixa']),
                Paragraph("Médico Solicitante:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'medico_solicitante', '') or "", styles['ValorCaixa'])
            ],
            # Linha 2 - Data Nascimento e Médico Responsável
            [
                Paragraph("Data de Nascimento:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'data_nascimento', '') or "", styles['ValorCaixa']),
                Paragraph("Médico Responsável:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'medico_usuario', '') or "", styles['ValorCaixa'])
            ],
            # Linha 3 - Idade e Convênio
            [
                Paragraph("Idade:", styles['LabelModerno']),
                Paragraph(f"{getattr(exame, 'idade', '')}" if getattr(exame, 'idade', None) else "", styles['ValorCaixa']),
                Paragraph("Convênio:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'tipo_atendimento', '') or "", styles['ValorCaixa'])
            ],
            # Linha 4 - Sexo e Data do Exame
            [
                Paragraph("Sexo:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'sexo', '') or "", styles['ValorCaixa']),
                Paragraph("Data do Exame:", styles['LabelModerno']),
                Paragraph(getattr(exame, 'data_exame', '') or "", styles['ValorCaixa'])
            ],
            # Linha 5 - Indicação do Exame (span 2 colunas)
            [
                Paragraph("Indicação do Exame:", styles['LabelModerno']),
                "",
                "",
                ""
            ],
            [
                Paragraph(getattr(exame, 'indicacao', '') or "", styles['ValorCaixaGrande']),
                "",
                "",
                ""
            ]
        ]
        
        # Tabela com colunas padronizadas e homogêneas
        tabela_dados = Table(dados_tabela, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm], rowHeights=[12*mm, 12*mm, 12*mm, 12*mm, 8*mm, 15*mm])
        tabela_dados.setStyle(TableStyle([
            # Alinhamento e fonte
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            
            # Padding padronizado para todas as células
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Span para indicação do exame (linha 5 e 6)
            ('SPAN', (0, 4), (3, 4)),  # Label da indicação
            ('SPAN', (0, 5), (3, 5)),  # Valor da indicação
            
            # Espaçamento entre linhas
            ('TOPPADDING', (0, 4), (-1, 4), 10),  # Espaço antes da indicação
            
            # Bordas sutis para separar seções
            ('LINEBELOW', (0, 3), (-1, 3), 0.5, self.cor_borda),  # Linha após dados básicos
        ]))
        
        elementos.append(tabela_dados)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secao_dados_antropometricos(self, parametros, styles):
        """Criar seção de dados antropométricos com layout padronizado e homogêneo"""
        elementos = []
        
        # Título da seção com borda azul
        titulo_antropometricos = Paragraph("Dados Antropométricos", styles['TituloSecaoModerno'])
        elementos.append(titulo_antropometricos)
        elementos.append(Spacer(1, 8))
        
        # Layout horizontal padronizado com caixas homogêneas
        dados_antropometricos = [
            # Labels uniformemente espaçados
            [
                Paragraph("Peso (kg):", styles['LabelModerno']),
                Paragraph("Altura (cm):", styles['LabelModerno']),
                Paragraph("Superfície Corporal (m²):", styles['LabelModerno']),
                Paragraph("Frequência Cardíaca (bpm):", styles['LabelModerno'])
            ],
            # Caixas editáveis com tamanho padronizado
            [
                Paragraph(f"{parametros.peso}" if parametros and parametros.peso else "", styles['ValorCaixa']),
                Paragraph(f"{parametros.altura}" if parametros and parametros.altura else "", styles['ValorCaixa']),
                Paragraph(f"{parametros.superficie_corporal:.2f}" if parametros and parametros.superficie_corporal else "", styles['ValorCaixa']),
                Paragraph(f"{parametros.frequencia_cardiaca}" if parametros and parametros.frequencia_cardiaca else "", styles['ValorCaixa'])
            ]
        ]
        
        # Tabela com colunas e alturas padronizadas (mesmo tamanho das outras seções)
        tabela_antropometricos = Table(dados_antropometricos, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm], rowHeights=[8*mm, 12*mm])
        tabela_antropometricos.setStyle(TableStyle([
            # Alinhamento e fonte padronizados
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            
            # Padding padronizado (mesmo das outras seções)
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Alinhamento centralizado para dados numéricos
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            
            # Bordas sutis para homogeneidade visual
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, self.cor_borda),  # Linha após labels
        ]))
        
        elementos.append(tabela_antropometricos)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_caixa_parametro(self, label, valor, unidade, referencia, styles):
        """Criar uma caixa individual para cada parâmetro"""
        dados_caixa = [
            [Paragraph(f"{label} ({unidade})", styles['LabelModerno'])],
            [Paragraph(str(valor) if valor else "", styles['ValorCaixa'])],
            [Paragraph(f"Normal: {referencia}", styles['LabelModerno'])]
        ]
        
        tabela_caixa = Table(dados_caixa, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_caixa.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return tabela_caixa

    def criar_secao_medidas_basicas(self, parametros, styles):
        """Criar seção Medidas Ecocardiográficas Básicas"""
        elementos = []
        
        titulo = Paragraph("Medidas Ecocardiográficas Básicas", styles['TituloSecaoModerno'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        if not parametros:
            return elementos
        
        # Átrio Esquerdo
        elementos.append(self.criar_caixa_parametro("Átrio Esquerdo", parametros.atrio_esquerdo, "mm", "27-38 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # Raiz da Aorta
        elementos.append(self.criar_caixa_parametro("Raiz da Aorta", parametros.raiz_aorta, "mm", "21-34 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # Relação AE/Ao (calculada)
        relacao_ae_ao = ""
        if parametros.atrio_esquerdo and parametros.raiz_aorta:
            relacao_ae_ao = f"{parametros.atrio_esquerdo / parametros.raiz_aorta:.2f}"
        
        dados_relacao = [
            [Paragraph("Relação AE/Ao", styles['LabelModerno'])],
            [Paragraph(relacao_ae_ao, styles['ValorCaixa'])],
            [Paragraph("Normal: <1,5", styles['LabelModerno'])]
        ]
        
        tabela_relacao = Table(dados_relacao, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_relacao.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_relacao)
        elementos.append(Spacer(1, 8))
        
        # Aorta Ascendente
        elementos.append(self.criar_caixa_parametro("Aorta Ascendente", parametros.aorta_ascendente, "mm", "<38 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # Diâmetro VD
        elementos.append(self.criar_caixa_parametro("Diâmetro VD", parametros.diametro_ventricular_direito, "mm", "7-23 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # Diâmetro Basal VD
        elementos.append(self.criar_caixa_parametro("Diâmetro Basal VD", parametros.diametro_basal_vd, "mm", "25-41 mm", styles))
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secao_ventriculo_esquerdo(self, parametros, styles):
        """Criar seção Ventrículo Esquerdo"""
        elementos = []
        
        titulo = Paragraph("Ventrículo Esquerdo", styles['TituloSecaoModerno'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        if not parametros:
            return elementos
        
        # DDVE
        elementos.append(self.criar_caixa_parametro("DDVE", parametros.diametro_diastolico_final_ve, "mm", "35-56 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # DSVE
        elementos.append(self.criar_caixa_parametro("DSVE", parametros.diametro_sistolico_final, "mm", "21-40 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # % Encurtamento (calculado)
        dados_encurtamento = [
            [Paragraph("% Encurtamento", styles['LabelModerno'])],
            [Paragraph(f"{parametros.percentual_encurtamento}" if parametros.percentual_encurtamento else "", styles['ValorCaixa'])],
            [Paragraph("Normal: 25-45%", styles['LabelModerno'])]
        ]
        
        tabela_encurtamento = Table(dados_encurtamento, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_encurtamento.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_encurtamento)
        elementos.append(Spacer(1, 8))
        
        # Septo
        elementos.append(self.criar_caixa_parametro("Septo", parametros.espessura_diastolica_septo, "mm", "6-11 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # Parede Posterior
        elementos.append(self.criar_caixa_parametro("Parede Posterior", parametros.espessura_diastolica_ppve, "mm", "6-11 mm", styles))
        elementos.append(Spacer(1, 8))
        
        # Relação Septo/PP (calculada)
        relacao_septo_pp = ""
        if parametros.espessura_diastolica_septo and parametros.espessura_diastolica_ppve:
            relacao_septo_pp = f"{parametros.espessura_diastolica_septo / parametros.espessura_diastolica_ppve:.2f}"
        
        dados_relacao_septo = [
            [Paragraph("Relação Septo/PP", styles['LabelModerno'])],
            [Paragraph(relacao_septo_pp, styles['ValorCaixa'])],
            [Paragraph("Normal: <1,3", styles['LabelModerno'])]
        ]
        
        tabela_relacao_septo = Table(dados_relacao_septo, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_relacao_septo.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_relacao_septo)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secao_volumes_funcao(self, parametros, styles):
        """Criar seção Volumes e Função Sistólica"""
        elementos = []
        
        titulo = Paragraph("Volumes e Função Sistólica", styles['TituloSecaoModerno'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        if not parametros:
            return elementos
        
        # Volume Diastólico Final
        elementos.append(self.criar_caixa_parametro("Volume Diastólico Final", parametros.volume_diastolico_final, "mL", "67-155 mL", styles))
        elementos.append(Spacer(1, 8))
        
        # Volume Sistólico Final
        elementos.append(self.criar_caixa_parametro("Volume Sistólico Final", parametros.volume_sistolico_final, "mL", "22-58 mL", styles))
        elementos.append(Spacer(1, 8))
        
        # Volume de Ejeção (calculado)
        volume_ejecao = ""
        if parametros.volume_diastolico_final and parametros.volume_sistolico_final:
            volume_ejecao = f"{parametros.volume_diastolico_final - parametros.volume_sistolico_final:.1f}"
        
        dados_vol_ejecao = [
            [Paragraph("Volume de Ejeção (mL)", styles['LabelModerno'])],
            [Paragraph(volume_ejecao, styles['ValorCaixa'])],
            [Paragraph("Calculado: VDF - VSF", styles['LabelModerno'])]
        ]
        
        tabela_vol_ejecao = Table(dados_vol_ejecao, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_vol_ejecao.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_vol_ejecao)
        elementos.append(Spacer(1, 8))
        
        # Fração de Ejeção (calculada)
        dados_fe = [
            [Paragraph("Fração de Ejeção (%)", styles['LabelModerno'])],
            [Paragraph(f"{parametros.fracao_ejecao}" if parametros.fracao_ejecao else "", styles['ValorCaixa'])],
            [Paragraph("Normal: ≥55%", styles['LabelModerno'])]
        ]
        
        tabela_fe = Table(dados_fe, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_fe.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_fe)
        elementos.append(Spacer(1, 8))
        
        # Massa VE
        elementos.append(self.criar_caixa_parametro("Massa VE", parametros.massa_ve, "g", "H: 88-224g, M: 67-162g", styles))
        elementos.append(Spacer(1, 8))
        
        # Índice Massa VE (calculado)
        indice_massa_ve = ""
        if parametros.massa_ve and parametros.superficie_corporal:
            indice_massa_ve = f"{parametros.massa_ve / parametros.superficie_corporal:.1f}"
        
        dados_indice_massa = [
            [Paragraph("Índice Massa VE (g/m²)", styles['LabelModerno'])],
            [Paragraph(indice_massa_ve, styles['ValorCaixa'])],
            [Paragraph("Normal H: ≤115, M: ≤95 g/m²", styles['LabelModerno'])]
        ]
        
        tabela_indice_massa = Table(dados_indice_massa, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_indice_massa.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_indice_massa)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secao_velocidades_fluxos(self, parametros, styles):
        """Criar seção Velocidades dos Fluxos"""
        elementos = []
        
        titulo = Paragraph("Velocidades dos Fluxos", styles['TituloSecaoModerno'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        if not parametros:
            return elementos
        
        # Fluxo Pulmonar
        elementos.append(self.criar_caixa_parametro("Fluxo Pulmonar", parametros.fluxo_pulmonar, "m/s", "0,6-0,9 m/s", styles))
        elementos.append(Spacer(1, 8))
        
        # Fluxo Mitral
        elementos.append(self.criar_caixa_parametro("Fluxo Mitral", parametros.fluxo_mitral, "m/s", "0,6-1,3 m/s", styles))
        elementos.append(Spacer(1, 8))
        
        # Fluxo Aórtico
        elementos.append(self.criar_caixa_parametro("Fluxo Aórtico", parametros.fluxo_aortico, "m/s", "1,0-1,7 m/s", styles))
        elementos.append(Spacer(1, 8))
        
        # Fluxo Tricúspide
        elementos.append(self.criar_caixa_parametro("Fluxo Tricúspide", parametros.fluxo_tricuspide, "m/s", "0,3-0,7 m/s", styles))
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secao_gradientes(self, parametros, styles):
        """Criar seção Gradientes"""
        elementos = []
        
        titulo = Paragraph("Gradientes", styles['TituloSecaoModerno'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        if not parametros:
            return elementos
        
        # Gradiente VD→AP
        elementos.append(self.criar_caixa_parametro("Gradiente VD→AP", parametros.gradiente_vd_ap, "mmHg", "<10 mmHg", styles))
        elementos.append(Spacer(1, 8))
        
        # Gradiente AE→VE
        elementos.append(self.criar_caixa_parametro("Gradiente AE→VE", parametros.gradiente_ae_ve, "mmHg", "<5 mmHg", styles))
        elementos.append(Spacer(1, 8))
        
        # Gradiente VE→AO
        elementos.append(self.criar_caixa_parametro("Gradiente VE→AO", parametros.gradiente_ve_ao, "mmHg", "<10 mmHg", styles))
        elementos.append(Spacer(1, 8))
        
        # Gradiente AD→VD
        elementos.append(self.criar_caixa_parametro("Gradiente AD→VD", parametros.gradiente_ad_vd, "mmHg", "<5 mmHg", styles))
        elementos.append(Spacer(1, 8))
        
        # Gradiente IT
        elementos.append(self.criar_caixa_parametro("Gradiente IT", parametros.gradiente_tricuspide, "mmHg", "Para cálculo da PSAP", styles))
        elementos.append(Spacer(1, 8))
        
        # PSAP (calculada)
        dados_psap = [
            [Paragraph("PSAP (mmHg)", styles['LabelModerno'])],
            [Paragraph(f"{parametros.pressao_sistolica_vd}" if parametros.pressao_sistolica_vd else "", styles['ValorCaixa'])],
            [Paragraph("Normal: <35 mmHg", styles['LabelModerno'])]
        ]
        
        tabela_psap = Table(dados_psap, colWidths=[7*cm], rowHeights=[8*mm, 12*mm, 6*mm])
        tabela_psap.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Campo calculado
        ]))
        
        elementos.append(tabela_psap)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secoes_medicas_finais(self, laudo, styles):
        """Criar seções médicas finais (Modo M, Doppler, Conclusão)"""
        elementos = []
        
        # Modo M e Bidimensional
        titulo_modo_m = Paragraph("Modo M e Bidimensional:", styles['TituloSecaoModerno'])
        elementos.append(titulo_modo_m)
        elementos.append(Spacer(1, 6))
        
        texto_modo_m = laudo.modo_m_bidimensional if laudo and laudo.modo_m_bidimensional else "None"
        paragrafo_modo_m = Paragraph(texto_modo_m, styles['TextoMedico'])
        elementos.append(paragrafo_modo_m)
        elementos.append(Spacer(1, 12))
        
        # Doppler Convencional
        titulo_doppler_conv = Paragraph("Doppler Convencional:", styles['TituloSecaoModerno'])
        elementos.append(titulo_doppler_conv)
        elementos.append(Spacer(1, 6))
        
        texto_doppler_conv = laudo.doppler_convencional if laudo and laudo.doppler_convencional else "None"
        paragrafo_doppler_conv = Paragraph(texto_doppler_conv, styles['TextoMedico'])
        elementos.append(paragrafo_doppler_conv)
        elementos.append(Spacer(1, 12))
        
        # Doppler Tecidual
        titulo_doppler_tec = Paragraph("Doppler Tecidual:", styles['TituloSecaoModerno'])
        elementos.append(titulo_doppler_tec)
        elementos.append(Spacer(1, 6))
        
        texto_doppler_tec = laudo.doppler_tecidual if laudo and laudo.doppler_tecidual else "None"
        paragrafo_doppler_tec = Paragraph(texto_doppler_tec, styles['TextoMedico'])
        elementos.append(paragrafo_doppler_tec)
        elementos.append(Spacer(1, 12))
        
        # Conclusão (com cor verde)
        conclusao_style = ParagraphStyle(
            name='ConclusaoVerde',
            parent=styles['TituloSecaoModerno'],
            textColor=colors.darkgreen,
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        
        titulo_conclusao = Paragraph("Conclusão:", conclusao_style)
        elementos.append(titulo_conclusao)
        elementos.append(Spacer(1, 6))
        
        texto_conclusao = laudo.conclusao if laudo and laudo.conclusao else "None"
        paragrafo_conclusao = Paragraph(texto_conclusao, styles['TextoMedico'])
        elementos.append(paragrafo_conclusao)
        elementos.append(Spacer(1, 20))
        
        return elementos

    def criar_assinatura_centralizada(self, medico, styles):
        """Criar seção de assinatura centralizada"""
        elementos = []
        
        # Espaçamento antes da assinatura
        elementos.append(Spacer(1, 30))
        
        # Estilo para assinatura centralizada
        assinatura_centralizada_style = ParagraphStyle(
            name='AssinaturaCentralizada',
            parent=styles['Normal'],
            fontSize=11,
            textColor=black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        
        crm_centralizado_style = ParagraphStyle(
            name='CRMCentralizado',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=15
        )
        
        # Nome do médico centralizado
        nome_medico = medico.nome if medico and medico.nome else "Michel Raineri Haddad"
        elementos.append(Paragraph(nome_medico, assinatura_centralizada_style))
        
        # CRM centralizado
        crm_medico = medico.crm if medico and medico.crm else "CRM-SP 123456"
        elementos.append(Paragraph(crm_medico, crm_centralizado_style))
        
        # Assinatura digital centralizada (se disponível)
        if medico and medico.assinatura_data:
            try:
                import base64
                from PIL import Image
                import io
                
                # Decodificar assinatura base64
                assinatura_bytes = base64.b64decode(medico.assinatura_data)
                assinatura_img = Image.open(io.BytesIO(assinatura_bytes))
                
                # Salvar temporariamente para usar no PDF
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    assinatura_img.save(temp_file.name, 'PNG')
                    
                    # Adicionar imagem centralizada
                    from reportlab.platypus import Image as RLImage
                    img_assinatura = RLImage(temp_file.name, width=4*cm, height=2*cm)
                    
                    # Centralizar a imagem
                    img_centralizada = Table([[img_assinatura]], colWidths=[self.largura_util])
                    img_centralizada.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                    ]))
                    
                    elementos.append(img_centralizada)
                    
            except Exception as e:
                logger.warning(f"Erro ao processar assinatura digital: {e}")
                # Fallback para linha de assinatura
                elementos.append(Paragraph("_________________________", crm_centralizado_style))
        else:
            # Linha de assinatura padrão
            elementos.append(Paragraph("_________________________", crm_centralizado_style))
        
        return elementos

    def criar_secoes_medicas(self, laudo, styles):
        """Criar seções médicas com design moderno"""
        elementos = []
        
        # Estilo para títulos médicos
        titulo_medico_style = ParagraphStyle(
            'TituloMedicoModerno',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.cor_azul_titulo,
            alignment=TA_LEFT,
            spaceAfter=6,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para conteúdo médico
        conteudo_medico_style = ParagraphStyle(
            'ConteudoMedicoModerno',
            parent=styles['Normal'],
            fontSize=9,
            textColor=black,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName='Helvetica',
            borderWidth=1,
            borderColor=self.cor_borda,
            borderPadding=6,
            backColor=self.cor_cinza_claro
        )
        
        if not laudo:
            # Seções padrão modernas
            secoes = [
                ("MODO M E BIDIMENSIONAL", "Análise ecocardiográfica realizada em modo M e bidimensional com avaliação das dimensões e função ventricular."),
                ("ESTUDO DOPPLER", "Estudo Doppler colorido e pulsado para avaliação dos fluxos valvulares e função diastólica."),
                ("CONCLUSÃO", "Ecocardiograma transtorácico com parâmetros dentro da normalidade para idade e biotipo.")
            ]
        else:
            secoes = []
            if laudo.modo_m_bidimensional:
                secoes.append(("MODO M E BIDIMENSIONAL", laudo.modo_m_bidimensional))
            if laudo.doppler_convencional:
                secoes.append(("ESTUDO DOPPLER", laudo.doppler_convencional))
            if laudo.conclusao:
                secoes.append(("CONCLUSÃO", laudo.conclusao))
        
        for titulo, conteudo in secoes:
            elementos.append(Paragraph(titulo, titulo_medico_style))
            elementos.append(Paragraph(conteudo, conteudo_medico_style))
        
        return elementos

    def criar_assinatura(self, medico, styles):
        """Criar seção de assinatura moderna"""
        elementos = []
        
        elementos.append(Spacer(1, 15))
        
        # Estilo moderno para assinatura
        assinatura_style = ParagraphStyle(
            'AssinaturaModerna',
            parent=styles['Normal'],
            fontSize=9,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=3,
            fontName='Helvetica'
        )
        
        # Nome e CRM
        nome_medico = medico.nome if medico else "Michel Raineri Haddad"
        crm_medico = medico.crm if medico else "183299"
        
        elementos.append(Paragraph(f"Médico Responsável: {nome_medico}", assinatura_style))
        elementos.append(Paragraph(f"CRM: {crm_medico}", assinatura_style))
        elementos.append(Spacer(1, 10))
        
        # Linha de assinatura moderna
        elementos.append(Paragraph("Assinatura: ________________________", assinatura_style))
        
        return elementos

    def gerar_pdf_design_moderno(self, exame, parametros, laudo, medico, nome_arquivo):
        """Gerar PDF com design moderno seguindo estrutura das imagens fornecidas"""
        try:
            logger.info(f"🔄 Gerando PDF com design moderno para: {exame.nome_paciente}")
            
            # Configurar documento com margens otimizadas
            doc = SimpleDocTemplate(
                nome_arquivo,
                pagesize=A4,
                leftMargin=self.margem_esquerda,
                rightMargin=self.margem_direita,
                topMargin=self.margem_superior,
                bottomMargin=self.margem_inferior
            )
            
            # Criar estilos modernos
            styles = self.criar_estilos()
            
            # Elementos do documento
            elementos = []
            
            # 1. Cabeçalho moderno
            elementos.extend(self.criar_cabecalho(styles))
            
            # 2. Dados do paciente com caixas editáveis
            elementos.extend(self.criar_secao_dados_paciente(exame, styles))
            
            # 3. Dados antropométricos com layout horizontal moderno
            elementos.extend(self.criar_secao_dados_antropometricos(parametros, styles))
            
            # 4. Medidas Ecocardiográficas Básicas (seguindo imagem 1)
            elementos.extend(self.criar_secao_medidas_basicas(parametros, styles))
            
            # 5. Ventrículo Esquerdo (seguindo imagem 2)
            elementos.extend(self.criar_secao_ventriculo_esquerdo(parametros, styles))
            
            # 6. Volumes e Função Sistólica (seguindo imagem 3)
            elementos.extend(self.criar_secao_volumes_funcao(parametros, styles))
            
            # 7. Velocidades dos Fluxos (seguindo imagem 4)
            elementos.extend(self.criar_secao_velocidades_fluxos(parametros, styles))
            
            # 8. Gradientes (seguindo imagem 5)
            elementos.extend(self.criar_secao_gradientes(parametros, styles))
            
            # 9. Seções médicas finais (seguindo imagem 6)
            elementos.extend(self.criar_secoes_medicas_finais(laudo, styles))
            
            # 10. Assinatura centralizada
            elementos.extend(self.criar_assinatura_centralizada(medico, styles))
            
            # Gerar PDF
            doc.build(elementos)
            
            # Verificar tamanho
            tamanho = os.path.getsize(nome_arquivo)
            logger.info(f"✅ PDF design moderno gerado: {nome_arquivo} ({tamanho} bytes)")
            
            return nome_arquivo, tamanho
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do PDF design moderno: {e}")
            raise e

def gerar_pdf_design_moderno(exame, medico_data):
    """Função principal para gerar PDF com design moderno"""
    try:
        # Diretório de PDFs
        pdf_dir = "generated_pdfs"
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Nome do arquivo
        data_formatada = datetime.now().strftime("%d%m%Y")
        nome_arquivo = os.path.join(
            pdf_dir, 
            f"laudo_eco_{exame.nome_paciente.replace(' ', '_')}_{data_formatada}.pdf"
        )
        
        # Criar gerador
        gerador = PDFDesignModerno()
        
        # Obter parâmetros e laudo com fallback
        parametros = getattr(exame, 'parametros', None)
        laudos = getattr(exame, 'laudos', [])
        laudo = laudos[0] if laudos else None
        
        # Criar objeto médico
        class MedicoObj:
            def __init__(self, data):
                self.nome = data.get('nome', 'Michel Raineri Haddad')
                self.crm = data.get('crm', '183299')
                self.assinatura_data = data.get('assinatura_data')
        
        medico = MedicoObj(medico_data)
        
        # Gerar PDF
        arquivo_gerado, tamanho = gerador.gerar_pdf_design_moderno(
            exame, parametros, laudo, medico, nome_arquivo
        )
        
        return arquivo_gerado, tamanho
        
    except Exception as e:
        logger.error(f"❌ Erro na função principal: {e}")
        raise e