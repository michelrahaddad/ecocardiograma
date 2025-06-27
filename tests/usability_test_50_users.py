"""
Teste de Usuabilidade com 50 Usuários Reais - Sistema de Ecocardiograma
Simula cenários reais de uso com diferentes tipos de usuários médicos

Score: 0-100 baseado na experiência do usuário real
"""

import requests
import json
import time
import random
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Configurações do teste
BASE_URL = "http://localhost:5000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "VidahAdmin2025!"}

# Dados reais de pacientes brasileiros para teste
PACIENTES_REAIS = [
    {"nome": "Maria Silva Santos", "idade": 45, "sexo": "Feminino", "nascimento": "1979-03-15"},
    {"nome": "João Carlos Oliveira", "idade": 62, "sexo": "Masculino", "nascimento": "1962-07-22"},
    {"nome": "Ana Paula Ferreira", "idade": 38, "sexo": "Feminino", "nascimento": "1985-11-08"},
    {"nome": "Carlos Eduardo Lima", "idade": 55, "sexo": "Masculino", "nascimento": "1968-12-03"},
    {"nome": "Fernanda Costa Almeida", "idade": 41, "sexo": "Feminino", "nascimento": "1982-09-17"},
    {"nome": "Roberto Pereira Souza", "idade": 58, "sexo": "Masculino", "nascimento": "1965-04-25"},
    {"nome": "Juliana Rodrigues", "idade": 33, "sexo": "Feminino", "nascimento": "1990-06-12"},
    {"nome": "Pedro Henrique Silva", "idade": 47, "sexo": "Masculino", "nascimento": "1976-10-30"},
    {"nome": "Luciana Alves Martins", "idade": 52, "sexo": "Feminino", "nascimento": "1971-02-18"},
    {"nome": "Anderson Santos Lima", "idade": 39, "sexo": "Masculino", "nascimento": "1984-08-05"},
    {"nome": "Patrícia Gomes Costa", "idade": 44, "sexo": "Feminino", "nascimento": "1979-12-28"},
    {"nome": "Marcos Vinícius Rocha", "idade": 36, "sexo": "Masculino", "nascimento": "1987-05-14"},
    {"nome": "Cristina Barbosa", "idade": 49, "sexo": "Feminino", "nascimento": "1974-01-09"},
    {"nome": "Rafael Cardoso Mendes", "idade": 42, "sexo": "Masculino", "nascimento": "1981-11-21"},
    {"nome": "Mônica Fernandes", "idade": 37, "sexo": "Feminino", "nascimento": "1986-07-06"},
    {"nome": "Thiago Augusto Pinto", "idade": 51, "sexo": "Masculino", "nascimento": "1972-03-19"},
    {"nome": "Vanessa Lopes Correia", "idade": 29, "sexo": "Feminino", "nascimento": "1994-09-23"},
    {"nome": "Bruno César Araújo", "idade": 46, "sexo": "Masculino", "nascimento": "1977-04-11"},
    {"nome": "Camila Duarte Moreira", "idade": 35, "sexo": "Feminino", "nascimento": "1988-10-02"},
    {"nome": "Gabriel Henrique Nunes", "idade": 28, "sexo": "Masculino", "nascimento": "1995-12-15"},
    {"nome": "Priscila Andrade", "idade": 43, "sexo": "Feminino", "nascimento": "1980-06-08"},
    {"nome": "Leonardo Torres Freitas", "idade": 54, "sexo": "Masculino", "nascimento": "1969-02-27"},
    {"nome": "Daniela Campos Ribeiro", "idade": 40, "sexo": "Feminino", "nascimento": "1983-08-14"},
    {"nome": "Felipe Santos Carvalho", "idade": 32, "sexo": "Masculino", "nascimento": "1991-05-30"},
    {"nome": "Renata Machado Silva", "idade": 48, "sexo": "Feminino", "nascimento": "1975-11-17"},
    {"nome": "Eduardo Nascimento", "idade": 56, "sexo": "Masculino", "nascimento": "1967-01-12"},
    {"nome": "Larissa Ramos Costa", "idade": 31, "sexo": "Feminino", "nascimento": "1992-07-25"},
    {"nome": "Rodrigo Ferraz Monteiro", "idade": 45, "sexo": "Masculino", "nascimento": "1978-04-03"},
    {"nome": "Tatiana Cruz Nogueira", "idade": 50, "sexo": "Feminino", "nascimento": "1973-10-22"},
    {"nome": "Vinícius Leal Batista", "idade": 34, "sexo": "Masculino", "nascimento": "1989-03-07"},
    {"nome": "Alessandra Moura", "idade": 41, "sexo": "Feminino", "nascimento": "1982-12-11"},
    {"nome": "Diego Almeida Teixeira", "idade": 38, "sexo": "Masculino", "nascimento": "1985-09-18"},
    {"nome": "Mariana Oliveira Cunha", "idade": 27, "sexo": "Feminino", "nascimento": "1996-06-04"},
    {"nome": "Henrique Borges Lima", "idade": 53, "sexo": "Masculino", "nascimento": "1970-02-16"},
    {"nome": "Adriana Carvalho Dias", "idade": 46, "sexo": "Feminino", "nascimento": "1977-08-29"},
    {"nome": "Marcelo Soares Pinto", "idade": 39, "sexo": "Masculino", "nascimento": "1984-11-13"},
    {"nome": "Elaine Gonçalves", "idade": 42, "sexo": "Feminino", "nascimento": "1981-05-20"},
    {"nome": "Alexandre Costa Santos", "idade": 57, "sexo": "Masculino", "nascimento": "1966-12-01"},
    {"nome": "Bianca Reis Martins", "idade": 30, "sexo": "Feminino", "nascimento": "1993-04-24"},
    {"nome": "Igor Pereira Rocha", "idade": 44, "sexo": "Masculino", "nascimento": "1979-09-10"},
    {"nome": "Silvia Regina Torres", "idade": 49, "sexo": "Feminino", "nascimento": "1974-07-07"},
    {"nome": "André Luiz Barbosa", "idade": 36, "sexo": "Masculino", "nascimento": "1987-01-26"},
    {"nome": "Carolina Mendes Silva", "idade": 33, "sexo": "Feminino", "nascimento": "1990-11-19"},
    {"nome": "Gustavo Fernandes", "idade": 52, "sexo": "Masculino", "nascimento": "1971-06-02"},
    {"nome": "Natália Souza Lima", "idade": 28, "sexo": "Feminino", "nascimento": "1995-03-15"},
    {"nome": "Fábio Rodrigues Costa", "idade": 47, "sexo": "Masculino", "nascimento": "1976-10-08"},
    {"nome": "Isabela Santos Araújo", "idade": 35, "sexo": "Feminino", "nascimento": "1988-12-23"},
    {"nome": "Lucas Matheus Vieira", "idade": 29, "sexo": "Masculino", "nascimento": "1994-08-16"},
    {"nome": "Raquel Alves Pereira", "idade": 43, "sexo": "Feminino", "nascimento": "1980-04-05"},
    {"nome": "Mateus Henrique Moura", "idade": 31, "sexo": "Masculino", "nascimento": "1992-01-28"}
]

