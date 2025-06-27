#!/usr/bin/env python3
"""
Gerador de PDF - Layout da Segunda Foto
Reproduz exatamente o layout mostrado na segunda captura de tela
com separação entre dados antropométricos e medidas ecocardiográficas
"""

import io
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, white, blue
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

class PDFLayoutSegundaFoto:
    def __init__(self):
        """Inicializar gerador seguindo layout da segunda foto"""
        # Margens conforme modelo
        self.margem_esquerda = 20 * mm
        self.margem_direita = 20 * mm
        self.margem_superior = 15 * mm
        self.margem_inferior = 15 * mm
        
        # Largura útil
        self.largura_util = A4[0] - self.margem_esquerda - self.margem_direita

    def criar_estilos(self):
        """Criar estilos do documento"""
        styles = getSampleStyleSheet()
        
        # Título das seções com linha azul
        styles.add(ParagraphStyle(
            name='TituloSecaoComLinha',
            parent=styles['Normal'],
            fontSize=14,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=blue,
            borderPadding=8,
            leftIndent=0,
            rightIndent=0
        ))
        
        # Labels dos campos
        styles.add(ParagraphStyle(
            name='LabelCampo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=2,
            fontName='Helvetica'
        ))
        
        # Valores dos campos
        styles.add(ParagraphStyle(
            name='ValorCampo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        return styles

    def criar_cabecalho(self, styles):
        """Criar cabeçalho GRUPO VIDAH"""
        elementos = []
        
        # Título principal
        titulo_style = ParagraphStyle(
            'TituloPrincipal',
            parent=styles['Title'],
            fontSize=24,
            textColor=blue,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        elementos.append(Paragraph("GRUPO VIDAH", titulo_style))
        
        # Subtítulo
        subtitulo_style = ParagraphStyle(
            'SubtituloSistema',
            parent=styles['Normal'],
            fontSize=12,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica'
        )
        
        elementos.append(Paragraph("Sistema de Ecocardiograma", subtitulo_style))
        
        # Título do laudo
        titulo_laudo_style = ParagraphStyle(
            'TituloLaudo',
            parent=styles['Title'],
            fontSize=16,
            textColor=blue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        elementos.append(Paragraph("LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO", titulo_laudo_style))
        
        return elementos

    def criar_secao_dados_paciente(self, exame, styles):
        """Criar seção de dados do paciente conforme segunda foto"""
        elementos = []
        
        # Título da seção com linha azul
        titulo_com_linha = Paragraph("Dados do Paciente", styles['TituloSecaoComLinha'])
        elementos.append(titulo_com_linha)
        elementos.append(Spacer(1, 8))
        
        # Criar tabela de dados em duas colunas (conforme segunda foto)
        dados_tabela = [
            # Linha 1
            [
                Paragraph("Nome:", styles['LabelCampo']),
                Paragraph(exame.nome_paciente or "", styles['ValorCampo']),
                Paragraph("Médico Solicitante:", styles['LabelCampo']),
                Paragraph(exame.medico_solicitante or "", styles['ValorCampo'])
            ],
            # Linha 2 - espaçamento
            ["", "", "", ""],
            # Linha 3
            [
                Paragraph("Data de Nascimento:", styles['LabelCampo']),
                Paragraph(exame.data_nascimento or "dd/mm/aaaa", styles['ValorCampo']),
                Paragraph("Médico Examinador:", styles['LabelCampo']),
                Paragraph(exame.medico_usuario or "", styles['ValorCampo'])
            ],
            # Linha 4 - espaçamento
            ["", "", "", ""],
            # Linha 5
            [
                Paragraph("Idade:", styles['LabelCampo']),
                Paragraph(f"{exame.idade}" if exame.idade else "", styles['ValorCampo']),
                Paragraph("Convênio:", styles['LabelCampo']),
                Paragraph(exame.tipo_atendimento or "", styles['ValorCampo'])
            ],
            # Linha 6 - espaçamento
            ["", "", "", ""],
            # Linha 7
            [
                Paragraph("Sexo:", styles['LabelCampo']),
                Paragraph(exame.sexo or "Selecione", styles['ValorCampo']),
                Paragraph("Data do Exame:", styles['LabelCampo']),
                Paragraph(exame.data_exame or "dd/mm/aaaa", styles['ValorCampo'])
            ]
        ]
        
        tabela_dados = Table(dados_tabela, colWidths=[3*cm, 4.5*cm, 3.5*cm, 4*cm])
        tabela_dados.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elementos.append(tabela_dados)
        elementos.append(Spacer(1, 20))
        
        return elementos

    def criar_secao_dados_antropometricos(self, parametros, styles):
        """Criar seção de dados antropométricos separada (conforme segunda foto)"""
        elementos = []
        
        # Título da seção com linha azul
        titulo_com_linha = Paragraph("Dados Antropométricos", styles['TituloSecaoComLinha'])
        elementos.append(titulo_com_linha)
        elementos.append(Spacer(1, 8))
        
        # Dados antropométricos em linha horizontal (conforme segunda foto)
        dados_antropometricos = [
            [
                Paragraph("Peso (kg):", styles['LabelCampo']),
                Paragraph("Altura (cm):", styles['LabelCampo']),
                Paragraph("Superfície Corporal (m²):", styles['LabelCampo']),
                Paragraph("Frequência Cardíaca (bpm):", styles['LabelCampo'])
            ],
            [
                Paragraph(f"{parametros.peso}" if parametros and parametros.peso else "", styles['ValorCampo']),
                Paragraph(f"{parametros.altura}" if parametros and parametros.altura else "", styles['ValorCampo']),
                Paragraph(f"{parametros.superficie_corporal:.2f}" if parametros and parametros.superficie_corporal else "", styles['ValorCampo']),
                Paragraph(f"{parametros.frequencia_cardiaca}" if parametros and parametros.frequencia_cardiaca else "", styles['ValorCampo'])
            ]
        ]
        
        tabela_antropometricos = Table(dados_antropometricos, colWidths=[3.5*cm, 3.5*cm, 4.5*cm, 4*cm])
        tabela_antropometricos.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            # Bordas simples para os campos
            ('BOX', (0, 1), (0, 1), 0.5, colors.grey),
            ('BOX', (1, 1), (1, 1), 0.5, colors.grey),
            ('BOX', (2, 1), (2, 1), 0.5, colors.grey),
            ('BOX', (3, 1), (3, 1), 0.5, colors.grey),
        ]))
        
        elementos.append(tabela_antropometricos)
        elementos.append(Spacer(1, 20))
        
        return elementos

    def criar_secao_medidas_ecocardiograficas(self, parametros, styles):
        """Criar seção de medidas ecocardiográficas (separada dos dados antropométricos)"""
        elementos = []
        
        # Título da seção com linha azul
        titulo_com_linha = Paragraph("Medidas Ecocardiográficas", styles['TituloSecaoComLinha'])
        elementos.append(titulo_com_linha)
        elementos.append(Spacer(1, 8))
        
        if not parametros:
            elementos.append(Paragraph("Dados não disponíveis", styles['ValorCampo']))
            return elementos
        
        # Tabela de medidas ecocardiográficas
        dados_medidas = [
            ["Parâmetro", "Valor", "Unidade", "Valores de Referência"],
            
            # Medidas cardíacas básicas
            ["Átrio Esquerdo", f"{parametros.atrio_esquerdo or 'N/A'}", "mm", "27-38"],
            ["Raiz da Aorta", f"{parametros.raiz_aorta or 'N/A'}", "mm", "21-34"],
            ["Aorta Ascendente", f"{parametros.aorta_ascendente or 'N/A'}", "mm", "<38"],
            
            # Ventrículo esquerdo
            ["DDVE", f"{parametros.diametro_diastolico_final_ve or 'N/A'}", "mm", "35-56"],
            ["DSVE", f"{parametros.diametro_sistolico_final or 'N/A'}", "mm", "21-40"],
            ["Septo Interventricular", f"{parametros.espessura_diastolica_septo or 'N/A'}", "mm", "6-11"],
            ["Parede Posterior VE", f"{parametros.espessura_diastolica_ppve or 'N/A'}", "mm", "6-11"],
            
            # Função ventricular
            ["Fração de Ejeção", f"{parametros.fracao_ejecao or 'N/A'}", "%", "≥55"],
            ["Encurtamento Fracional", f"{parametros.percentual_encurtamento or 'N/A'}", "%", "25-45"],
            ["VDF", f"{parametros.volume_diastolico_final or 'N/A'}", "mL", "65-195"],
            ["VSF", f"{parametros.volume_sistolico_final or 'N/A'}", "mL", "22-58"],
            ["Massa VE", f"{parametros.massa_ve or 'N/A'}", "g", "67-162 (H), 55-141 (M)"]
        ]
        
        tabela_medidas = Table(dados_medidas, colWidths=[
            self.largura_util * 0.35,  # Parâmetro
            self.largura_util * 0.2,   # Valor
            self.largura_util * 0.15,  # Unidade
            self.largura_util * 0.3    # Referência
        ])
        
        # Estilo da tabela
        tabela_medidas.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Parâmetro - esquerda
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Outros - centro
            
            # Linhas alternadas
            ('BACKGROUND', (0, 1), (-1, 1), white),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('BACKGROUND', (0, 3), (-1, 3), white),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
            ('BACKGROUND', (0, 5), (-1, 5), white),
            ('BACKGROUND', (0, 6), (-1, 6), colors.lightgrey),
            ('BACKGROUND', (0, 7), (-1, 7), white),
            ('BACKGROUND', (0, 8), (-1, 8), colors.lightgrey),
            ('BACKGROUND', (0, 9), (-1, 9), white),
            ('BACKGROUND', (0, 10), (-1, 10), colors.lightgrey),
            ('BACKGROUND', (0, 11), (-1, 11), white),
            ('BACKGROUND', (0, 12), (-1, 12), colors.lightgrey),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, blue),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elementos.append(tabela_medidas)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_secoes_medicas(self, laudo, styles):
        """Criar seções médicas (laudos)"""
        elementos = []
        
        # Estilo para títulos de seções médicas
        titulo_medico_style = ParagraphStyle(
            'TituloMedico',
            parent=styles['Normal'],
            fontSize=12,
            textColor=blue,
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para conteúdo médico
        conteudo_medico_style = ParagraphStyle(
            'ConteudoMedico',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            fontName='Helvetica'
        )
        
        if not laudo:
            # Seções padrão se não houver laudo
            secoes = [
                ("MODO M E BIDIMENSIONAL", "Ventrículo esquerdo com dimensões e função sistólica preservadas. Análise da contratilidade segmentar e global dentro dos parâmetros de normalidade."),
                ("ESTUDO DOPPLER", "Fluxos valvulares avaliados pelo Doppler. Função diastólica preservada."),
                ("CONCLUSÃO", "Ecocardiograma transtorácico bidimensional com Doppler dentro dos parâmetros de normalidade.")
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
        """Criar seção de assinatura"""
        elementos = []
        
        elementos.append(Spacer(1, 20))
        
        # Estilo para assinatura
        assinatura_style = ParagraphStyle(
            'Assinatura',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica'
        )
        
        # Nome e CRM
        nome_medico = medico.nome if medico else "Michel Raineri Haddad"
        crm_medico = medico.crm if medico else "183299"
        
        medico_info = Paragraph(f"Médico Responsável: {nome_medico}", assinatura_style)
        elementos.append(medico_info)
        
        crm_info = Paragraph(f"CRM: {crm_medico}", assinatura_style)
        elementos.append(crm_info)
        elementos.append(Spacer(1, 15))
        
        # Linha de assinatura
        linha_assinatura = Paragraph("Assinatura: ________________________________________", assinatura_style)
        elementos.append(linha_assinatura)
        
        return elementos

    def gerar_pdf_layout_segunda_foto(self, exame, parametros, laudo, medico, nome_arquivo):
        """Gerar PDF seguindo exatamente o layout da segunda foto"""
        try:
            logger.info(f"🔄 Gerando PDF com layout da segunda foto para: {exame.nome_paciente}")
            
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
            styles = self.criar_estilos()
            
            # Elementos do documento
            elementos = []
            
            # 1. Cabeçalho
            elementos.extend(self.criar_cabecalho(styles))
            
            # 2. Dados do paciente (layout segunda foto)
            elementos.extend(self.criar_secao_dados_paciente(exame, styles))
            
            # 3. Dados antropométricos SEPARADOS (conforme segunda foto)
            elementos.extend(self.criar_secao_dados_antropometricos(parametros, styles))
            
            # 4. Medidas ecocardiográficas (separadas dos antropométricos)
            elementos.extend(self.criar_secao_medidas_ecocardiograficas(parametros, styles))
            
            # 5. Seções médicas (laudos)
            elementos.extend(self.criar_secoes_medicas(laudo, styles))
            
            # 6. Assinatura
            elementos.extend(self.criar_assinatura(medico, styles))
            
            # Gerar PDF
            doc.build(elementos)
            
            # Verificar tamanho do arquivo
            tamanho = os.path.getsize(nome_arquivo)
            logger.info(f"✅ PDF layout segunda foto gerado: {nome_arquivo} ({tamanho} bytes)")
            
            return nome_arquivo, tamanho
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do PDF layout segunda foto: {e}")
            raise e

def gerar_pdf_layout_segunda_foto(exame, medico_data):
    """Função principal para gerar PDF com layout da segunda foto"""
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
        gerador = PDFLayoutSegundaFoto()
        
        # Obter parâmetros e laudo
        parametros = exame.parametros
        laudo = exame.laudos[0] if exame.laudos else None
        
        # Criar objeto médico para compatibilidade
        class MedicoObj:
            def __init__(self, data):
                self.nome = data.get('nome', 'Michel Raineri Haddad')
                self.crm = data.get('crm', '183299')
                self.assinatura_data = data.get('assinatura_data')
        
        medico = MedicoObj(medico_data)
        
        # Gerar PDF
        arquivo_gerado, tamanho = gerador.gerar_pdf_layout_segunda_foto(
            exame, parametros, laudo, medico, nome_arquivo
        )
        
        return arquivo_gerado, tamanho
        
    except Exception as e:
        logger.error(f"❌ Erro na função principal: {e}")
        raise e