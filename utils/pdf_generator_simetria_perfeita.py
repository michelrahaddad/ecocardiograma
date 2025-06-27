"""
Gerador PDF com Simetria Perfeita - Alinhamento Idêntico
Sistema que garante:
✅ Todos os títulos na mesma posição vertical
✅ Todas as tabelas com largura idêntica
✅ Simetria perfeita entre dados do paciente e outras seções
✅ Zero deslocamentos - linha vertical única
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64
import logging

class PDFSimetriaPerfeita:
    def __init__(self):
        """Gerador com simetria perfeita entre todos os elementos"""
        self.page_width, self.page_height = A4
        
        # MARGENS SIMÉTRICAS EXATAS
        self.margin_left = 2*cm
        self.margin_right = 2*cm
        self.margin_top = 2*cm  
        self.margin_bottom = 2*cm
        
        # LARGURA ÚNICA PARA TODAS AS TABELAS - SIMETRIA PERFEITA
        self.largura_tabela_unica = self.page_width - self.margin_left - self.margin_right
        
        # POSIÇÃO FIXA PARA TODOS OS TÍTULOS - ALINHAMENTO PERFEITO
        self.posicao_titulo_fixa = self.margin_left
        
        # CORES MÉDICAS INSTITUCIONAIS
        self.cores = {
            'titulo_principal': colors.HexColor('#2C3E50'),     # Azul escuro médico
            'titulo_secao': colors.HexColor('#34495E'),         # Azul escuro secundário
            'texto_principal': colors.HexColor('#2C3436'),      # Texto principal
            'fundo_tabela': colors.HexColor('#F8F9FA'),         # Fundo cinza claro
            'linha_separadora': colors.HexColor('#BDC3C7'),     # Linhas cinza claro
            'cabecalho_tabela': colors.HexColor('#34495E'),     # Cabeçalho das tabelas
            'texto_cabecalho': colors.white                     # Texto branco nos cabeçalhos
        }
        
        self.estilos = self.criar_estilos_simetricos()

    def criar_estilos_simetricos(self):
        """Criar estilos com simetria perfeita"""
        estilos = {}
        
        # TÍTULO PRINCIPAL CENTRALIZADO
        estilos['titulo_principal'] = ParagraphStyle(
            'TituloPrincipal',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=self.cores['titulo_principal'],
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        # TÍTULOS DE SEÇÃO - POSIÇÃO FIXA IDÊNTICA
        estilos['titulo_secao'] = ParagraphStyle(
            'TituloSecao',
            fontName='Helvetica-Bold', 
            fontSize=14,
            leading=18,
            textColor=self.cores['titulo_secao'],
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=10,
            leftIndent=0  # ZERO INDENTAÇÃO - ALINHAMENTO PERFEITO
        )
        
        # TEXTO NORMAL
        estilos['texto_normal'] = ParagraphStyle(
            'TextoNormal',
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            textColor=self.cores['texto_principal'],
            alignment=TA_LEFT,
            leftIndent=0
        )
        
        return estilos

    def criar_cabecalho_simetrico(self):
        """Criar cabeçalho com alinhamento perfeito"""
        def adicionar_cabecalho(canvas, doc):
            canvas.saveState()
            
            # TÍTULO CENTRALIZADO
            canvas.setFont('Helvetica-Bold', 14)
            canvas.setFillColor(self.cores['titulo_principal'])
            canvas.drawString(self.page_width/2 - 120, self.page_height - 40, 
                              "GRUPO VIDAH - MEDICINA DIAGNÓSTICA")
            
            # LINHA HORIZONTAL
            canvas.setStrokeColor(self.cores['linha_separadora'])
            canvas.setLineWidth(1)
            canvas.line(self.margin_left, self.page_height - 60, 
                       self.page_width - self.margin_right, self.page_height - 60)
            
            # TÍTULO DO DOCUMENTO
            canvas.setFont('Helvetica-Bold', 16)
            canvas.drawString(self.page_width/2 - 140, self.page_height - 85,
                              "LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO")
            
            canvas.restoreState()
            
        return adicionar_cabecalho

    def criar_secao_dados_paciente_simetrica(self, exame):
        """Dados do paciente com simetria perfeita"""
        elementos = []
        
        # TÍTULO COM POSIÇÃO FIXA IDÊNTICA A TODAS AS OUTRAS SEÇÕES
        titulo = Paragraph("■ DADOS DO PACIENTE", self.estilos['titulo_secao'])
        elementos.append(titulo)
        
        # TABELA COM LARGURA IDÊNTICA A TODAS AS OUTRAS
        dados = [
            ['PACIENTE:', f'{exame.nome_paciente}', 'DATA NASCIMENTO:', f'{exame.data_nascimento or "Não informado"}'],
            ['DATA DO EXAME:', f'{exame.data_exame}', 'IDADE:', f'{exame.idade or "Não informada"} anos'],
            ['SEXO:', f'{exame.sexo or "Não informado"}', 'TIPO ATENDIMENTO:', f'{exame.convenio or "+Vidah"}']
        ]
        
        # SIMETRIA PERFEITA - MESMA LARGURA DE TODAS AS TABELAS
        tabela = Table(dados, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cores['fundo_tabela']),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.cores['texto_principal']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cores['linha_separadora']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 15))
        
        return elementos

    def criar_tabela_parametros_simetrica(self, titulo, dados_parametros, icon="■"):
        """Tabela de parâmetros com simetria perfeita"""
        elementos = []
        
        # TÍTULO NA MESMA POSIÇÃO DE TODOS OS OUTROS
        titulo_formatado = Paragraph(f"{icon} {titulo}", self.estilos['titulo_secao'])
        elementos.append(titulo_formatado)
        
        if dados_parametros:
            # CABEÇALHO DA TABELA
            dados_tabela = [['PARÂMETRO', 'VALOR MEDIDO', 'REFERÊNCIA NORMAL']]
            
            # DADOS DOS PARÂMETROS
            for param, valor, referencia in dados_parametros:
                dados_tabela.append([param, str(valor), str(referencia)])
            
            # TABELA COM LARGURA IDÊNTICA A DADOS DO PACIENTE
            tabela = Table(dados_tabela, colWidths=[7*cm, 4*cm, 6*cm])
            tabela.setStyle(TableStyle([
                # CABEÇALHO
                ('BACKGROUND', (0, 0), (-1, 0), self.cores['cabecalho_tabela']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.cores['texto_cabecalho']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # DADOS
                ('BACKGROUND', (0, 1), (-1, -1), self.cores['fundo_tabela']),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.cores['texto_principal']),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # Parâmetro
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),   # Valor
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),   # Referência
                
                # BORDAS E ESPAÇAMENTO IDÊNTICOS
                ('GRID', (0, 0), (-1, -1), 0.5, self.cores['linha_separadora']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elementos.append(tabela)
        
        elementos.append(Spacer(1, 15))
        return elementos

    def processar_parametros_simetricos(self, parametros):
        """Processar parâmetros mantendo simetria"""
        antropometricos = []
        medidas_basicas = []
        ventriculo = []
        velocidades = []
        
        if parametros:
            # Tratar parametros como lista se necessário
            param_obj = parametros[0] if hasattr(parametros, '__getitem__') and len(parametros) > 0 else parametros
            
            # DADOS ANTROPOMÉTRICOS
            if getattr(param_obj, 'peso', None):
                antropometricos.append(['Peso', f'{param_obj.peso} kg', 'Medido'])
            if getattr(param_obj, 'altura', None):
                antropometricos.append(['Altura', f'{param_obj.altura} cm', 'Medido'])
            if getattr(param_obj, 'superficie_corporal', None):
                antropometricos.append(['Superfície Corporal', f'{param_obj.superficie_corporal:.2f} m²', 'Calculada'])
            if getattr(param_obj, 'frequencia_cardiaca', None):
                antropometricos.append(['Frequência Cardíaca', f'{param_obj.frequencia_cardiaca} bpm', '60-100 bpm'])
            
            # MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS
            if getattr(param_obj, 'ae', None):
                medidas_basicas.append(['Átrio Esquerdo', f'{param_obj.ae} mm', '27-38 mm'])
            if getattr(param_obj, 'raiz_aorta', None):
                medidas_basicas.append(['Raiz da Aorta', f'{param_obj.raiz_aorta} mm', '21-34 mm'])
            if getattr(param_obj, 'relacao_ae_ao', None):
                medidas_basicas.append(['Relação AE/Ao', f'{param_obj.relacao_ae_ao:.2f}', '< 1,5'])
            if getattr(param_obj, 'aorta_ascendente', None):
                medidas_basicas.append(['Aorta Ascendente', f'{param_obj.aorta_ascendente} mm', '< 38 mm'])
            if getattr(param_obj, 'vd', None):
                medidas_basicas.append(['Diâmetro VD', f'{param_obj.vd} mm', '7-23 mm'])
            if getattr(param_obj, 'vd_basal', None):
                medidas_basicas.append(['Diâmetro Basal VD', f'{param_obj.vd_basal} mm', '25-41 mm'])
            
            # VENTRÍCULO ESQUERDO
            if getattr(param_obj, 'ddve', None):
                ventriculo.append(['DDVE', f'{param_obj.ddve} mm', '35-56 mm'])
            if getattr(param_obj, 'dsve', None):
                ventriculo.append(['DSVE', f'{param_obj.dsve} mm', '21-40 mm'])
            if getattr(param_obj, 'percentual_encurtamento', None):
                ventriculo.append(['% Encurtamento', f'{param_obj.percentual_encurtamento:.1f}%', '25-45%'])
            if getattr(param_obj, 'septo', None):
                ventriculo.append(['Septo', f'{param_obj.septo} mm', '6-11 mm'])
            if getattr(param_obj, 'parede_posterior', None):
                ventriculo.append(['Parede Posterior', f'{param_obj.parede_posterior} mm', '6-11 mm'])
            if getattr(param_obj, 'relacao_septo_pp', None):
                ventriculo.append(['Relação Septo/PP', f'{param_obj.relacao_septo_pp:.2f}', '< 1,3'])
            
            # VELOCIDADES DOS FLUXOS
            if getattr(param_obj, 'fluxo_pulmonar', None):
                velocidades.append(['Fluxo Pulmonar', f'{param_obj.fluxo_pulmonar:.2f} m/s', '0,6-0,9 m/s'])
            if getattr(param_obj, 'fluxo_mitral', None):
                velocidades.append(['Fluxo Mitral', f'{param_obj.fluxo_mitral:.2f} m/s', '0,6-1,3 m/s'])
            if getattr(param_obj, 'fluxo_aortico', None):
                velocidades.append(['Fluxo Aórtico', f'{param_obj.fluxo_aortico:.2f} m/s', '1,0-1,7 m/s'])
            if getattr(param_obj, 'fluxo_tricuspide', None):
                velocidades.append(['Fluxo Tricúspide', f'{param_obj.fluxo_tricuspide:.2f} m/s', '0,3-0,7 m/s'])
        
        return antropometricos, medidas_basicas, ventriculo, velocidades

    def gerar_pdf_simetria_perfeita(self, exame, parametros, laudos, medico, caminho_saida):
        """Gerar PDF com simetria perfeita em todos os elementos"""
        
        # CRIAR DOCUMENTO
        doc = SimpleDocTemplate(
            caminho_saida,
            pagesize=A4,
            leftMargin=self.margin_left,
            rightMargin=self.margin_right,
            topMargin=self.margin_top + 40,
            bottomMargin=self.margin_bottom + 40
        )
        
        # ELEMENTOS COM SIMETRIA PERFEITA
        elementos = []
        
        # 1. DADOS DO PACIENTE
        elementos.extend(self.criar_secao_dados_paciente_simetrica(exame))
        
        # 2. PROCESSAR PARÂMETROS
        antropometricos, medidas_basicas, ventriculo, velocidades = self.processar_parametros_simetricos(parametros)
        
        # 3. DADOS ANTROPOMÉTRICOS
        if antropometricos:
            elementos.extend(self.criar_tabela_parametros_simetrica(
                "DADOS ANTROPOMÉTRICOS", antropometricos
            ))
        
        # 4. MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS  
        if medidas_basicas:
            elementos.extend(self.criar_tabela_parametros_simetrica(
                "MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS", medidas_basicas
            ))
        
        # 5. VENTRÍCULO ESQUERDO
        if ventriculo:
            elementos.extend(self.criar_tabela_parametros_simetrica(
                "VENTRÍCULO ESQUERDO", ventriculo
            ))
        
        # 6. VELOCIDADES DOS FLUXOS
        if velocidades:
            elementos.extend(self.criar_tabela_parametros_simetrica(
                "VELOCIDADES DOS FLUXOS", velocidades
            ))
        
        # 7. SEÇÕES MÉDICAS COM SIMETRIA
        if laudos:
            if hasattr(laudos, '__getitem__') and len(laudos) > 0:
                laudo_obj = laudos[0] 
            else:
                laudo_obj = laudos
                
            # Modo M e Bidimensional
            if getattr(laudo_obj, 'modo_m_bidimensional', None):
                titulo = Paragraph("■ MODO M E BIDIMENSIONAL", self.estilos['titulo_secao'])
                elementos.append(titulo)
                texto = Paragraph(laudo_obj.modo_m_bidimensional, self.estilos['texto_normal'])
                elementos.append(texto)
                elementos.append(Spacer(1, 15))
            
            # Doppler Convencional
            if getattr(laudo_obj, 'doppler_convencional', None):
                titulo = Paragraph("■ DOPPLER CONVENCIONAL", self.estilos['titulo_secao'])
                elementos.append(titulo)
                texto = Paragraph(laudo_obj.doppler_convencional, self.estilos['texto_normal'])
                elementos.append(texto)
                elementos.append(Spacer(1, 15))
            
            # Doppler Tecidual
            if getattr(laudo_obj, 'doppler_tecidual', None):
                titulo = Paragraph("■ DOPPLER TECIDUAL", self.estilos['titulo_secao'])
                elementos.append(titulo)
                texto = Paragraph(laudo_obj.doppler_tecidual, self.estilos['texto_normal'])
                elementos.append(texto)
                elementos.append(Spacer(1, 15))
            
            # Conclusão Diagnóstica
            if getattr(laudo_obj, 'conclusao_diagnostica', None):
                titulo = Paragraph("■ CONCLUSÃO DIAGNÓSTICA", self.estilos['titulo_secao'])
                elementos.append(titulo)
                texto = Paragraph(laudo_obj.conclusao_diagnostica, self.estilos['texto_normal'])
                elementos.append(texto)
                elementos.append(Spacer(1, 30))
        
        # 8. ASSINATURA MÉDICA
        if medico:
            assinatura = Paragraph(f"Dr. {medico.get('nome', 'Michel Raineri Haddad')}", self.estilos['texto_normal'])
            elementos.append(assinatura)
            crm = Paragraph(f"{medico.get('crm', 'CRM-SP 183299')}", self.estilos['texto_normal'])
            elementos.append(crm)
        
        # GERAR DOCUMENTO
        doc.build(elementos, onFirstPage=self.criar_cabecalho_simetrico())

def gerar_pdf_simetria_perfeita(exame, medico_data):
    """Função principal para gerar PDF com simetria perfeita"""
    try:
        # BUSCAR DADOS
        parametros = getattr(exame, 'parametros', None)
        laudos = getattr(exame, 'laudos', None)
        
        # CRIAR GERADOR
        gerador = PDFSimetriaPerfeita()
        
        # NOME DO ARQUIVO
        nome_paciente = getattr(exame, 'nome_paciente', 'Paciente').replace(' ', '_')
        data_hoje = __import__('datetime').datetime.now().strftime('%d%m%Y')
        caminho_pdf = f"generated_pdfs/laudo_simetria_perfeita_{nome_paciente}_{data_hoje}.pdf"
        
        # GARANTIR DIRETÓRIO
        os.makedirs('generated_pdfs', exist_ok=True)
        
        # GERAR PDF
        gerador.gerar_pdf_simetria_perfeita(exame, parametros, laudos, medico_data, caminho_pdf)
        
        return caminho_pdf
        
    except Exception as e:
        logging.error(f"Erro ao gerar PDF com simetria perfeita: {str(e)}")
        return None