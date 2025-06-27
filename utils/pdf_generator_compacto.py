"""
Gerador de PDF Compacto - Máximo 2 Páginas A4
Design profissional com tabelas organizadas e layout condensado
"""

import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import black, white, lightgrey
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

logger = logging.getLogger(__name__)

class PDFCompacto:
    def __init__(self):
        """Gerador compacto para máximo 2 páginas A4"""
        # Margens mínimas para máximo aproveitamento
        self.margem_esquerda = 10*mm
        self.margem_direita = 10*mm
        self.margem_superior = 10*mm
        self.margem_inferior = 10*mm
        
        # Largura útil
        self.largura_util = A4[0] - self.margem_esquerda - self.margem_direita
        
        # Cores profissionais
        self.cor_titulo = colors.blue
        self.cor_subtitulo = colors.darkgrey
        self.cor_campo = lightgrey
        self.cor_borda = colors.grey
    
    def criar_estilos_compactos(self):
        """Criar estilos otimizados para layout compacto"""
        styles = getSampleStyleSheet()
        
        # Título principal - compacto para 2 páginas
        styles.add(ParagraphStyle(
            name='TituloCompacto',
            parent=styles['Heading1'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1A365D'),
            alignment=TA_CENTER,
            spaceAfter=6,
            spaceBefore=4,
            leading=16
        ))
        
        # Subtítulo das seções - espaçamento reduzido
        styles.add(ParagraphStyle(
            name='SubtituloSecao',
            parent=styles['Heading2'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2E5090'),
            alignment=TA_LEFT,
            spaceAfter=3,
            spaceBefore=6,
            leftIndent=2,
            leading=13
        ))
        
        # Label de campo - melhor legibilidade
        styles.add(ParagraphStyle(
            name='LabelCampo',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2D3748'),  # Cinza escuro profissional
            alignment=TA_LEFT,
            spaceAfter=2,
            leading=11
        ))
        
        # Valor de campo - fonte mais clara
        styles.add(ParagraphStyle(
            name='ValorCampo',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            textColor=colors.HexColor('#1A202C'),  # Preto suave
            alignment=TA_LEFT,
            spaceAfter=2,
            leading=12
        ))
        
        # Texto médico - formatação profissional
        styles.add(ParagraphStyle(
            name='TextoMedico',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            textColor=colors.HexColor('#2D3748'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            spaceBefore=4,
            leading=14,
            leftIndent=6,
            rightIndent=6
        ))
        
        # Assinatura médica - destaque especial
        styles.add(ParagraphStyle(
            name='AssinaturaMedica',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1A365D'),
            alignment=TA_CENTER,
            spaceAfter=6,
            spaceBefore=12,
            leading=16
        ))
        
        return styles
    
    def criar_cabecalho_compacto(self, styles):
        """Cabeçalho profissional com identidade visual moderna"""
        elementos = []
        
        # Header com logo e informações organizacionais
        header_data = [
            ['GRUPO VIDAH', '', 'Tel: (16) 3342-4768'],
            ['MEDICINA DIAGNÓSTICA', '', 'R. XV de Novembro, 594 - Centro'],
            ['', '', 'Ibitinga - SP, 14940-000']
        ]
        
        header_table = Table(header_data, colWidths=[6*cm, 6*cm, 6*cm])
        header_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (0, 1), 12),
            ('FONTSIZE', (2, 0), (2, 2), 8),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
            ('TEXTCOLOR', (0, 0), (0, 1), colors.HexColor('#1A365D')),
            ('TEXTCOLOR', (2, 0), (2, 2), colors.HexColor('#4A5568')),
            ('ALIGN', (0, 0), (0, 1), 'LEFT'),
            ('ALIGN', (2, 0), (2, 2), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(header_table)
        elementos.append(Spacer(1, 6))
        
        # Título principal centralizado e destacado
        titulo = Paragraph("<b>LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO</b>", styles['TituloCompacto'])
        elementos.append(titulo)
        
        # Linha decorativa com gradiente visual
        linha_decorativa = Table([[''] * 1], colWidths=[18*cm])
        linha_decorativa.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2E5090')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(Spacer(1, 3))
        elementos.append(linha_decorativa)
        elementos.append(Spacer(1, 8))
        
        return elementos
    
    def criar_tabela_dados_paciente(self, exame, styles):
        """Card de dados do paciente com design moderno"""
        elementos = []
        
        # Cabeçalho da seção com ícone
        titulo = Paragraph("📋 DADOS DO PACIENTE", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        # Card principal com informações essenciais
        info_principal = [
            ['PACIENTE:', getattr(exame, 'nome_paciente', '').upper()],
            ['NASCIMENTO:', getattr(exame, 'data_nascimento', '')],
            ['EXAME:', getattr(exame, 'data_exame', '')]
        ]
        
        card_principal = Table(info_principal, colWidths=[3*cm, 12*cm])
        card_principal.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2D3748')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        elementos.append(card_principal)
        elementos.append(Spacer(1, 3))
        
        # Informações complementares em linha
        info_complementar = [
            ['Idade:', f"{getattr(exame, 'idade', '')} anos" if getattr(exame, 'idade', None) else "",
             'Sexo:', getattr(exame, 'sexo', ''),
             'Tipo:', getattr(exame, 'tipo_atendimento', '')]
        ]
        
        tabela_complementar = Table(info_complementar, colWidths=[1.5*cm, 2.5*cm, 1.5*cm, 2.5*cm, 1.5*cm, 5.5*cm])
        tabela_complementar.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Labels em negrito
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Labels em negrito
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F7FAFC')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F7FAFC')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2D3748')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#2D3748')),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
        ]))
        
        elementos.append(tabela_complementar)
        elementos.append(Spacer(1, 3))
        
        # Indicação se existir
        indicacao = getattr(exame, 'indicacao', '')
        if indicacao:
            indicacao_dados = [['Indicação:', indicacao]]
            tabela_indicacao = Table(indicacao_dados, colWidths=[3*cm, 12*cm])
            tabela_indicacao.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
                ('BACKGROUND', (0, 0), (0, -1), self.cor_campo),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
            ]))
            elementos.append(tabela_indicacao)
            elementos.append(Spacer(1, 6))
        
        return elementos
    
    def criar_tabela_antropometricos(self, parametros, styles):
        """Dados antropométricos em linha horizontal"""
        if not parametros:
            return []
        
        elementos = []
        titulo = Paragraph("DADOS ANTROPOMÉTRICOS", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        # Tabela horizontal compacta
        dados = [
            ['Peso (kg)', 'Altura (cm)', 'SC (m²)', 'FC (bpm)'],
            [
                f"{getattr(parametros, 'peso', '')}" if getattr(parametros, 'peso', None) else "",
                f"{getattr(parametros, 'altura', '')}" if getattr(parametros, 'altura', None) else "",
                f"{getattr(parametros, 'superficie_corporal', ''):.2f}" if getattr(parametros, 'superficie_corporal', None) else "",
                f"{getattr(parametros, 'frequencia_cardiaca', '')}" if getattr(parametros, 'frequencia_cardiaca', None) else ""
            ]
        ]
        
        tabela_antro = Table(dados, colWidths=[3.75*cm, 3.75*cm, 3.75*cm, 3.75*cm])
        tabela_antro.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_campo),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3)
        ]))
        
        elementos.append(tabela_antro)
        elementos.append(Spacer(1, 4))
        
        return elementos
    
    def criar_medidas_basicas(self, parametros, styles):
        """📊 Medidas Ecocardiográficas Básicas com indicadores visuais"""
        if not parametros:
            return []
        
        elementos = []
        titulo = Paragraph("📊 MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        # Função para determinar status do valor
        def get_status_color(valor, min_normal, max_normal):
            if not valor or valor == 0:
                return colors.HexColor('#F7FAFC')  # Cinza claro para valores vazios
            if min_normal <= valor <= max_normal:
                return colors.HexColor('#F0FFF4')  # Verde claro para normal
            else:
                return colors.HexColor('#FFF5F5')  # Rosa claro para alterado
        
        # Calcular valores e status
        ae = getattr(parametros, 'atrio_esquerdo', 0)
        ao = getattr(parametros, 'raiz_aorta', 0)
        relacao_ae_ao = f"{ae/ao:.2f}" if ae and ao and ae != 0 and ao != 0 else ""
        
        dados = [
            ['PARÂMETRO', 'VALOR', 'STATUS', 'REFERÊNCIA NORMAL'],
            ['Átrio Esquerdo', f"{ae:.1f} mm" if ae and ae != 0 else "—", 
             "NORMAL" if ae and 27 <= ae <= 38 else "ALTERADO" if ae and ae != 0 else "—", '27-38 mm'],
            ['Raiz da Aorta', f"{ao:.1f} mm" if ao and ao != 0 else "—",
             "NORMAL" if ao and 21 <= ao <= 34 else "ALTERADO" if ao and ao != 0 else "—", '21-34 mm'],
            ['Relação AE/Ao', relacao_ae_ao if relacao_ae_ao else "—",
             "NORMAL" if relacao_ae_ao and float(relacao_ae_ao) < 1.5 else "ALTERADO" if relacao_ae_ao else "—", '< 1,5'],
            ['Aorta Ascendente', f"{getattr(parametros, 'aorta_ascendente', 0):.1f} mm" if getattr(parametros, 'aorta_ascendente', 0) else "—",
             "NORMAL" if getattr(parametros, 'aorta_ascendente', 0) and getattr(parametros, 'aorta_ascendente', 0) < 38 else "ALTERADO" if getattr(parametros, 'aorta_ascendente', 0) else "—", '< 38 mm'],
            ['Diâmetro VD', f"{getattr(parametros, 'diametro_ventricular_direito', 0):.1f} mm" if getattr(parametros, 'diametro_ventricular_direito', 0) else "—",
             "NORMAL" if getattr(parametros, 'diametro_ventricular_direito', 0) and 7 <= getattr(parametros, 'diametro_ventricular_direito', 0) <= 23 else "ALTERADO" if getattr(parametros, 'diametro_ventricular_direito', 0) else "—", '7-23 mm'],
            ['Diâmetro Basal VD', f"{getattr(parametros, 'diametro_basal_vd', 0):.1f} mm" if getattr(parametros, 'diametro_basal_vd', 0) else "—",
             "NORMAL" if getattr(parametros, 'diametro_basal_vd', 0) and 25 <= getattr(parametros, 'diametro_basal_vd', 0) <= 41 else "ALTERADO" if getattr(parametros, 'diametro_basal_vd', 0) else "—", '25-41 mm']
        ]
        
        tabela = Table(dados, colWidths=[6*cm, 3*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_campo),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10))
        return elementos
    
    def criar_ventriculo_esquerdo(self, parametros, styles):
        """2. Ventrículo Esquerdo"""
        if not parametros:
            return []
        
        elementos = []
        titulo = Paragraph("Ventrículo Esquerdo", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        # Calcular relação Septo/PP
        septo = getattr(parametros, 'espessura_diastolica_septo', None)
        pp = getattr(parametros, 'espessura_diastolica_ppve', None)
        relacao_septo_pp = ""
        if septo and pp and pp != 0:
            relacao_septo_pp = f"{septo/pp:.2f}"
        
        dados = [
            ['Parâmetro', 'Valor', 'Referência'],
            ['DDVE (mm)', f"{getattr(parametros, 'diametro_diastolico_final_ve', '')}" if getattr(parametros, 'diametro_diastolico_final_ve', None) else "", 'Normal: 35-56 mm'],
            ['DSVE (mm)', f"{getattr(parametros, 'diametro_sistolico_final', '')}" if getattr(parametros, 'diametro_sistolico_final', None) else "", 'Normal: 21-40 mm'],
            ['% Encurtamento', f"{getattr(parametros, 'percentual_encurtamento', '')}" if getattr(parametros, 'percentual_encurtamento', None) else "", 'Normal: 25-45%'],
            ['Septo (mm)', f"{septo}" if septo else "", 'Normal: 6-11 mm'],
            ['Parede Posterior (mm)', f"{pp}" if pp else "", 'Normal: 6-11 mm'],
            ['Relação Septo/PP', relacao_septo_pp, 'Normal: <1,3']
        ]
        
        tabela = Table(dados, colWidths=[6*cm, 3*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_campo),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10))
        return elementos
    
    def criar_volumes_funcao(self, parametros, styles):
        """3. Volumes e Função Sistólica"""
        if not parametros:
            return []
        
        elementos = []
        titulo = Paragraph("Volumes e Função Sistólica", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        # Calcular volume de ejeção
        vdf = getattr(parametros, 'volume_diastolico_final', None)
        vsf = getattr(parametros, 'volume_sistolico_final', None)
        volume_ejecao = ""
        if vdf and vsf:
            volume_ejecao = f"{vdf - vsf:.1f}"
        
        dados = [
            ['Parâmetro', 'Valor', 'Referência'],
            ['Volume Diastólico Final (mL)', f"{vdf}" if vdf else "", 'Normal: 67-155 mL'],
            ['Volume Sistólico Final (mL)', f"{vsf}" if vsf else "", 'Normal: 22-58 mL'],
            ['Volume de Ejeção (mL)', volume_ejecao, 'Calculado: VDF - VSF'],
            ['Fração de Ejeção (%)', f"{getattr(parametros, 'fracao_ejecao', '')}" if getattr(parametros, 'fracao_ejecao', None) else "", 'Normal: ≥55%'],
            ['Massa VE (g)', f"{getattr(parametros, 'massa_ve', '')}" if getattr(parametros, 'massa_ve', None) else "", 'Normal H: 88-224g, M: 67-162g'],
            ['Índice Massa VE (g/m²)', f"{getattr(parametros, 'indice_massa_ve', '')}" if getattr(parametros, 'indice_massa_ve', None) else "", 'Normal H: ≤115, M: ≤95 g/m²']
        ]
        
        tabela = Table(dados, colWidths=[6*cm, 3*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_campo),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10))
        return elementos
    
    def criar_velocidades_fluxos(self, parametros, styles):
        """4. Velocidades dos Fluxos"""
        if not parametros:
            return []
        
        elementos = []
        titulo = Paragraph("Velocidades dos Fluxos", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        dados = [
            ['Parâmetro', 'Valor', 'Referência'],
            ['Fluxo Pulmonar (m/s)', f"{getattr(parametros, 'fluxo_pulmonar', '')}" if getattr(parametros, 'fluxo_pulmonar', None) else "", 'Normal: 0,6-0,9 m/s'],
            ['Fluxo Mitral (m/s)', f"{getattr(parametros, 'fluxo_mitral', '')}" if getattr(parametros, 'fluxo_mitral', None) else "", 'Normal: 0,6-1,3 m/s'],
            ['Fluxo Aórtico (m/s)', f"{getattr(parametros, 'fluxo_aortico', '')}" if getattr(parametros, 'fluxo_aortico', None) else "", 'Normal: 1,0-1,7 m/s'],
            ['Fluxo Tricúspide (m/s)', f"{getattr(parametros, 'fluxo_tricuspide', '')}" if getattr(parametros, 'fluxo_tricuspide', None) else "", 'Normal: 0,3-0,7 m/s']
        ]
        
        tabela = Table(dados, colWidths=[6*cm, 3*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_campo),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10))
        return elementos
    
    def criar_gradientes(self, parametros, styles):
        """5. Gradientes"""
        if not parametros:
            return []
        
        elementos = []
        titulo = Paragraph("Gradientes", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        dados = [
            ['Parâmetro', 'Valor', 'Referência'],
            ['Gradiente VD→AP (mmHg)', f"{getattr(parametros, 'gradiente_vd_ap', '')}" if getattr(parametros, 'gradiente_vd_ap', None) else "", 'Normal: <10 mmHg'],
            ['Gradiente AE→VE (mmHg)', f"{getattr(parametros, 'gradiente_ae_ve', '')}" if getattr(parametros, 'gradiente_ae_ve', None) else "", 'Normal: <5 mmHg'],
            ['Gradiente VE→AO (mmHg)', f"{getattr(parametros, 'gradiente_ve_ao', '')}" if getattr(parametros, 'gradiente_ve_ao', None) else "", 'Normal: <10 mmHg'],
            ['Gradiente AD→VD (mmHg)', f"{getattr(parametros, 'gradiente_ad_vd', '')}" if getattr(parametros, 'gradiente_ad_vd', None) else "", 'Normal: <5 mmHg'],
            ['Gradiente IT (mmHg)', f"{getattr(parametros, 'gradiente_tricuspide', '')}" if getattr(parametros, 'gradiente_tricuspide', None) else "", 'Para cálculo da PSAP'],
            ['PSAP (mmHg)', f"{getattr(parametros, 'pressao_sistolica_vd', '')}" if getattr(parametros, 'pressao_sistolica_vd', None) else "", 'Normal: <35 mmHg']
        ]
        
        tabela = Table(dados, colWidths=[6*cm, 3*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_borda),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_campo),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10))
        return elementos
    
    def criar_secoes_medicas_compactas(self, laudo, styles):
        """Seções médicas em formato compacto"""
        if not laudo:
            return []
        
        elementos = []
        titulo = Paragraph("LAUDOS MÉDICOS", styles['SubtituloSecao'])
        elementos.append(titulo)
        
        # Modo M e Bidimensional
        modo_m_texto = getattr(laudo, 'modo_m_bidimensional', '') or "Dentro dos limites da normalidade"
        elementos.append(Paragraph(f"<b>Modo M e Bidimensional:</b> {modo_m_texto}", styles['TextoMedico']))
        
        # Doppler Convencional
        doppler_conv_texto = getattr(laudo, 'doppler_convencional', '') or "Fluxos dentro da normalidade"
        elementos.append(Paragraph(f"<b>Doppler Convencional:</b> {doppler_conv_texto}", styles['TextoMedico']))
        
        # Doppler Tecidual
        doppler_tec_texto = getattr(laudo, 'doppler_tecidual', '') or "Velocidades miocárdicas preservadas"
        elementos.append(Paragraph(f"<b>Doppler Tecidual:</b> {doppler_tec_texto}", styles['TextoMedico']))
        
        # Conclusão
        conclusao_texto = getattr(laudo, 'conclusao', '') or "Ecocardiograma dentro dos parâmetros normais"
        elementos.append(Paragraph(f"<b><font color='green'>Conclusão:</font></b> {conclusao_texto}", styles['TextoMedico']))
        
        elementos.append(Spacer(1, 12))
        
        return elementos
    
    def criar_assinatura_compacta(self, medico, styles):
        """Assinatura médica compacta com dados reais do sistema"""
        elementos = []
        
        # Espaçamento
        elementos.append(Spacer(1, 15))
        
        # Dados do médico do sistema
        nome_medico = getattr(medico, 'nome', 'Michel Raineri Haddad') if medico else 'Michel Raineri Haddad'
        crm_medico = getattr(medico, 'crm', 'CRM-SP 123456') if medico else 'CRM-SP 123456'
        
        # Verificar se há assinatura digital cadastrada
        assinatura_data = getattr(medico, 'assinatura_data', None) if medico else None
        assinatura_url = getattr(medico, 'assinatura_url', None) if medico else None
        
        assinatura_style = ParagraphStyle(
            name='AssinaturaCompacta',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=3
        )
        
        # Se há assinatura digital cadastrada, incluir no PDF
        if assinatura_data or assinatura_url:
            try:
                # Tentar incluir a assinatura digital
                if assinatura_data:
                    # Decodificar base64 da assinatura
                    import base64
                    import io
                    from reportlab.lib.utils import ImageReader
                    
                    # Remover prefixo data:image se presente
                    if ',' in assinatura_data:
                        assinatura_data = assinatura_data.split(',')[1]
                    
                    # Decodificar base64
                    assinatura_bytes = base64.b64decode(assinatura_data)
                    assinatura_img = ImageReader(io.BytesIO(assinatura_bytes))
                    
                    # Adicionar imagem da assinatura
                    from reportlab.platypus import Image
                    img_assinatura = Image(assinatura_img, width=4*cm, height=2*cm)
                    img_assinatura.hAlign = 'CENTER'
                    elementos.append(img_assinatura)
                    
                elif assinatura_url:
                    # Se há URL da assinatura, tentar incluir
                    from reportlab.platypus import Image
                    img_assinatura = Image(assinatura_url, width=4*cm, height=2*cm)
                    img_assinatura.hAlign = 'CENTER'
                    elementos.append(img_assinatura)
                    
            except Exception as e:
                logger.warning(f"Erro ao incluir assinatura digital: {e}")
                # Fallback para linha de assinatura simples
                elementos.append(Paragraph("_" * 40, assinatura_style))
        else:
            # Linha de assinatura simples
            elementos.append(Paragraph("_" * 40, assinatura_style))
        
        # Nome e CRM do médico com design elegante
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(f"<b>{nome_medico}</b>", styles['AssinaturaMedica']))
        elementos.append(Paragraph(crm_medico, styles['AssinaturaMedica']))
        elementos.append(Spacer(1, 6))
        
        return elementos
    
    def gerar_pdf_compacto(self, exame, parametros, laudo, medico, nome_arquivo):
        """Gerar PDF compacto em máximo 2 páginas"""
        try:
            logger.info(f"Gerando PDF compacto para: {getattr(exame, 'nome_paciente', 'Paciente')}")
            
            # Configurar documento
            doc = SimpleDocTemplate(
                nome_arquivo,
                pagesize=A4,
                leftMargin=self.margem_esquerda,
                rightMargin=self.margem_direita,
                topMargin=self.margem_superior,
                bottomMargin=self.margem_inferior
            )
            
            # Criar estilos
            styles = self.criar_estilos_compactos()
            
            # Elementos do documento
            elementos = []
            
            # 1. Cabeçalho
            elementos.extend(self.criar_cabecalho_compacto(styles))
            
            # 2. Dados do paciente
            elementos.extend(self.criar_tabela_dados_paciente(exame, styles))
            
            # 3. Dados antropométricos
            elementos.extend(self.criar_tabela_antropometricos(parametros, styles))
            
            # 4. Medidas Ecocardiográficas Básicas
            elementos.extend(self.criar_medidas_basicas(parametros, styles))
            
            # 5. Ventrículo Esquerdo
            elementos.extend(self.criar_ventriculo_esquerdo(parametros, styles))
            
            # 6. Volumes e Função Sistólica
            elementos.extend(self.criar_volumes_funcao(parametros, styles))
            
            # 7. Velocidades dos Fluxos
            elementos.extend(self.criar_velocidades_fluxos(parametros, styles))
            
            # 8. Gradientes
            elementos.extend(self.criar_gradientes(parametros, styles))
            
            # 6. Laudos médicos
            elementos.extend(self.criar_secoes_medicas_compactas(laudo, styles))
            
            # 7. Assinatura
            elementos.extend(self.criar_assinatura_compacta(medico, styles))
            
            # Gerar PDF
            doc.build(elementos)
            
            # Verificar tamanho
            tamanho = os.path.getsize(nome_arquivo)
            logger.info(f"PDF compacto gerado: {nome_arquivo} ({tamanho} bytes)")
            
            return nome_arquivo, tamanho
            
        except Exception as e:
            logger.error(f"Erro na geração do PDF compacto: {e}")
            raise e

