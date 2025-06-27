"""
Serviço de PDF - Geração de relatórios em PDF

Centraliza toda a lógica de geração de PDFs profissionais
para laudos e relatórios médicos.
"""

from typing import Optional
from flask import Response, make_response
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import logging

from modules.core.database import DatabaseManager
from modules.core.exceptions import BusinessRuleError
from models import Exame

logger = logging.getLogger(__name__)

class PDFService:
    """Serviço centralizado para geração de PDFs"""
    
    @staticmethod
    def generate_exam_pdf(exam_id: int) -> Response:
        """Gera PDF completo do exame"""
        try:
            # Obter dados do exame
            exam = DatabaseManager.get_by_id(Exame, exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            # Criar buffer para PDF
            buffer = BytesIO()
            
            # Criar documento
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Construir conteúdo
            story = []
            story.extend(PDFService._build_header(exam))
            story.extend(PDFService._build_patient_info(exam))
            story.extend(PDFService._build_parameters_section(exam))
            story.extend(PDFService._build_laudo_section(exam))
            story.extend(PDFService._build_footer())
            
            # Gerar PDF
            doc.build(story)
            
            # Preparar resposta
            buffer.seek(0)
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=exame_{exam_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            
            buffer.close()
            return response
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            raise BusinessRuleError(f"Erro ao gerar PDF: {str(e)}")
    
    @staticmethod
    def _build_header(exam: Exame) -> list:
        """Constrói cabeçalho do PDF"""
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=1  # Centro
        )
        
        story = []
        story.append(Paragraph("GRUPO VIDAH", header_style))
        story.append(Paragraph("Ecocardiograma Transtorácico", styles['Heading2']))
        story.append(Spacer(1, 0.5*cm))
        
        return story
    
    @staticmethod
    def _build_patient_info(exam: Exame) -> list:
        """Constrói seção de informações do paciente"""
        styles = getSampleStyleSheet()
        story = []
        
        # Título da seção
        story.append(Paragraph("DADOS DO PACIENTE", styles['Heading3']))
        
        # Tabela com informações
        data = [
            ['Nome:', exam.nome_paciente],
            ['Data de Nascimento:', exam.data_nascimento],
            ['Idade:', f"{exam.idade} anos"],
            ['Sexo:', exam.sexo],
            ['Data do Exame:', exam.data_exame],
            ['Tipo de Atendimento:', exam.tipo_atendimento or 'Não informado'],
            ['Médico Solicitante:', exam.medico_solicitante or 'Não informado'],
            ['Indicação:', exam.indicacao or 'Não informada']
        ]
        
        table = Table(data, colWidths=[4*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
        
        return story
    
    @staticmethod
    def _build_parameters_section(exam: Exame) -> list:
        """Constrói seção de parâmetros"""
        from modules.exams.parameter_service import ParameterService
        
        styles = getSampleStyleSheet()
        story = []
        
        parameters = ParameterService.get_parameters(exam.id)
        
        if parameters:
            story.append(Paragraph("PARÂMETROS ECOCARDIOGRÁFICOS", styles['Heading3']))
            
            # Organizar parâmetros em grupos
            param_groups = PDFService._organize_parameters(parameters)
            
            for group_name, group_params in param_groups.items():
                if group_params:
                    story.append(Paragraph(group_name, styles['Heading4']))
                    
                    # Criar tabela para o grupo
                    data = []
                    for param_name, param_value in group_params.items():
                        if param_value is not None:
                            data.append([param_name, str(param_value)])
                    
                    if data:
                        table = Table(data, colWidths=[8*cm, 4*cm])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 0.3*cm))
        
        return story
    
    @staticmethod
    def _build_laudo_section(exam: Exame) -> list:
        """Constrói seção do laudo"""
        from modules.reports.laudo_service import LaudoService
        
        styles = getSampleStyleSheet()
        story = []
        
        laudo = LaudoService.get_laudo(exam.id)
        
        if laudo:
            story.append(Paragraph("LAUDO MÉDICO", styles['Heading3']))
            
            sections = [
                ('Modo M e Bidimensional:', laudo.modo_m_bidimensional),
                ('Doppler Convencional:', laudo.doppler_convencional),
                ('Doppler Tecidual:', laudo.doppler_tecidual),
                ('Conclusão:', laudo.conclusao),
                ('Recomendações:', laudo.recomendacoes)
            ]
            
            for section_title, section_content in sections:
                if section_content:
                    story.append(Paragraph(section_title, styles['Heading4']))
                    story.append(Paragraph(section_content, styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        return story
    
    @staticmethod
    def _build_footer() -> list:
        """Constrói rodapé do PDF"""
        styles = getSampleStyleSheet()
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1  # Centro
        )
        
        story = []
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - Sistema Ecocardiograma Grupo Vidah",
            footer_style
        ))
        
        return story
    
    @staticmethod
    def _organize_parameters(parameters) -> dict:
        """Organiza parâmetros em grupos lógicos"""
        groups = {
            "Dados Antropométricos": {
                "Peso (kg)": parameters.peso,
                "Altura (m)": parameters.altura,
                "Superfície Corporal (m²)": parameters.superficie_corporal,
                "Frequência Cardíaca (bpm)": parameters.frequencia_cardiaca
            },
            "Medidas Estruturais": {
                "Átrio Esquerdo (cm)": parameters.atrio_esquerdo,
                "Raiz da Aorta (cm)": parameters.raiz_aorta,
                "Relação AE/Ao": parameters.relacao_atrio_esquerdo_aorta,
                "Aorta Ascendente (cm)": parameters.aorta_ascendente,
                "Diâmetro VD (cm)": parameters.diametro_ventricular_direito
            },
            "Função Ventricular Esquerda": {
                "DDVE (cm)": parameters.diametro_diastolico_final_ve,
                "DSVE (cm)": parameters.diametro_sistolico_final,
                "Fração de Ejeção (%)": parameters.fracao_ejecao,
                "% Encurtamento": parameters.percentual_encurtamento,
                "Septo IV (cm)": parameters.espessura_diastolica_septo,
                "Parede Posterior (cm)": parameters.espessura_diastolica_ppve
            },
            "Função Diastólica": {
                "Onda E (m/s)": parameters.onda_e,
                "Onda A (m/s)": parameters.onda_a,
                "Relação E/A": parameters.relacao_e_a,
                "E' (cm/s)": parameters.onda_e_linha,
                "Relação E/E'": parameters.relacao_e_e_linha
            },
            "Avaliação das Valvas": {
                "Insuficiência Mitral": parameters.insuficiencia_mitral,
                "Insuficiência Tricúspide": parameters.insuficiencia_tricuspide,
                "Insuficiência Aórtica": parameters.insuficiencia_aortica,
                "Pressão Sistólica VD (mmHg)": parameters.pressao_sistolica_vd
            }
        }
        
        return groups