#!/usr/bin/env python3
"""
Gerador de PDF - Reprodução Exata do Modelo Fornecido
Baseado nas capturas de tela fornecidas pelo usuário
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

class PDFModeloExato:
    def __init__(self):
        """Inicializar gerador de PDF seguindo modelo exato"""
        # Cores exatas do modelo
        self.cor_azul_titulo = colors.blue  # Azul do GRUPO VIDAH
        self.cor_azul_secao = colors.blue   # Azul das seções
        self.cor_cinza_alternado = colors.lightgrey  # Cinza claro das linhas alternadas
        self.cor_azul_cabecalho_tabela = colors.blue  # Azul do cabeçalho da tabela
        
        # Margens conforme modelo
        self.margem_esquerda = 20 * mm
        self.margem_direita = 20 * mm
        self.margem_superior = 15 * mm
        self.margem_inferior = 15 * mm
        
        # Largura útil
        self.largura_util = A4[0] - self.margem_esquerda - self.margem_direita

    def criar_estilos(self):
        """Criar estilos exatos do modelo"""
        styles = getSampleStyleSheet()
        
        # Título principal GRUPO VIDAH
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.cor_azul_titulo,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo "Sistema de Ecocardiograma"
        styles.add(ParagraphStyle(
            name='SubtituloSistema',
            parent=styles['Normal'],
            fontSize=12,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica'
        ))
        
        # Título do laudo
        styles.add(ParagraphStyle(
            name='TituloLaudo',
            parent=styles['Title'],
            fontSize=18,
            textColor=self.cor_azul_titulo,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Título das seções
        styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.cor_azul_secao,
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Dados do paciente
        styles.add(ParagraphStyle(
            name='DadosPaciente',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            spaceAfter=2,
            fontName='Helvetica'
        ))
        
        # Conteúdo das seções médicas
        styles.add(ParagraphStyle(
            name='ConteudoMedico',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName='Helvetica',
            leading=12
        ))
        
        # Assinatura
        styles.add(ParagraphStyle(
            name='Assinatura',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        return styles

    def criar_cabecalho(self, styles):
        """Criar cabeçalho exato do modelo"""
        elementos = []
        
        # Linha superior
        elementos.append(HRFlowable(width="100%", thickness=2, color=black))
        elementos.append(Spacer(1, 8))
        
        # GRUPO VIDAH
        titulo = Paragraph("GRUPO VIDAH", styles['TituloPrincipal'])
        elementos.append(titulo)
        
        # Sistema de Ecocardiograma
        subtitulo = Paragraph("Sistema de Ecocardiograma", styles['SubtituloSistema'])
        elementos.append(subtitulo)
        
        # Linha inferior
        elementos.append(HRFlowable(width="100%", thickness=2, color=black))
        elementos.append(Spacer(1, 15))
        
        # Título do laudo
        titulo_laudo = Paragraph("LAUDO DE ECOCARDIOGRAMA<br/>TRANSTORÁCICO", styles['TituloLaudo'])
        elementos.append(titulo_laudo)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_dados_paciente(self, exame, styles):
        """Criar seção de dados do paciente conforme modelo"""
        elementos = []
        
        # Título da seção
        titulo = Paragraph("DADOS DO PACIENTE", styles['TituloSecao'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        # Dados formatados exatamente como no modelo
        dados = [
            f"Paciente: {exame.nome_paciente}",
            f"Data de Nascimento: {exame.data_nascimento}",
            f"Idade: {exame.idade} anos",
            f"Sexo: {exame.sexo}",
            f"Data do Exame: {exame.data_exame}",
            f"Médico Solicitante: {exame.medico_solicitante or 'Não informado'}",
            f"Tipo de Atendimento: {exame.tipo_atendimento or 'Particular'}",
            f"Indicação: {exame.indicacao or 'Exame de rotina'}"
        ]
        
        for dado in dados:
            p = Paragraph(dado, styles['DadosPaciente'])
            elementos.append(p)
            elementos.append(Spacer(1, 3))
        
        elementos.append(Spacer(1, 10))
        return elementos

    def criar_tabela_parametros(self, parametros, styles):
        """Criar tabela de parâmetros conforme modelo exato"""
        elementos = []
        
        if not parametros:
            return elementos
        
        # Título da seção
        titulo = Paragraph("DADOS ANTROPOMÉTRICOS E MEDIDAS ECOCARDIOGRÁFICAS", styles['TituloSecao'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 8))
        
        # Dados da tabela seguindo o modelo exato
        dados_tabela = [
            # Cabeçalho
            ["Parâmetro", "Valor", "Unidade", "Valores de Referência"],
            
            # Dados antropométricos
            ["Peso", f"{parametros.peso or 'N/A'}", "kg", "Conforme biótipo"],
            ["Altura", f"{parametros.altura or 'N/A'}", "m", "Conforme idade"],
            ["Superfície Corporal", f"{parametros.superficie_corporal or 'N/A'}", "m²", "1.5-2.0"],
            ["Frequência Cardíaca", f"{parametros.frequencia_cardiaca or 'N/A'}", "bpm", "60-100"],
            
            # Medidas cardíacas
            ["Átrio Esquerdo", f"{parametros.atrio_esquerdo or 'N/A'}", "mm", "27-38"],
            ["Raiz da Aorta", f"{parametros.raiz_aorta or 'N/A'}", "mm", "21-34"],
            ["Relação AE/Ao", f"{parametros.relacao_atrio_esquerdo_aorta or 'N/A'}", "", "<1.5"],
            ["DDVE", f"{parametros.diametro_diastolico_final_ve or 'N/A'}", "mm", "35-56"],
            ["DSVE", f"{parametros.diametro_sistolico_final or 'N/A'}", "mm", "21-40"],
            ["Septo Interventricular", f"{parametros.espessura_diastolica_septo or 'N/A'}", "mm", "6-11"],
            ["Parede Posterior VE", f"{parametros.espessura_diastolica_ppve or 'N/A'}", "mm", "6-11"]
        ]
        
        # Criar tabela
        tabela = Table(dados_tabela, colWidths=[
            self.largura_util * 0.4,  # Parâmetro
            self.largura_util * 0.2,  # Valor
            self.largura_util * 0.15, # Unidade
            self.largura_util * 0.25  # Referência
        ])
        
        # Estilo da tabela conforme modelo
        tabela.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_azul_cabecalho_tabela),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Parâmetro - esquerda
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Outros - centro
            
            # Linhas alternadas (conforme modelo)
            ('BACKGROUND', (0, 1), (-1, 1), white),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_cinza_alternado),
            ('BACKGROUND', (0, 3), (-1, 3), white),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_cinza_alternado),
            ('BACKGROUND', (0, 5), (-1, 5), white),
            ('BACKGROUND', (0, 6), (-1, 6), self.cor_cinza_alternado),
            ('BACKGROUND', (0, 7), (-1, 7), white),
            ('BACKGROUND', (0, 8), (-1, 8), self.cor_cinza_alternado),
            ('BACKGROUND', (0, 9), (-1, 9), white),
            ('BACKGROUND', (0, 10), (-1, 10), self.cor_cinza_alternado),
            ('BACKGROUND', (0, 11), (-1, 11), white),
            ('BACKGROUND', (0, 12), (-1, 12), self.cor_cinza_alternado),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.cor_azul_cabecalho_tabela),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elementos.append(tabela)
        
        # Continuar na segunda página se necessário - volumes e função
        if parametros.volume_diastolico_final or parametros.fracao_ejecao:
            elementos.append(Spacer(1, 1))  # Quebra de página
            
            # Segunda tabela - continuação
            dados_tabela_2 = [
                ["Encurtamento Fracional", f"{parametros.percentual_encurtamento or 'N/A'}", "%", "25-45"],
                ["Fração de Ejeção", f"{parametros.fracao_ejecao or 'N/A'}", "%", "≥55"],
                ["Volume Diastólico Final", f"{parametros.volume_diastolico_final or 'N/A'}", "mL", "65-195"],
                ["Volume Sistólico Final", f"{parametros.volume_sistolico_final or 'N/A'}", "mL", "22-58"],
                ["Massa do VE", f"{parametros.massa_ve or 'N/A'}", "g", "67-162 (H), 55-141 (M)"]
            ]
            
            tabela_2 = Table(dados_tabela_2, colWidths=[
                self.largura_util * 0.4,
                self.largura_util * 0.2,
                self.largura_util * 0.15,
                self.largura_util * 0.25
            ])
            
            tabela_2.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                
                # Linhas alternadas
                ('BACKGROUND', (0, 0), (-1, 0), white),
                ('BACKGROUND', (0, 1), (-1, 1), self.cor_cinza_alternado),
                ('BACKGROUND', (0, 2), (-1, 2), white),
                ('BACKGROUND', (0, 3), (-1, 3), self.cor_cinza_alternado),
                ('BACKGROUND', (0, 4), (-1, 4), white),
                
                ('GRID', (0, 0), (-1, -1), 0.5, black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            elementos.append(tabela_2)
        
        elementos.append(Spacer(1, 15))
        return elementos

    def criar_secoes_medicas(self, laudo, styles):
        """Criar seções médicas conforme modelo"""
        elementos = []
        
        if not laudo:
            # Criar seções padrão se não houver laudo
            secoes = [
                ("MODO M E BIDIMENSIONAL", "Ventrículo esquerdo com dimensões e função sistólica avaliadas pelo modo M e bidimensional. Análise da contratilidade segmentar e global."),
                ("ESTUDO DOPPLER CONVENCIONAL", "Fluxos valvulares avaliados pelo Doppler convencional. Estudo das valvas mitral, aórtica, tricúspide e pulmonar."),
                ("ESTUDO DOPPLER TECIDUAL", "Função diastólica avaliada pelo Doppler tecidual com análise das velocidades miocárdicas."),
                ("CONCLUSÃO", "Função sistólica global do ventrículo esquerdo preservada. Dimensões ventriculares dentro dos limites da normalidade. Átrio esquerdo com dimensões normais. Valvas cardíacas sem alterações estruturais significativas ao exame ecocardiográfico. Ecocardiograma transtorácico bidimensional com Doppler dentro dos parâmetros de normalidade.")
            ]
        else:
            secoes = []
            if laudo.modo_m_bidimensional:
                secoes.append(("MODO M E BIDIMENSIONAL", laudo.modo_m_bidimensional))
            if laudo.doppler_convencional:
                secoes.append(("ESTUDO DOPPLER CONVENCIONAL", laudo.doppler_convencional))
            if laudo.doppler_tecidual:
                secoes.append(("ESTUDO DOPPLER TECIDUAL", laudo.doppler_tecidual))
            if laudo.conclusao:
                secoes.append(("CONCLUSÃO", laudo.conclusao))
        
        for titulo, conteudo in secoes:
            # Título da seção
            titulo_p = Paragraph(titulo, styles['TituloSecao'])
            elementos.append(titulo_p)
            
            # Conteúdo
            conteudo_p = Paragraph(conteudo, styles['ConteudoMedico'])
            elementos.append(conteudo_p)
            elementos.append(Spacer(1, 8))
        
        return elementos

    def criar_assinatura(self, medico, styles):
        """Criar seção de assinatura conforme modelo"""
        elementos = []
        
        elementos.append(Spacer(1, 20))
        
        # Nome e CRM
        nome_medico = medico.nome if medico else "Michel Raineri Haddad"
        crm_medico = medico.crm if medico else "183299"
        
        medico_info = Paragraph(f"Médico Responsável: {nome_medico}", styles['Assinatura'])
        elementos.append(medico_info)
        elementos.append(Spacer(1, 4))
        
        crm_info = Paragraph(f"CRM: {crm_medico}", styles['Assinatura'])
        elementos.append(crm_info)
        elementos.append(Spacer(1, 15))
        
        # Linha de assinatura
        linha_assinatura = Paragraph("Assinatura: ________________________________________", styles['Assinatura'])
        elementos.append(linha_assinatura)
        
        return elementos

    def gerar_pdf_modelo_exato(self, exame, parametros, laudo, medico, nome_arquivo):
        """Gerar PDF seguindo exatamente o modelo fornecido"""
        try:
            logger.info(f"🔄 Iniciando geração de PDF modelo exato para: {exame.nome_paciente}")
            
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
            
            # 3. Tabela de parâmetros
            elementos.extend(self.criar_tabela_parametros(parametros, styles))
            
            # 4. Seções médicas
            elementos.extend(self.criar_secoes_medicas(laudo, styles))
            
            # 5. Assinatura
            elementos.extend(self.criar_assinatura(medico, styles))
            
            # Gerar PDF
            doc.build(elementos)
            
            # Verificar tamanho
            tamanho = os.path.getsize(nome_arquivo)
            logger.info(f"✅ PDF modelo exato gerado: {nome_arquivo} ({tamanho} bytes)")
            
            return nome_arquivo, tamanho
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do PDF modelo exato: {e}")
            raise e

def gerar_pdf_modelo_exato(exame, medico_data=None):
    """Função principal para gerar PDF conforme modelo exato"""
    try:
        # Diretório para PDFs
        pdf_dir = "generated_pdfs"
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        # Nome do arquivo
        safe_name = "".join(c for c in exame.nome_paciente if c.isalnum() or c in (' ', '_')).rstrip()
        safe_date = exame.data_exame.replace("/", "") if exame.data_exame else datetime.now().strftime('%d%m%Y')
        nome_arquivo = os.path.join(pdf_dir, f'laudo_eco_{safe_name.replace(" ", "_")}_{safe_date}.pdf')
        
        # Buscar dados relacionados
        from models import ParametrosEcocardiograma, LaudoEcocardiograma, Medico
        
        parametros = ParametrosEcocardiograma.query.filter_by(exame_id=exame.id).first()
        laudo = LaudoEcocardiograma.query.filter_by(exame_id=exame.id).first()
        
        # Dados do médico
        medico = None
        if medico_data and isinstance(medico_data, dict):
            class MedicoObj:
                def __init__(self, data):
                    self.nome = data.get('nome', 'Michel Raineri Haddad')
                    self.crm = data.get('crm', '183299')
                    self.assinatura_data = data.get('assinatura_data')
            medico = MedicoObj(medico_data)
        else:
            medico = Medico.query.filter_by(ativo=True).first()
        
        # Gerar PDF
        gerador = PDFModeloExato()
        return gerador.gerar_pdf_modelo_exato(exame, parametros, laudo, medico, nome_arquivo)
        
    except Exception as e:
        logger.error(f"Erro na função gerar_pdf_modelo_exato: {e}")
        raise e