MEDICOS_SOLICITANTES = [
    "Dr. Carlos Cardiologista", "Dr. Ana Clínica Geral", "Dr. Pedro Internista",
    "Dr. Maria Cardiologia", "Dr. João Medicina Interna", "Dr. Fernanda Clínica",
    "Dr. Roberto Cardiologia", "Dr. Juliana Internista", "Dr. Anderson Clínico",
    "Dr. Patrícia Cardiologista"
]

INDICACOES_REAIS = [
    "Investigação de sopro cardíaco",
    "Controle pós-infarto do miocárdio",
    "Avaliação de hipertensão arterial",
    "Investigação de dispneia aos esforços",
    "Rotina cardiológica anual",
    "Avaliação pré-operatória",
    "Controle de insuficiência cardíaca",
    "Investigação de dor torácica",
    "Avaliação de arritmia cardíaca",
    "Controle de valvopatia conhecida"
]

class UsabilityTestUser:
    def __init__(self, user_id, paciente_data):
        self.user_id = user_id
        self.paciente = paciente_data
        self.session = requests.Session()
        self.score = 0
        self.max_score = 100
        self.actions_log = []
        self.start_time = time.time()
        
    def log_action(self, action, success, points=0, details=""):
        """Registra ação do usuário"""
        elapsed = time.time() - self.start_time
        status = "✅" if success else "❌"
        if success:
            self.score += points
        
        log_entry = {
            "user_id": self.user_id,
            "action": action,
            "success": success,
            "points": points,
            "details": details,
            "elapsed_time": elapsed,
            "status": status
        }
        self.actions_log.append(log_entry)
        
    def login(self):
        """Simula login do usuário médico"""
        try:
            login_data = {
                "username": ADMIN_CREDENTIALS["username"],
                "password": ADMIN_CREDENTIALS["password"]
            }
            response = self.session.post(f"{BASE_URL}/auth/login", data=login_data)
            success = response.status_code in [200, 302]
            self.log_action("Login", success, 5, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_action("Login", False, 0, f"Erro: {str(e)}")
            return False
    
    def criar_exame_completo(self):
        """Simula criação completa de exame"""
        try:
            # Dados do exame
            exam_data = {
                "nome_paciente": self.paciente["nome"],
                "data_nascimento": self.paciente["nascimento"],
                "idade": self.paciente["idade"],
                "sexo": self.paciente["sexo"],
                "data_exame": datetime.now().strftime("%Y-%m-%d"),
                "tipo_atendimento": random.choice(["Particular", "Convênio", "SUS"]),
                "medico_solicitante": random.choice(MEDICOS_SOLICITANTES),
                "indicacao": random.choice(INDICACOES_REAIS)
            }
            
            response = self.session.post(f"{BASE_URL}/novo-exame", data=exam_data)
            success = response.status_code in [200, 302]
            self.log_action("Criar Exame", success, 15, f"Paciente: {self.paciente['nome']}")
            return success
        except Exception as e:
            self.log_action("Criar Exame", False, 0, f"Erro: {str(e)}")
            return False
    
    def preencher_parametros(self, exame_id):
        """Simula preenchimento de parâmetros ecocardiográficos"""
        try:
            # Parâmetros realistas baseados em valores normais
            params = {
                "atrio_esquerdo": round(random.uniform(32, 38), 1),
                "raiz_aorta": round(random.uniform(30, 37), 1),
                "aorta_ascendente": round(random.uniform(28, 36), 1),
                "diametro_ventricular_direito": round(random.uniform(15, 25), 1),
                "diametro_basal_vd": round(random.uniform(28, 35), 1),
                "diametro_diastolico_final_ve": round(random.uniform(42, 52), 1),
                "diametro_sistolico_final": round(random.uniform(28, 38), 1),
                "espessura_diastolica_septo": round(random.uniform(7, 11), 1),
                "espessura_diastolica_ppve": round(random.uniform(7, 11), 1),
                "fluxo_pulmonar": round(random.uniform(0.8, 1.2), 1),
                "fluxo_mitral": round(random.uniform(0.6, 1.0), 1),
                "fluxo_aortico": round(random.uniform(0.9, 1.3), 1),
                "fluxo_tricuspide": round(random.uniform(0.3, 0.7), 1)
            }
            
            response = self.session.post(f"{BASE_URL}/parametros/{exame_id}", data=params)
            success = response.status_code in [200, 302]
            self.log_action("Parâmetros", success, 20, f"Exame ID: {exame_id}")
            return success
        except Exception as e:
            self.log_action("Parâmetros", False, 0, f"Erro: {str(e)}")
            return False
    
    def criar_laudo(self, exame_id):
        """Simula criação de laudo médico"""
        try:
            laudos_exemplo = [
                "Exame ecocardiográfico dentro dos padrões de normalidade. Função sistólica do ventrículo esquerdo preservada.",
                "Ventrículo esquerdo com dimensões normais e função sistólica preservada. Valvas cardíacas sem alterações significativas.",
                "Ecocardiograma normal. Função diastólica preservada. Pressões pulmonares dentro dos limites da normalidade.",
                "Estruturas cardíacas com dimensões normais. Não evidenciadas alterações segmentares da contratilidade.",
                "Exame dentro dos padrões de normalidade para a faixa etária. Recomenda-se seguimento clínico habitual."
            ]
            
            laudo_data = {
                "conclusao": random.choice(laudos_exemplo),
                "modo_m_bidimensional": "Ventrículo esquerdo com dimensões e função normais. Átrios com dimensões preservadas.",
                "doppler_convencional": "Fluxos transvalvares dentro dos padrões de normalidade.",
                "recomendacoes": "Manter acompanhamento clínico. Retornar se sintomas."
            }
            
            response = self.session.post(f"{BASE_URL}/laudo/{exame_id}", data=laudo_data)
            success = response.status_code in [200, 302]
            self.log_action("Laudo", success, 20, f"Exame ID: {exame_id}")
            return success
        except Exception as e:
            self.log_action("Laudo", False, 0, f"Erro: {str(e)}")
            return False
    
    def gerar_pdf(self, exame_id):
        """Simula geração de PDF"""
        try:
            response = self.session.get(f"{BASE_URL}/gerar-pdf/{exame_id}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                is_pdf = 'application/pdf' in content_type
                pdf_size = len(response.content)
                success = is_pdf and pdf_size > 1000
                self.log_action("PDF", success, 15, f"Tamanho: {pdf_size} bytes")
            else:
                self.log_action("PDF", False, 0, f"Status: {response.status_code}")
                success = False
            return success
        except Exception as e:
            self.log_action("PDF", False, 0, f"Erro: {str(e)}")
            return False
    
    def buscar_paciente(self):
        """Simula busca de paciente"""
        try:
            nome_busca = self.paciente["nome"].split()[0]  # Buscar pelo primeiro nome
            response = self.session.get(f"{BASE_URL}/prontuario/buscar?nome={nome_busca}")
            success = response.status_code == 200
            self.log_action("Busca", success, 10, f"Busca por: {nome_busca}")
            return success
        except Exception as e:
            self.log_action("Busca", False, 0, f"Erro: {str(e)}")
            return False
    
    def usar_apis(self):
        """Simula uso de APIs do sistema"""
        try:
            apis = ["/api/hora-atual", "/api/patologias", "/api/templates-laudo"]
            api_successes = 0
            
            for api in apis:
                try:
                    response = self.session.get(f"{BASE_URL}{api}")
                    if response.status_code == 200:
                        api_successes += 1
                except:
                    pass
            
            success = api_successes >= 2
            self.log_action("APIs", success, 10, f"{api_successes}/3 APIs funcionando")
            return success
        except Exception as e:
            self.log_action("APIs", False, 0, f"Erro: {str(e)}")
            return False
    
    def logout(self):
        """Simula logout"""
        try:
            response = self.session.get(f"{BASE_URL}/auth/logout")
            success = response.status_code in [200, 302]
            self.log_action("Logout", success, 5, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_action("Logout", False, 0, f"Erro: {str(e)}")
            return False
    
    def executar_fluxo_completo(self):
        """Executa o fluxo completo de um usuário médico"""
        print(f"Usuário {self.user_id}: Iniciando teste com {self.paciente['nome']}")
        
        # Simular tempo de carregamento da página
        time.sleep(random.uniform(0.5, 2.0))
        
        if not self.login():
            return self.get_final_score()
        
        # Criar exame
        if not self.criar_exame_completo():
            return self.get_final_score()
        
        # Assumir que o exame foi criado com ID sequencial
        exame_id = self.user_id + 10  # ID baseado no usuário
        
        # Preencher parâmetros
        time.sleep(random.uniform(1.0, 3.0))  # Tempo para preencher formulário
        self.preencher_parametros(exame_id)
        
        # Criar laudo
        time.sleep(random.uniform(2.0, 4.0))  # Tempo para elaborar laudo
        self.criar_laudo(exame_id)
        
        # Gerar PDF
        time.sleep(random.uniform(0.5, 1.5))
        self.gerar_pdf(exame_id)
        
        # Buscar paciente
        time.sleep(random.uniform(0.5, 1.0))
        self.buscar_paciente()
        
        # Usar APIs
        self.usar_apis()
        
        # Logout
        self.logout()
        
        return self.get_final_score()
    
    def get_final_score(self):
        """Retorna score final do usuário"""
        elapsed_total = time.time() - self.start_time
        return {
            "user_id": self.user_id,
            "paciente": self.paciente["nome"],
            "score": self.score,
            "max_score": self.max_score,
            "percentage": (self.score / self.max_score) * 100,
            "elapsed_time": elapsed_total,
            "actions": len(self.actions_log),
            "actions_log": self.actions_log
        }

def executar_teste_usuario(user_id):
    """Executa teste para um usuário específico"""
    paciente = PACIENTES_REAIS[user_id % len(PACIENTES_REAIS)]
    user = UsabilityTestUser(user_id, paciente)
    return user.executar_fluxo_completo()

def main():
    """Executa teste de usuabilidade com 50 usuários"""
    print("=" * 60)
    print("TESTE DE USUABILIDADE - 50 USUÁRIOS REAIS")
    print("Sistema de Ecocardiograma - Grupo Vidah")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    
    # Executar testes em paralelo (simulando usuários simultâneos)
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submeter tarefas para 50 usuários
        futures = [executor.submit(executar_teste_usuario, i) for i in range(50)]
        
        # Coletar resultados conforme completam
        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
                print(f"Usuário {result['user_id']}: {result['score']}/{result['max_score']} pts "
                      f"({result['percentage']:.1f}%) - {result['paciente']}")
            except Exception as e:
                print(f"Erro no usuário {i}: {str(e)}")
    
    # Calcular estatísticas finais
    total_time = time.time() - start_time
    
    if results:
        scores = [r['score'] for r in results]
        percentages = [r['percentage'] for r in results]
        times = [r['elapsed_time'] for r in results]
        
        avg_score = sum(scores) / len(scores)
        avg_percentage = sum(percentages) / len(percentages)
        avg_time = sum(times) / len(times)
        
        successful_users = len([r for r in results if r['percentage'] >= 80])
        
        print("\n" + "=" * 60)
        print("RESULTADOS FINAIS - TESTE DE USUABILIDADE")
        print("=" * 60)
        print(f"Total de usuários testados: {len(results)}")
        print(f"Usuários com sucesso (≥80%): {successful_users}/{len(results)} ({(successful_users/len(results)*100):.1f}%)")
        print(f"Score médio: {avg_score:.1f}/{results[0]['max_score']} ({avg_percentage:.1f}%)")
        print(f"Tempo médio por usuário: {avg_time:.1f}s")
        print(f"Tempo total do teste: {total_time:.1f}s")
        
        # Classificação geral
        if avg_percentage >= 90:
            classification = "EXCELENTE - Sistema pronto para produção"
        elif avg_percentage >= 80:
            classification = "MUITO BOM - Pequenos ajustes recomendados"
        elif avg_percentage >= 70:
            classification = "BOM - Melhorias necessárias"
        elif avg_percentage >= 60:
            classification = "REGULAR - Correções importantes"
        else:
            classification = "INSATISFATÓRIO - Requer correções críticas"
        
        print(f"Classificação: {classification}")
        
        # Análise de problemas mais comuns
        all_actions = []
        for result in results:
            all_actions.extend(result['actions_log'])
        
        failed_actions = [a for a in all_actions if not a['success']]
        if failed_actions:
            print(f"\nProblemas identificados: {len(failed_actions)} falhas")
            action_failures = {}
            for action in failed_actions:
                action_type = action['action']
                if action_type not in action_failures:
                    action_failures[action_type] = 0
                action_failures[action_type] += 1
            
            print("Falhas por tipo de ação:")
            for action_type, count in sorted(action_failures.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {action_type}: {count} falhas")
        
        # Salvar relatório detalhado
        with open('relatorio_usuabilidade_50_usuarios.json', 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_users': len(results),
                    'successful_users': successful_users,
                    'avg_score': avg_score,
                    'avg_percentage': avg_percentage,
                    'avg_time': avg_time,
                    'total_time': total_time,
                    'classification': classification
                },
                'detailed_results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nRelatório detalhado salvo em: relatorio_usuabilidade_50_usuarios.json")
        
        return avg_percentage
    else:
        print("Nenhum resultado válido obtido")
        return 0

if __name__ == "__main__":
    score = main()