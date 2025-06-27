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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

logger = logging.getLogger(__name__)

def generate_pdf_report(exame):
    """
    Função principal para gerar PDF do exame
    """
    try:
        # Criar pasta de PDFs se não existir
        pdf_dir = 'generated_pdfs'
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        # Nome do arquivo
        filename = f'laudo_ecocardiograma_{exame.id}_{exame.nome_paciente.replace(" ", "_")}.pdf'
        filepath = os.path.join(pdf_dir, filename)
        
        # Criar PDF
        pdf_generator = PDFCompacto()
        pdf_generator.gerar_pdf(exame, filepath)
        
        return filepath
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        raise

class PDFCompacto:
    def __init__(self):
        """Gerador compacto para máximo 2 páginas A4"""
        # Margens mínimas para máximo aproveitamento
        self.margem_esquerda = 8*mm
        self.margem_direita = 8*mm
        self.margem_superior = 8*mm
        self.margem_inferior = 8*mm
        
        # Largura útil
        self.largura_util = A4[0] - self.margem_esquerda - self.margem_direita
        
        # Estilos
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
    
    def _criar_estilos_customizados(self):
        """Criar estilos personalizados para o PDF"""
        # Cabeçalho principal
        self.style_cabecalho = ParagraphStyle(
            'CabecalhoPersonalizado',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            spaceAfter=1*mm
        )
        
        # Título documento
        self.style_titulo = ParagraphStyle(
            'TituloPersonalizado',
            parent=self.styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=2*mm
        )
        
        # Seções
        self.style_secao = ParagraphStyle(
            'SecaoPersonalizada',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold',
            spaceAfter=1*mm
        )
        
        # Texto normal
        self.style_texto = ParagraphStyle(
            'TextoPersonalizado',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=black,
            alignment=TA_JUSTIFY,
            spaceAfter=1*mm
        )
    
    def gerar_pdf(self, exame, filepath):
        """Gerar PDF compacto com dados do exame"""
        try:
            # Criar documento
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                leftMargin=self.margem_esquerda,
                rightMargin=self.margem_direita,
                topMargin=self.margem_superior,
                bottomMargin=self.margem_inferior
            )
            
            # Elementos do PDF
            elementos = []
            
            # Cabeçalho
            elementos.extend(self._criar_cabecalho())
            
            # Dados do paciente
            elementos.extend(self._criar_dados_paciente(exame))
            
            # Parâmetros ecocardiográficos
            elementos.extend(self._criar_parametros_ecocardiograficos(exame))
            
            # Quebra de página antes dos laudos
            elementos.append(PageBreak())
            
            # Laudos médicos
            elementos.extend(self._criar_laudos_medicos(exame))
            
            # Assinatura
            elementos.extend(self._criar_assinatura(exame))
            
            # Gerar PDF
            doc.build(elementos)
            
            logger.info(f"PDF gerado com sucesso: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            raise
    
    def _criar_cabecalho(self):
        """Criar cabeçalho do documento"""
        elementos = []
        
        # Nome da clínica
        cabecalho_texto = "GRUPO VIDAH - MEDICINA DIAGNÓSTICA<br/>R. XV de Novembro, 594 - Ibitinga-SP | Tel: (16) 3342-4768"
        elementos.append(Paragraph(cabecalho_texto, self.style_cabecalho))
        elementos.append(Spacer(1, 2*mm))
        
        # Título do documento
        titulo = "LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO"
        elementos.append(Paragraph(titulo, self.style_titulo))
        elementos.append(Spacer(1, 3*mm))
        
        return elementos
    
    def _criar_dados_paciente(self, exame):
        """Criar seção de dados do paciente"""
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph("DADOS DO PACIENTE", self.style_secao))
        
        # Dados básicos
        dados_basicos = [
            ['Nome:', exame.nome_paciente or ''],
            ['Data de Nascimento:', exame.data_nascimento or ''],
            ['Idade:', f"{exame.idade} anos" if exame.idade else ''],
            ['Sexo:', exame.sexo or ''],
            ['Data do Exame:', exame.data_exame or ''],
            ['Tipo de Atendimento:', exame.tipo_atendimento or ''],
            ['Médico Solicitante:', exame.medico_solicitante or ''],
            ['Indicação:', exame.indicacao or '']
        ]
        
        tabela_dados = Table(dados_basicos, colWidths=[4*cm, 14*cm])
        tabela_dados.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elementos.append(tabela_dados)
        elementos.append(Spacer(1, 3*mm))
        
        return elementos
    
    def _criar_parametros_ecocardiograficos(self, exame):
        """Criar seção de parâmetros ecocardiográficos"""
        elementos = []
        parametros = exame.parametros
        
        if not parametros:
            return elementos
        
        # Dados antropométricos
        elementos.append(Paragraph("DADOS ANTROPOMÉTRICOS", self.style_secao))
        
        dados_antropometricos = [
            ['Peso:', f"{parametros.peso:.1f} kg" if parametros.peso else ''],
            ['Altura:', f"{parametros.altura:.2f} m" if parametros.altura else ''],
            ['Superfície Corporal:', f"{parametros.superficie_corporal:.2f} m²" if parametros.superficie_corporal else ''],
            ['FC:', f"{parametros.frequencia_cardiaca} bpm" if parametros.frequencia_cardiaca else '']
        ]
        
        tabela_antropometricos = Table(dados_antropometricos, colWidths=[4*cm, 14*cm])
        tabela_antropometricos.setStyle(self._get_tabela_style())
        elementos.append(tabela_antropometricos)
        elementos.append(Spacer(1, 2*mm))
        
        # Medidas ecocardiográficas básicas
        elementos.append(Paragraph("MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS", self.style_secao))
        
        medidas_basicas = [
            ['AE:', f"{parametros.atrio_esquerdo:.1f} mm" if parametros.atrio_esquerdo else ''],
            ['Raiz Aorta:', f"{parametros.raiz_aorta:.1f} mm" if parametros.raiz_aorta else ''],
            ['Relação AE/Ao:', f"{parametros.relacao_atrio_esquerdo_aorta:.1f}" if parametros.relacao_atrio_esquerdo_aorta else ''],
            ['Aorta Ascendente:', f"{parametros.aorta_ascendente:.1f} mm" if parametros.aorta_ascendente else ''],
            ['VD:', f"{parametros.diametro_ventricular_direito:.1f} mm" if parametros.diametro_ventricular_direito else ''],
            ['VD Basal:', f"{parametros.diametro_basal_vd:.1f} mm" if parametros.diametro_basal_vd else '']
        ]
        
        tabela_basicas = Table(medidas_basicas, colWidths=[4*cm, 14*cm])
        tabela_basicas.setStyle(self._get_tabela_style())
        elementos.append(tabela_basicas)
        elementos.append(Spacer(1, 2*mm))
        
        # Ventrículo esquerdo
        elementos.append(Paragraph("VENTRÍCULO ESQUERDO", self.style_secao))
        
        dados_ve = [
            ['DDVE:', f"{parametros.diametro_diastolico_final_ve:.1f} mm" if parametros.diametro_diastolico_final_ve else ''],
            ['DSVE:', f"{parametros.diametro_sistolico_final:.1f} mm" if parametros.diametro_sistolico_final else ''],
            ['% Encurtamento:', f"{parametros.percentual_encurtamento:.1f}%" if parametros.percentual_encurtamento else ''],
            ['Septo:', f"{parametros.espessura_diastolica_septo:.1f} mm" if parametros.espessura_diastolica_septo else ''],
            ['PP:', f"{parametros.espessura_diastolica_ppve:.1f} mm" if parametros.espessura_diastolica_ppve else ''],
            ['Relação S/PP:', f"{parametros.relacao_septo_parede_posterior:.1f}" if parametros.relacao_septo_parede_posterior else '']
        ]
        
        tabela_ve = Table(dados_ve, colWidths=[4*cm, 14*cm])
        tabela_ve.setStyle(self._get_tabela_style())
        elementos.append(tabela_ve)
        elementos.append(Spacer(1, 2*mm))
        
        # Volumes e função sistólica
        elementos.append(Paragraph("VOLUMES E FUNÇÃO SISTÓLICA", self.style_secao))
        
        dados_volumes = [
            ['VDF:', f"{parametros.volume_diastolico_final:.1f} mL" if parametros.volume_diastolico_final else ''],
            ['VSF:', f"{parametros.volume_sistolico_final:.1f} mL" if parametros.volume_sistolico_final else ''],
            ['Volume Ejeção:', f"{parametros.volume_ejecao:.1f} mL" if parametros.volume_ejecao else ''],
            ['FE:', f"{parametros.fracao_ejecao:.1f}%" if parametros.fracao_ejecao else ''],
            ['Massa VE:', f"{parametros.massa_ve:.1f} g" if parametros.massa_ve else ''],
            ['Índice Massa VE:', f"{parametros.indice_massa_ve:.1f} g/m²" if parametros.indice_massa_ve else '']
        ]
        
        tabela_volumes = Table(dados_volumes, colWidths=[4*cm, 14*cm])
        tabela_volumes.setStyle(self._get_tabela_style())
        elementos.append(tabela_volumes)
        
        return elementos
    
    def _criar_laudos_medicos(self, exame):
        """Criar seção de laudos médicos"""
        elementos = []
        
        if not exame.laudos:
            return elementos
        
        laudo = exame.laudos[0]
        
        # Modo M e Bidimensional
        if laudo.modo_m_bidimensional:
            elementos.append(Paragraph("MODO M E BIDIMENSIONAL", self.style_secao))
            elementos.append(Paragraph(laudo.modo_m_bidimensional, self.style_texto))
            elementos.append(Spacer(1, 3*mm))
        
        # Doppler Convencional
        if laudo.doppler_convencional:
            elementos.append(Paragraph("DOPPLER CONVENCIONAL", self.style_secao))
            elementos.append(Paragraph(laudo.doppler_convencional, self.style_texto))
            elementos.append(Spacer(1, 3*mm))
        
        # Doppler Tecidual
        if laudo.doppler_tecidual:
            elementos.append(Paragraph("DOPPLER TECIDUAL", self.style_secao))
            elementos.append(Paragraph(laudo.doppler_tecidual, self.style_texto))
            elementos.append(Spacer(1, 3*mm))
        
        # Conclusão
        if laudo.conclusao:
            elementos.append(Paragraph("CONCLUSÃO", self.style_secao))
            elementos.append(Paragraph(laudo.conclusao, self.style_texto))
            elementos.append(Spacer(1, 5*mm))
        
        return elementos
    
    def _criar_assinatura(self, exame):
        """Criar seção de assinatura médica"""
        elementos = []
        
        # Buscar médico
        from models import Medico
        medico = Medico.query.filter_by(ativo=True).first()
        
        if not medico:
            # Médico padrão
            nome_medico = "Dr. Michel Raineri Haddad"
            crm_medico = "CRM-SP 183299"
        else:
            nome_medico = medico.nome
            crm_medico = medico.crm
        
        # Data do exame
        data_exame = exame.data_exame or datetime.now().strftime('%d/%m/%Y')
        
        # Tabela de assinatura
        assinatura_dados = [
            ['', ''],
            ['ASSINATURA DIGITAL', ''],
            ['', ''],
            [nome_medico, ''],
            [crm_medico, ''],
            [f'Data: {data_exame}', '']
        ]
        
        tabela_assinatura = Table(assinatura_dados, colWidths=[9*cm, 9*cm])
        tabela_assinatura.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),  # ASSINATURA DIGITAL
            ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),  # Nome médico
            ('TOPPADDING', (0, 0), (-1, -1), 1*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1*mm),
            ('LINEBELOW', (0, 2), (0, 2), 1, black),  # Linha da assinatura
        ]))
        
        elementos.append(Spacer(1, 10*mm))
        elementos.append(tabela_assinatura)
        
        return elementos
    
    def _get_tabela_style(self):
        """Estilo padrão para tabelas"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ])
