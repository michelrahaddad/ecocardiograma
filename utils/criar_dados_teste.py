"""
Script para criar dados de teste para o módulo de prontuário
"""

from app import app, db
from models import Exame, ParametrosEcocardiograma, LaudoEcocardiograma, Medico
from datetime import datetime, timedelta
import random

def criar_dados_teste():
    """Criar dados de teste para demonstração do prontuário"""
    
    with app.app_context():
        # Criar médico padrão se não existir
        medico = Medico.query.first()
        if not medico:
            medico = Medico()
            medico.nome = "Dr. Michel Raineri Haddad"
            medico.crm = "183299"
            medico.ativo = True
            db.session.add(medico)
            db.session.commit()

        # Lista de pacientes de exemplo
        pacientes = [
            {
                'nome': 'João Silva Santos',
                'data_nascimento': '15/03/1980',
                'idade': 44,
                'sexo': 'Masculino'
            },
            {
                'nome': 'Maria Oliveira Costa',
                'data_nascimento': '22/07/1965',
                'idade': 59,
                'sexo': 'Feminino'
            },
            {
                'nome': 'Pedro Henrique Almeida',
                'data_nascimento': '08/11/1975',
                'idade': 49,
                'sexo': 'Masculino'
            },
            {
                'nome': 'Ana Carolina Ferreira',
                'data_nascimento': '14/09/1990',
                'idade': 34,
                'sexo': 'Feminino'
            },
            {
                'nome': 'Carlos Eduardo Lima',
                'data_nascimento': '03/05/1960',
                'idade': 64,
                'sexo': 'Masculino'
            }
        ]

        # Criar exames para cada paciente
        for paciente in pacientes:
            # Número aleatório de exames por paciente (1-4)
            num_exames = random.randint(1, 4)
            
            for i in range(num_exames):
                # Data do exame (últimos 2 anos)
                data_base = datetime.now() - timedelta(days=random.randint(30, 730))
                data_exame = data_base.strftime('%d/%m/%Y')
                
                # Criar exame
                exame = Exame()
                exame.nome_paciente = paciente['nome']
                exame.data_nascimento = paciente['data_nascimento']
                exame.idade = paciente['idade']
                exame.sexo = paciente['sexo']
                exame.data_exame = data_exame
                exame.tipo_atendimento = random.choice(['Ambulatorial', 'Internação', 'UTI', 'Emergência'])
                exame.medico_usuario = medico.nome
                exame.medico_solicitante = random.choice([
                    'Dr. João Cardiologista',
                    'Dra. Maria Clínica Geral',
                    'Dr. Pedro Intensivista',
                    'Dra. Ana Geriatria'
                ])
                exame.indicacao = random.choice([
                    'Investigação de sopro cardíaco',
                    'Controle de hipertensão arterial',
                    'Avaliação pré-operatória',
                    'Dor torácica atípica',
                    'Dispneia aos esforços',
                    'Seguimento de cardiomiopatia',
                    'Avaliação de função ventricular'
                ])
                exame.created_at = data_base
                exame.updated_at = data_base
                
                db.session.add(exame)
                db.session.flush()  # Para obter o ID
                
                # Criar parâmetros ecocardiográficos
                params = ParametrosEcocardiograma()
                params.exame_id = exame.id
                
                # Dados antropométricos
                params.peso = round(random.uniform(50, 120), 1)
                params.altura = random.randint(150, 190)
                params.superficie_corporal = round(params.peso * params.altura / 10000 * 0.725, 2)
                params.frequencia_cardiaca = random.randint(50, 110)
                
                # Estruturas cardíacas
                params.atrio_esquerdo = round(random.uniform(2.5, 4.2), 2)
                params.raiz_aorta = round(random.uniform(2.0, 3.8), 2)
                params.relacao_atrio_esquerdo_aorta = round(params.atrio_esquerdo / params.raiz_aorta, 2)
                params.aorta_ascendente = round(random.uniform(2.5, 4.0), 2)
                
                # Ventrículo esquerdo
                params.diametro_diastolico_final_ve = round(random.uniform(3.5, 5.8), 2)
                params.diametro_sistolico_final = round(random.uniform(2.0, 4.0), 2)
                params.fracao_ejecao = round(random.uniform(50, 75), 1)
                params.percentual_encurtamento = round(random.uniform(25, 45), 1)
                
                # Paredes
                params.espessura_diastolica_septo = round(random.uniform(0.6, 1.4), 2)
                params.espessura_diastolica_ppve = round(random.uniform(0.6, 1.2), 2)
                
                # Doppler
                params.onda_e = round(random.uniform(0.4, 1.2), 2)
                params.onda_a = round(random.uniform(0.3, 1.0), 2)
                params.relacao_e_a = round(params.onda_e / params.onda_a, 2)
                
                params.created_at = data_base
                params.updated_at = data_base
                
                db.session.add(params)
                
                # Criar laudo
                laudo = LaudoEcocardiograma()
                laudo.exame_id = exame.id
                
                laudo.modo_m_bidimensional = random.choice([
                    'Ventrículo esquerdo com dimensões e função sistólica preservadas. Átrios de dimensões normais. Ventrículo direito com dimensões normais.',
                    'Ventrículo esquerdo com dimensões aumentadas e disfunção sistólica leve. Átrio esquerdo discretamente aumentado.',
                    'Função sistólica do ventrículo esquerdo preservada. Geometria ventricular normal. Cavidades cardíacas com dimensões normais.',
                    'Hipertrofia ventricular esquerda concêntrica leve. Função sistólica preservada. Relaxamento ventricular alterado.'
                ])
                
                laudo.doppler_convencional = random.choice([
                    'Padrão de enchimento ventricular esquerdo normal. Pressões de enchimento normais.',
                    'Alteração do relaxamento ventricular esquerdo grau I. Pressões de enchimento discretamente elevadas.',
                    'Função diastólica do ventrículo esquerdo preservada. Sem evidências de hipertensão pulmonar.',
                    'Disfunção diastólica grau I do ventrículo esquerdo. Pressão sistólica da artéria pulmonar normal.'
                ])
                
                laudo.conclusao = random.choice([
                    'Ecocardiograma transtorácico normal.',
                    'Alteração leve do relaxamento ventricular esquerdo.',
                    'Hipertrofia ventricular esquerda concêntrica leve com função sistólica preservada.',
                    'Função sistólica e diastólica do ventrículo esquerdo preservadas.',
                    'Disfunção diastólica leve do ventrículo esquerdo.',
                    'Ventrículo esquerdo com dimensões e função normais.'
                ])
                
                laudo.recomendacoes = random.choice([
                    'Controle clínico e seguimento cardiológico conforme orientação médica.',
                    'Recomenda-se seguimento cardiológico e controle dos fatores de risco cardiovascular.',
                    'Manter seguimento clínico. Repetir ecocardiograma em 12 meses ou conforme indicação clínica.',
                    'Seguimento cardiológico regular. Controle da pressão arterial.',
                    'Acompanhamento cardiológico de rotina. Atividade física regular conforme liberação médica.'
                ])
                
                laudo.created_at = data_base
                laudo.updated_at = data_base
                
                db.session.add(laudo)
        
        # Salvar todas as alterações
        db.session.commit()
        print(f"Dados de teste criados com sucesso!")
        print(f"- {len(pacientes)} pacientes")
        print(f"- Total de exames criados: {sum(random.randint(1, 4) for _ in pacientes)}")

if __name__ == '__main__':
    criar_dados_teste()