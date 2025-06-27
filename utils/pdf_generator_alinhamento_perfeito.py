"""
Gerador de PDF com Alinhamento Perfeito - Design Institucional Moderno
Sistema seguindo exatamente o layout das imagens fornecidas:

✅ Todos os títulos alinhados na mesma posição vertical
✅ Todas as tabelas com alinhamento idêntico à esquerda
✅ Dados do paciente perfeitamente alinhados com início das tabelas
✅ Zero deslocamentos - linha vertical perfeita em todos os elementos
✅ Tipografia Helvetica-Bold 16pt títulos, Helvetica 11-12pt corpo
✅ Paleta médica: azul escuro (#2C3E50) títulos, cinza-claro (#BDC3C7) separadores
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
import logging

class PDFAlinhamentoPerfeito:
    def __init__(self):
        """Inicializar gerador com alinhamento perfeito"""
        self.page_width, self.page_height = A4
        
        # MARGENS SIMÉTRICAS
        self.margin_left = 2*cm
        self.margin_right = 2*cm
        self.margin_top = 2*cm
        self.margin_bottom = 2*cm
        
        # LINHA VERTICAL ÚNICA - ALINHAMENTO PERFEITO
        self.linha_alinhamento = self.margin_left  # POSIÇÃO FIXA PARA TODOS OS ELEMENTOS
        self.largura_util = self.page_width - self.margin_left - self.margin_right
        
        # CORES MÉDICAS INSTITUCIONAIS
        self.cores = {
            'titulo_principal': colors.HexColor('#2C3E50'),     # Azul escuro médico
            'titulo_secao': colors.HexColor('#2C3E50'),         # Mesma cor para consistência
            'texto_principal': colors.HexColor('#2C3436'),      # Texto principal
            'fundo_tabela': colors.HexColor('#F8F9FA'),         # Fundo cinza claro
            'linha_separadora': colors.HexColor('#BDC3C7'),     # Linhas cinza claro
            'cabecalho_tabela': colors.HexColor('#2C3E50'),     # Cabeçalho das tabelas
            'texto_cabecalho': colors.white                     # Texto branco nos cabeçalhos
        }
        
        self.estilos = self.criar_estilos_alinhamento()

    def criar_estilos_alinhamento(self):
        """Criar estilos tipográficos com alinhamento perfeito"""
        estilos = {}
        
        # TÍTULO PRINCIPAL
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
        
        # TEXTO MÉDICO
        estilos['texto_medico'] = ParagraphStyle(
            'TextoMedico',
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            textColor=self.cores['texto_principal'],
            alignment=TA_LEFT,
            leftIndent=0,
            spaceAfter=10
        )
        
        return estilos

    def criar_cabecalho_institucional(self):
        """Criar cabeçalho institucional moderno"""
        def adicionar_cabecalho(canvas, doc):
            canvas.saveState()
            
            # GRUPO VIDAH - CENTRALIZADO
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

    def criar_rodape_institucional(self):
        """Criar rodapé institucional (apenas na segunda página)"""
        def adicionar_rodape(canvas, doc):
            if doc.page > 1:  # Apenas da segunda página em diante
                canvas.saveState()
                
                # LINHA SUPERIOR
                canvas.setStrokeColor(self.cores['linha_separadora'])
                canvas.setLineWidth(0.5)
                canvas.line(self.margin_left, 50, 
                           self.page_width - self.margin_right, 50)
                
                # ENDEREÇO CENTRALIZADO
                canvas.setFont('Helvetica', 10)
                canvas.setFillColor(self.cores['texto_principal'])
                canvas.drawString(self.page_width/2 - 100, 30,
                                  "R. XV de Novembro, 594 - Ibitinga-SP | Tel: (16) 3342-4768")
                
                canvas.restoreState()
                
        return adicionar_rodape

    def criar_secao_dados_paciente(self, exame):
        """Criar seção de dados do paciente com SIMETRIA PERFEITA"""
        elementos = []
        
        # TÍTULO COM ALINHAMENTO IDÊNTICO A TODAS AS OUTRAS SEÇÕES
        titulo = Paragraph("■ DADOS DO PACIENTE", self.estilos['titulo_secao'])
        elementos.append(titulo)
        
        # TABELA COM LARGURA IDÊNTICA A TODAS AS OUTRAS TABELAS
        dados = [
            ['PACIENTE:', f'{exame.nome_paciente}', 'DATA NASCIMENTO:', f'{exame.data_nascimento or "Não informado"}'],
            ['DATA DO EXAME:', f'{exame.data_exame}', 'IDADE:', f'{exame.idade or "Não informada"} anos'],
            ['SEXO:', f'{exame.sexo or "Não informado"}', 'TIPO ATENDIMENTO:', f'{getattr(exame, "tipo_atendimento", None) or "+Vidah"}']
        ]
        
        # LARGURA IDÊNTICA A TODAS AS TABELAS - SIMETRIA PERFEITA
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

    def criar_tabela_parametros_alinhada(self, titulo, dados_parametros, icon="■"):
        """Criar tabela de parâmetros com SIMETRIA PERFEITA - tamanhos idênticos"""
        elementos = []
        
        # TÍTULO COM ALINHAMENTO IDÊNTICO
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
                
                # BORDAS E ESPAÇAMENTO
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

    def criar_secao_medica_alinhada(self, titulo, conteudo, icon="■"):
        """Criar seção médica com alinhamento perfeito"""
        elementos = []
        
        # TÍTULO NA MESMA LINHA VERTICAL DE TODOS OS OUTROS
        titulo_formatado = Paragraph(f"{icon} {titulo}", self.estilos['titulo_secao'])
        elementos.append(titulo_formatado)
        
        # CONTEÚDO MÉDICO
        if conteudo:
            texto = Paragraph(conteudo, self.estilos['texto_medico'])
            elementos.append(texto)
        
        elementos.append(Spacer(1, 15))
        return elementos

    def processar_assinatura_digital(self, medico):
        """Processar assinatura digital sem símbolos informais"""
        elementos = []
        
        # ASSINATURA DIGITAL
        if medico and medico.get('assinatura_data'):
            try:
                # Decodificar Base64
                assinatura_bytes = base64.b64decode(medico['assinatura_data'])
                assinatura_stream = BytesIO(assinatura_bytes)
                
                # Criar imagem
                assinatura_img = Image(assinatura_stream, width=120, height=50)
                elementos.append(assinatura_img)
                
            except Exception as e:
                # Fallback sem símbolos informais
                elementos.append(Paragraph("ASSINATURA DIGITAL", self.estilos['texto_medico']))
        
        # DADOS DO MÉDICO
        nome_medico = medico.get('nome', 'Michel Raineri Haddad')
        crm_medico = medico.get('crm', 'CRM-SP 183299')
        
        elementos.append(Paragraph(f"Dr. {nome_medico}", self.estilos['texto_medico']))
        elementos.append(Paragraph(f"{crm_medico}", self.estilos['texto_medico']))
        
        return elementos

    def processar_dados_parametros(self, parametros):
        """Processar dados dos parâmetros ecocardiográficos"""
        antropometricos = []
        medidas_basicas = []
        ventriculo = []
        volumes = []
        velocidades = []
        gradientes = []
        
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
        if parametros:
            if getattr(param_obj, 'atrio_esquerdo', None):
                medidas_basicas.append(['Átrio Esquerdo', f'{param_obj.atrio_esquerdo} mm', '27-38 mm'])
            if getattr(param_obj, 'raiz_aorta', None):
                medidas_basicas.append(['Raiz da Aorta', f'{param_obj.raiz_aorta} mm', '21-34 mm'])
            if getattr(param_obj, 'relacao_atrio_esquerdo_aorta', None):
                medidas_basicas.append(['Relação AE/Ao', f'{param_obj.relacao_atrio_esquerdo_aorta:.2f}', '< 1,5'])
            if getattr(param_obj, 'aorta_ascendente', None):
                medidas_basicas.append(['Aorta Ascendente', f'{param_obj.aorta_ascendente} mm', '< 38 mm'])
            if getattr(param_obj, 'diametro_ventricular_direito', None):
                medidas_basicas.append(['Diâmetro VD', f'{param_obj.diametro_ventricular_direito} mm', '7-23 mm'])
            if getattr(param_obj, 'diametro_basal_vd', None):
                medidas_basicas.append(['Diâmetro Basal VD', f'{param_obj.diametro_basal_vd} mm', '25-41 mm'])
        
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
        
            # VOLUMES E FUNÇÃO SISTÓLICA
            if getattr(param_obj, 'vdf', None):
                volumes.append(['VDF', f'{param_obj.vdf:.1f} mL', '67-155 mL'])
            if getattr(param_obj, 'vsf', None):
                volumes.append(['VSF', f'{param_obj.vsf:.1f} mL', '22-58 mL'])
            if getattr(param_obj, 'volume_ejecao', None):
                volumes.append(['Volume Ejeção', f'{param_obj.volume_ejecao:.1f} mL', 'Calculado'])
            if getattr(param_obj, 'fracao_ejecao', None):
                volumes.append(['Fração de Ejeção', f'{param_obj.fracao_ejecao:.1f}%', '≥55%'])
            if getattr(param_obj, 'massa_ve', None):
                volumes.append(['Massa VE', f'{param_obj.massa_ve:.1f} g', '88-224 g'])
            if getattr(param_obj, 'indice_massa_ve', None):
                volumes.append(['Índice Massa VE', f'{param_obj.indice_massa_ve:.1f} g/m²', '49-115 g/m²'])
        
            # VELOCIDADES DOS FLUXOS
            if getattr(param_obj, 'fluxo_pulmonar', None):
                velocidades.append(['Fluxo Pulmonar', f'{param_obj.fluxo_pulmonar:.2f} m/s', '0,6-0,9 m/s'])
            if getattr(param_obj, 'fluxo_mitral', None):
                velocidades.append(['Fluxo Mitral', f'{param_obj.fluxo_mitral:.2f} m/s', '0,6-1,3 m/s'])
            if getattr(param_obj, 'fluxo_aortico', None):
                velocidades.append(['Fluxo Aórtico', f'{param_obj.fluxo_aortico:.2f} m/s', '1,0-1,7 m/s'])
            if getattr(param_obj, 'fluxo_tricuspide', None):
                velocidades.append(['Fluxo Tricúspide', f'{param_obj.fluxo_tricuspide:.2f} m/s', '0,3-0,7 m/s'])
        
            # GRADIENTES
            if getattr(param_obj, 'gradiente_vd_ap', None):
                gradientes.append(['VD→AP', f'{param_obj.gradiente_vd_ap:.1f} mmHg', '< 4 mmHg'])
            if getattr(param_obj, 'gradiente_ae_ve', None):
                gradientes.append(['AE→VE', f'{param_obj.gradiente_ae_ve:.1f} mmHg', '< 5 mmHg'])
            if getattr(param_obj, 'gradiente_ve_ao', None):
                gradientes.append(['VE→AO', f'{param_obj.gradiente_ve_ao:.1f} mmHg', '< 4 mmHg'])
            if getattr(param_obj, 'gradiente_ad_vd', None):
                gradientes.append(['AD→VD', f'{param_obj.gradiente_ad_vd:.1f} mmHg', '< 5 mmHg'])
            if getattr(param_obj, 'gradiente_it', None):
                gradientes.append(['IT', f'{param_obj.gradiente_it:.1f} mmHg', '< 3 mmHg'])
            if getattr(param_obj, 'psap', None):
                gradientes.append(['PSAP', f'{param_obj.psap:.1f} mmHg', '15-30 mmHg'])
        
        return antropometricos, medidas_basicas, ventriculo, volumes, velocidades, gradientes

    def gerar_pdf_alinhamento_perfeito(self, exame, parametros, laudos, medico, caminho_saida):
        """Gerar PDF institucional com alinhamento perfeito"""
        
        # CRIAR DOCUMENTO
        doc = SimpleDocTemplate(
            caminho_saida,
            pagesize=A4,
            leftMargin=self.margin_left,
            rightMargin=self.margin_right,
            topMargin=self.margin_top + 40,
            bottomMargin=self.margin_bottom + 40
        )
        
        # ELEMENTOS COM ALINHAMENTO PERFEITO
        elementos = []
        
        # 1. DADOS DO PACIENTE
        elementos.extend(self.criar_secao_dados_paciente(exame))
        
        # 2. PROCESSAR PARÂMETROS
        antropometricos, medidas_basicas, ventriculo, volumes, velocidades, gradientes = self.processar_dados_parametros(parametros)
        
        # 3. DADOS ANTROPOMÉTRICOS
        if antropometricos:
            elementos.extend(self.criar_tabela_parametros_alinhada(
                "DADOS ANTROPOMÉTRICOS", antropometricos
            ))
        
        # 4. MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS  
        if medidas_basicas:
            elementos.extend(self.criar_tabela_parametros_alinhada(
                "MEDIDAS ECOCARDIOGRÁFICAS BÁSICAS", medidas_basicas
            ))
        
        # 5. VENTRÍCULO ESQUERDO
        if ventriculo:
            elementos.extend(self.criar_tabela_parametros_alinhada(
                "VENTRÍCULO ESQUERDO", ventriculo
            ))
        
        # 6. VOLUMES E FUNÇÃO SISTÓLICA
        if volumes:
            elementos.extend(self.criar_tabela_parametros_alinhada(
                "VOLUMES E FUNÇÃO SISTÓLICA", volumes
            ))
        
        # 7. VELOCIDADES DOS FLUXOS
        if velocidades:
            elementos.extend(self.criar_tabela_parametros_alinhada(
                "VELOCIDADES DOS FLUXOS", velocidades
            ))
        
        # 8. GRADIENTES
        if gradientes:
            elementos.extend(self.criar_tabela_parametros_alinhada(
                "GRADIENTES", gradientes
            ))
        
        # QUEBRA DE PÁGINA CONTROLADA PARA 2 PÁGINAS
        elementos.append(PageBreak())
        
        # 9. SEÇÕES MÉDICAS COM ALINHAMENTO PERFEITO
        if laudos:
            if hasattr(laudos, '__getitem__') and len(laudos) > 0:
                laudo_obj = laudos[0] 
            else:
                laudo_obj = laudos
                
            # Modo M e Bidimensional
            if getattr(laudo_obj, 'modo_m_bidimensional', None):
                elementos.extend(self.criar_secao_medica_alinhada(
                    "MODO M E BIDIMENSIONAL", laudo_obj.modo_m_bidimensional
                ))
            
            # Doppler Convencional
            if getattr(laudo_obj, 'doppler_convencional', None):
                elementos.extend(self.criar_secao_medica_alinhada(
                    "DOPPLER CONVENCIONAL", laudo_obj.doppler_convencional
                ))
            
            # Doppler Tecidual
            if getattr(laudo_obj, 'doppler_tecidual', None):
                elementos.extend(self.criar_secao_medica_alinhada(
                    "DOPPLER TECIDUAL", laudo_obj.doppler_tecidual
                ))
            
            # Conclusão Diagnóstica
            if getattr(laudo_obj, 'conclusao_diagnostica', None):
                elementos.extend(self.criar_secao_medica_alinhada(
                    "CONCLUSÃO DIAGNÓSTICA", laudo_obj.conclusao_diagnostica
                ))
        
        # 10. ASSINATURA DIGITAL ALINHADA
        elementos.append(Spacer(1, 30))
        elementos.extend(self.processar_assinatura_digital(medico))
        
        # GERAR DOCUMENTO
        doc.build(elementos, 
                 onFirstPage=self.criar_cabecalho_institucional(),
                 onLaterPages=self.criar_rodape_institucional())

def gerar_pdf_alinhamento_perfeito(exame, medico_data):
    """Função principal para gerar PDF com alinhamento perfeito"""
    try:
        # BUSCAR DADOS
        parametros = getattr(exame, 'parametros', None)
        laudos = getattr(exame, 'laudos', None)
        
        # CRIAR GERADOR
        gerador = PDFAlinhamentoPerfeito()
        
        # NOME DO ARQUIVO
        nome_paciente = getattr(exame, 'nome_paciente', 'Paciente').replace(' ', '_')
        data_hoje = __import__('datetime').datetime.now().strftime('%d%m%Y')
        caminho_pdf = f"generated_pdfs/laudo_alinhamento_perfeito_{nome_paciente}_{data_hoje}.pdf"
        
        # GARANTIR DIRETÓRIO
        os.makedirs('generated_pdfs', exist_ok=True)
        
        # MÉDICO CORRIGIDO
        class MedicoObj:
            def __init__(self, data):
                self.nome = data.get('nome', 'Michel Raineri Haddad')
                self.crm = data.get('crm', 'CRM-SP 183299')
                self.assinatura_data = data.get('assinatura_data')
                self.assinatura_url = data.get('assinatura_url')
        
        medico_obj = MedicoObj(medico_data) if medico_data else None
        
        # GERAR PDF
        gerador.gerar_pdf_alinhamento_perfeito(exame, parametros, laudos, medico_data, caminho_pdf)
        
        return caminho_pdf
        
    except Exception as e:
        logging.error(f"Erro ao gerar PDF com alinhamento perfeito: {str(e)}")
        return None