def gerar_pdf_compacto(exame, medico_data):
    """Função principal para gerar PDF compacto"""
    try:
        # Diretório de PDFs
        pdf_dir = "generated_pdfs"
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Nome do arquivo
        data_formatada = datetime.now().strftime("%d%m%Y")
        nome_arquivo = os.path.join(
            pdf_dir, 
            f"laudo_compacto_{getattr(exame, 'nome_paciente', 'paciente').replace(' ', '_')}_{data_formatada}.pdf"
        )
        
        # Criar gerador
        gerador = PDFCompacto()
        
        # Garantir que temos os dados do exame do banco de dados
        from app import db
        from models import ParametrosEcocardiograma, LaudoEcocardiograma
        
        # Recarregar o exame com todos os relacionamentos
        if hasattr(exame, 'id'):
            db.session.refresh(exame)
        
        # Sempre buscar dados diretamente do banco para garantir dados atualizados
        parametros = ParametrosEcocardiograma.query.filter_by(exame_id=exame.id).first()
        laudo = LaudoEcocardiograma.query.filter_by(exame_id=exame.id).first()
        
        # Debug detalhado dos dados encontrados
        if parametros:
            logger.info(f"Parâmetros carregados: peso={parametros.peso}, altura={parametros.altura}, AE={parametros.atrio_esquerdo}, FE={parametros.fracao_ejecao}")
        else:
            logger.warning(f"Nenhum parâmetro encontrado para exame {exame.id}")
            
        if laudo:
            logger.info(f"Laudo carregado: conclusao={laudo.conclusao[:50] if laudo.conclusao else 'vazio'}...")
        else:
            logger.warning(f"Nenhum laudo encontrado para exame {exame.id}")
        
        # Criar objeto médico com dados completos
        class MedicoObj:
            def __init__(self, data):
                if data and isinstance(data, dict):
                    self.nome = data.get('nome', 'Michel Raineri Haddad')
                    self.crm = data.get('crm', 'CRM-SP 183299')
                    self.assinatura_data = data.get('assinatura_data')
                    self.assinatura_url = data.get('assinatura_url')
                else:
                    self.nome = 'Michel Raineri Haddad'
                    self.crm = 'CRM-SP 183299'
                    self.assinatura_data = None
                    self.assinatura_url = None
        
        medico = MedicoObj(medico_data)
        
        logger.info(f"Gerando PDF para: {exame.nome_paciente}")
        logger.info(f"Parâmetros encontrados: {parametros is not None}")
        logger.info(f"Laudo encontrado: {laudo is not None}")
        logger.info(f"Médico: {medico.nome} ({medico.crm})")
        
        # Gerar PDF
        arquivo_gerado, tamanho = gerador.gerar_pdf_compacto(
            exame, parametros, laudo, medico, nome_arquivo
        )
        
        return arquivo_gerado, tamanho
        
    except Exception as e:
        logger.error(f"Erro na função principal: {e}")
        raise e
