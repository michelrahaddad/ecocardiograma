#!/usr/bin/env python3
"""
Gerador de PDF com Layout Customizado - Reprodução Exata do Modelo Fornecido
Sistema adaptado para preencher automaticamente todos os parâmetros ecocardiográficos
"""

import io
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, white, Color
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

class PDFLayoutCustom:
    def __init__(self):
        """Inicializar gerador de PDF com layout customizado"""
        self.cor_azul_cabecalho = Color(0.2, 0.4, 0.8)  # Azul similar ao modelo
        self.cor_cinza_claro = Color(0.95, 0.95, 0.95)
        self.cor_texto_normal = Color(0.2, 0.2, 0.2)
        
        # Margens padrão em mm
        self.margem_esquerda = 15 * mm
        self.margem_direita = 15 * mm
        self.margem_superior = 15 * mm
        self.margem_inferior = 15 * mm
        
        # Largura útil
        self.largura_util = A4[0] - self.margem_esquerda - self.margem_direita

    def criar_estilos(self):
        """Criar estilos customizados baseados no modelo"""
        styles = getSampleStyleSheet()
        
        # Estilo do cabeçalho principal
        styles.add(ParagraphStyle(
            name='CabecalhoPrincipal',
            parent=styles['Title'],
            fontSize=18,
            textColor=self.cor_azul_cabecalho,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo do subtítulo
        styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.cor_azul_cabecalho,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica'
        ))
        
        # Estilo para dados do paciente
        styles.add(ParagraphStyle(
            name='DadosPaciente',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=4,
            fontName='Helvetica'
        ))
        
        # Estilo para seções
        styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=styles['Normal'],
            fontSize=11,
            textColor=white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            backColor=self.cor_azul_cabecalho,
            borderPadding=4
        ))
        
        # Estilo para texto de conteúdo
        styles.add(ParagraphStyle(
            name='ConteudoSecao',
            parent=styles['Normal'],
            fontSize=9,
            textColor=black,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            fontName='Helvetica',
            leading=12
        ))
        
        # Estilo para assinatura
        styles.add(ParagraphStyle(
            name='Assinatura',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        return styles

    def criar_cabecalho(self, styles):
        """Criar cabeçalho do documento seguindo o modelo"""
        elementos = []
        
        # Logo e título principal
        titulo = Paragraph("GRUPO VIDAH", styles['CabecalhoPrincipal'])
        elementos.append(titulo)
        
        subtitulo = Paragraph("Medicina Diagnóstica", styles['Subtitulo'])
        elementos.append(subtitulo)
        
        # Linha separadora
        elementos.append(HRFlowable(width="100%", thickness=1, color=self.cor_azul_cabecalho))
        elementos.append(Spacer(1, 8))
        
        # Título do exame
        titulo_exame = Paragraph("<b>LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO</b>", styles['CabecalhoPrincipal'])
        elementos.append(titulo_exame)
        elementos.append(Spacer(1, 12))
        
        return elementos

    def criar_dados_paciente(self, exame, styles):
        """Criar seção de dados do paciente seguindo layout do modelo"""
        elementos = []
        
        # Título da seção
        titulo_secao = Paragraph("DADOS DO PACIENTE", styles['TituloSecao'])
        elementos.append(titulo_secao)
        elementos.append(Spacer(1, 6))
        
        # Dados em formato de tabela 2x3 como no modelo
        dados_tabela = [
            [f"Nome: {exame.nome_paciente}", f"Idade: {exame.idade} anos"],
            [f"Data de Nascimento: {exame.data_nascimento}", f"Sexo: {exame.sexo}"],
            [f"Data do Exame: {exame.data_exame}", f"Médico: {exame.medico_usuario or 'Dr. Michel Raineri Haddad'}"]
        ]
        
        tabela_dados = Table(dados_tabela, colWidths=[self.largura_util/2, self.largura_util/2])
        tabela_dados.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza_claro),
            ('BACKGROUND', (0, 0), (-1, -1), white),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        elementos.append(tabela_dados)
        elementos.append(Spacer(1, 12))
        
        return elementos

    def criar_parametros_ecocardiograficos(self, parametros, styles):
        """Criar seção de parâmetros ecocardiográficos seguindo modelo"""
        elementos = []
        
        if not parametros:
            return elementos
        
        # Título da seção
        titulo_secao = Paragraph("PARÂMETROS ECOCARDIOGRÁFICOS", styles['TituloSecao'])
        elementos.append(titulo_secao)
        elementos.append(Spacer(1, 6))
        
        # Organizar dados em seções como no modelo
        
        # 1. Dados Antropométricos
        dados_antropometricos = [
            ["DADOS ANTROPOMÉTRICOS", "", ""],
            ["Peso", f"{parametros.peso or 'N/A'} kg", ""],
            ["Altura", f"{parametros.altura or 'N/A'} m", ""],
            ["Superfície Corporal", f"{parametros.superficie_corporal or 'N/A'} m²", ""],
            ["Frequência Cardíaca", f"{parametros.frequencia_cardiaca or 'N/A'} bpm", ""]
        ]
        
        # 2. Medidas do Ventrículo Esquerdo
        medidas_ve = [
            ["MEDIDAS DO VENTRÍCULO ESQUERDO", "", ""],
            ["DDVE", f"{parametros.diametro_diastolico_final_ve or 'N/A'} mm", "35-56 mm"],
            ["DSVE", f"{parametros.diametro_sistolico_final or 'N/A'} mm", "21-40 mm"],
            ["Septo Interventricular", f"{parametros.espessura_diastolica_septo or 'N/A'} mm", "6-11 mm"],
            ["Parede Posterior", f"{parametros.espessura_diastolica_ppve or 'N/A'} mm", "6-11 mm"],
            ["% Encurtamento", f"{parametros.percentual_encurtamento or 'N/A'}%", "25-45%"]
        ]
        
        # 3. Volumes e Função Sistólica
        volumes_funcao = [
            ["VOLUMES E FUNÇÃO SISTÓLICA", "", ""],
            ["Volume Diastólico Final", f"{parametros.volume_diastolico_final or 'N/A'} mL", "67-155 mL"],
            ["Volume Sistólico Final", f"{parametros.volume_sistolico_final or 'N/A'} mL", "22-58 mL"],
            ["Fração de Ejeção", f"{parametros.fracao_ejecao or 'N/A'}%", "≥55%"],
            ["Massa VE", f"{parametros.massa_ve or 'N/A'} g", ""],
            ["Índice Massa VE", f"{parametros.indice_massa_ve or 'N/A'} g/m²", ""]
        ]
        
        # 4. Outras Estruturas
        outras_estruturas = [
            ["OUTRAS ESTRUTURAS", "", ""],
            ["Átrio Esquerdo", f"{parametros.atrio_esquerdo or 'N/A'} mm", "27-38 mm"],
            ["Raiz da Aorta", f"{parametros.raiz_aorta or 'N/A'} mm", "21-34 mm"],
            ["Aorta Ascendente", f"{parametros.aorta_ascendente or 'N/A'} mm", "<38 mm"],
            ["Ventrículo Direito", f"{parametros.diametro_ventricular_direito or 'N/A'} mm", "7-23 mm"]
        ]
        
        # Criar tabelas para cada seção
        for dados_secao in [dados_antropometricos, medidas_ve, volumes_funcao, outras_estruturas]:
            tabela = Table(dados_secao, colWidths=[self.largura_util*0.4, self.largura_util*0.3, self.largura_util*0.3])
            
            # Estilo da tabela
            tabela.setStyle(TableStyle([
                # Cabeçalho da seção
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('BACKGROUND', (0, 0), (-1, 0), self.cor_azul_cabecalho),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('SPAN', (0, 0), (-1, 0)),
                
                # Dados
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TEXTCOLOR', (0, 1), (-1, -1), black),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Bordas
                ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza_claro),
                ('LINEBELOW', (0, 0), (-1, 0), 1, self.cor_azul_cabecalho),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
            ]))
            
            elementos.append(tabela)
            elementos.append(Spacer(1, 8))
        
        return elementos

    def criar_laudos_medicos(self, laudo, styles):
        """Criar seção de laudos médicos seguindo modelo"""
        elementos = []
        
        if not laudo:
            return elementos
        
        # Seções de laudo médico
        secoes_laudo = [
            ("MODO M E BIDIMENSIONAL", laudo.modo_m_bidimensional),
            ("DOPPLER CONVENCIONAL", laudo.doppler_convencional), 
            ("DOPPLER TECIDUAL", laudo.doppler_tecidual),
            ("CONCLUSÃO", laudo.conclusao)
        ]
        
        for titulo, conteudo in secoes_laudo:
            if conteudo and conteudo.strip():
                # Título da seção
                titulo_secao = Paragraph(titulo, styles['TituloSecao'])
                elementos.append(titulo_secao)
                elementos.append(Spacer(1, 4))
                
                # Conteúdo
                conteudo_formatado = Paragraph(conteudo, styles['ConteudoSecao'])
                elementos.append(conteudo_formatado)
                elementos.append(Spacer(1, 8))
        
        return elementos

    def criar_assinatura_digital(self, medico, styles):
        """Criar seção de assinatura digital seguindo modelo"""
        elementos = []
        
        elementos.append(Spacer(1, 20))
        
        # Data do laudo
        data_atual = datetime.now().strftime("%d/%m/%Y")
        data_laudo = Paragraph(f"Ibitinga, {data_atual}", styles['Assinatura'])
        elementos.append(data_laudo)
        elementos.append(Spacer(1, 15))
        
        # Processar assinatura se disponível
        if medico and medico.assinatura_data:
            try:
                # Decodificar assinatura
                assinatura_bytes = base64.b64decode(medico.assinatura_data)
                assinatura_img = PILImage.open(io.BytesIO(assinatura_bytes))
                
                # Redimensionar mantendo proporção
                largura_max = 120
                altura_max = 60
                assinatura_img.thumbnail((largura_max, altura_max), PILImage.Resampling.LANCZOS)
                
                # Converter para ReportLab
                img_buffer = io.BytesIO()
                assinatura_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                assinatura_rl = Image(img_buffer, width=assinatura_img.width, height=assinatura_img.height)
                
                # Centralizar assinatura
                tabela_assinatura = Table([[assinatura_rl]], colWidths=[self.largura_util])
                tabela_assinatura.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE')
                ]))
                
                elementos.append(tabela_assinatura)
                elementos.append(Spacer(1, 8))
                
            except Exception as e:
                logger.warning(f"Erro ao processar assinatura digital: {e}")
        
        # Nome e CRM do médico
        nome_medico = medico.nome if medico else "Dr. Michel Raineri Haddad"
        crm_medico = medico.crm if medico else "CRM-SP 987654"
        
        medico_info = Paragraph(f"<b>{nome_medico}</b><br/>{crm_medico}", styles['Assinatura'])
        elementos.append(medico_info)
        elementos.append(Spacer(1, 10))
        
        # Linha para assinatura (caso não haja digital)
        if not (medico and medico.assinatura_data):
            elementos.append(HRFlowable(width="200", thickness=1, color=black))
            elementos.append(Spacer(1, 5))
            medico_info = Paragraph(f"{nome_medico} - {crm_medico}", styles['Assinatura'])
            elementos.append(medico_info)
        
        return elementos

    def gerar_pdf_customizado(self, exame, parametros, laudo, medico, nome_arquivo):
        """Gerar PDF com layout customizado seguindo modelo fornecido"""
        try:
            logger.info(f"🔄 Iniciando geração de PDF customizado para: {exame.nome_paciente}")
            
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
            
            # 2. Dados do paciente
            elementos.extend(self.criar_dados_paciente(exame, styles))
            
            # 3. Parâmetros ecocardiográficos
            elementos.extend(self.criar_parametros_ecocardiograficos(parametros, styles))
            
            # 4. Laudos médicos
            elementos.extend(self.criar_laudos_medicos(laudo, styles))
            
            # 5. Assinatura digital
            elementos.extend(self.criar_assinatura_digital(medico, styles))
            
            # Gerar PDF
            doc.build(elementos)
            
            # Verificar tamanho do arquivo
            tamanho = os.path.getsize(nome_arquivo)
            logger.info(f"✅ PDF customizado gerado com sucesso: {nome_arquivo} ({tamanho} bytes)")
            
            return nome_arquivo, tamanho
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do PDF customizado: {e}")
            raise e

def gerar_pdf_layout_custom(exame, parametros=None, laudo=None, medico=None):
    """Função principal para gerar PDF com layout customizado"""
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
        gerador = PDFLayoutCustom()
        
        # Gerar PDF
        arquivo_gerado, tamanho = gerador.gerar_pdf_customizado(
            exame, parametros, laudo, medico, nome_arquivo
        )
        
        return arquivo_gerado, tamanho
        
    except Exception as e:
        logger.error(f"❌ Erro na função principal de geração: {e}")
        raise e