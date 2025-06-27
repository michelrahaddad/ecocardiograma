"""
Teste de Usuabilidade Sequencial - 50 Usuários Reais
Adaptado para respeitar rate limiting e segurança do sistema
"""

import requests
import json
import time
import random
from datetime import datetime
import os

BASE_URL = "http://localhost:5000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "VidahAdmin2025!"}

# Pacientes reais brasileiros
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
    {"nome": "Gabriel Henrique Nunes", "idade": 28, "sexo": "Masculino", "nascimento": "1995-12-15"}
]

MEDICOS_SOLICITANTES = [
    "Dr. Carlos Cardiologista", "Dr. Ana Clínica Geral", "Dr. Pedro Internista",
    "Dr. Maria Cardiologia", "Dr. João Medicina Interna", "Dr. Fernanda Clínica"
]

INDICACOES_REAIS = [
    "Investigação de sopro cardíaco",
    "Controle pós-infarto do miocárdio",
    "Avaliação de hipertensão arterial",
    "Investigação de dispneia aos esforços",
    "Rotina cardiológica anual",
    "Avaliação pré-operatória"
]

class UsabilityTestResult:
    def __init__(self):
        self.total_users = 0
        self.successful_users = 0
        self.total_score = 0
        self.actions_performed = 0
        self.start_time = time.time()
        self.detailed_results = []
        
    def add_user_result(self, user_result):
        self.total_users += 1
        self.total_score += user_result['score']
        self.actions_performed += user_result['actions']
        
        if user_result['percentage'] >= 80:
            self.successful_users += 1
        
        self.detailed_results.append(user_result)
    
    def get_summary(self):
        elapsed_time = time.time() - self.start_time
        avg_score = self.total_score / self.total_users if self.total_users > 0 else 0
        avg_percentage = (avg_score / 100) * 100
        success_rate = (self.successful_users / self.total_users * 100) if self.total_users > 0 else 0
        
        return {
            'total_users': self.total_users,
            'successful_users': self.successful_users,
            'success_rate': success_rate,
            'avg_score': avg_score,
            'avg_percentage': avg_percentage,
            'total_actions': self.actions_performed,
            'elapsed_time': elapsed_time
        }

def simulate_user_session(user_id, paciente):
    """Simula uma sessão completa de usuário médico"""
    session = requests.Session()
    score = 0
    actions = 0
    log = []
    
    def log_action(action, success, points=0):
        nonlocal score, actions
        actions += 1
        if success:
            score += points
        log.append({
            'action': action,
            'success': success,
            'points': points
        })
    
    try:
        # 1. Login (5 pontos)
        login_data = {
            "username": ADMIN_CREDENTIALS["username"],
            "password": ADMIN_CREDENTIALS["password"]
        }
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        login_success = response.status_code in [200, 302]
        log_action("Login", login_success, 5)
        
        if not login_success:
            return create_user_result(user_id, paciente, score, actions, log)
        
        # 2. Criar exame (20 pontos)
        exam_data = {
            "nome_paciente": paciente["nome"],
            "data_nascimento": paciente["nascimento"],
            "idade": paciente["idade"],
            "sexo": paciente["sexo"],
            "data_exame": datetime.now().strftime("%Y-%m-%d"),
            "tipo_atendimento": random.choice(["Particular", "Convênio"]),
            "medico_solicitante": random.choice(MEDICOS_SOLICITANTES),
            "indicacao": random.choice(INDICACOES_REAIS)
        }
        
        response = session.post(f"{BASE_URL}/novo-exame", data=exam_data)
        exam_success = response.status_code in [200, 302]
        log_action("Criar Exame", exam_success, 20)
        
        # 3. Testar navegação (10 pontos)
        response = session.get(f"{BASE_URL}/")
        nav_success = response.status_code == 200
        log_action("Navegação", nav_success, 10)
        
        # 4. Buscar paciente (15 pontos)
        nome_busca = paciente["nome"].split()[0]
        response = session.get(f"{BASE_URL}/prontuario/buscar?nome={nome_busca}")
        search_success = response.status_code == 200
        log_action("Busca", search_success, 15)
        
        # 5. Testar APIs (20 pontos)
        api_score = 0
        apis = ["/api/hora-atual", "/api/patologias", "/api/templates-laudo"]
        
        for api in apis:
            try:
                response = session.get(f"{BASE_URL}{api}")
                if response.status_code == 200:
                    api_score += 7
            except:
                pass
        
        log_action("APIs", api_score > 0, api_score)
        
        # 6. Testar PDF (se houver exame) (20 pontos)
        try:
            response = session.get(f"{BASE_URL}/gerar-pdf/2")  # Usar exame existente
            pdf_success = response.status_code == 200 and 'application/pdf' in response.headers.get('content-type', '')
            log_action("PDF", pdf_success, 20)
        except:
            log_action("PDF", False, 0)
        
        # 7. Logout (10 pontos)
        response = session.get(f"{BASE_URL}/auth/logout")
        logout_success = response.status_code in [200, 302]
        log_action("Logout", logout_success, 10)
        
    except Exception as e:
        log_action("Erro Geral", False, 0)
    
    return create_user_result(user_id, paciente, score, actions, log)

def create_user_result(user_id, paciente, score, actions, log):
    """Cria resultado formatado do usuário"""
    return {
        'user_id': user_id,
        'paciente': paciente['nome'],
        'score': score,
        'max_score': 100,
        'percentage': (score / 100) * 100,
        'actions': actions,
        'log': log
    }

def main():
    """Executa teste de usuabilidade sequencial"""
    print("=" * 60)
    print("TESTE DE USUABILIDADE - 50 USUÁRIOS REAIS (SEQUENCIAL)")
    print("Sistema de Ecocardiograma - Grupo Vidah")
    print("=" * 60)
    
    results = UsabilityTestResult()
    
    # Executar 50 usuários sequencialmente para evitar rate limiting
    total_users = min(50, len(PACIENTES_REAIS) * 2)  # Usar pacientes repetidos se necessário
    
    for i in range(total_users):
        paciente_idx = i % len(PACIENTES_REAIS)
        paciente = PACIENTES_REAIS[paciente_idx]
        
        print(f"Usuário {i+1}/50: Testando {paciente['nome']}")
        
        # Simular sessão do usuário
        user_result = simulate_user_session(i, paciente)
        results.add_user_result(user_result)
        
        print(f"  Score: {user_result['score']}/100 ({user_result['percentage']:.1f}%)")
        
        # Pausa entre usuários para respeitar rate limiting
        time.sleep(1.0)
        
        # A cada 10 usuários, mostrar progresso
        if (i + 1) % 10 == 0:
            summary = results.get_summary()
            print(f"\nProgresso: {i+1}/50 usuários - Taxa de sucesso: {summary['success_rate']:.1f}%")
    
    # Resultados finais
    summary = results.get_summary()
    
    print("\n" + "=" * 60)
    print("RESULTADOS FINAIS - TESTE DE USUABILIDADE")
    print("=" * 60)
    print(f"Total de usuários testados: {summary['total_users']}")
    print(f"Usuários com sucesso (≥80%): {summary['successful_users']}/{summary['total_users']} ({summary['success_rate']:.1f}%)")
    print(f"Score médio: {summary['avg_score']:.1f}/100 ({summary['avg_percentage']:.1f}%)")
    print(f"Total de ações executadas: {summary['total_actions']}")
    print(f"Tempo total: {summary['elapsed_time']:.1f}s")
    
    # Classificação
    if summary['avg_percentage'] >= 90:
        classification = "EXCELENTE - Sistema pronto para produção"
    elif summary['avg_percentage'] >= 80:
        classification = "MUITO BOM - Pequenos ajustes recomendados"
    elif summary['avg_percentage'] >= 70:
        classification = "BOM - Melhorias necessárias"
    elif summary['avg_percentage'] >= 60:
        classification = "REGULAR - Correções importantes"
    else:
        classification = "INSATISFATÓRIO - Requer correções críticas"
    
    print(f"Classificação: {classification}")
    
    # Análise de problemas
    all_actions = []
    for result in results.detailed_results:
        all_actions.extend(result['log'])
    
    failed_actions = [a for a in all_actions if not a['success']]
    if failed_actions:
        print(f"\nProblemas identificados: {len(failed_actions)} falhas")
        
        action_failures = {}
        for action in failed_actions:
            action_type = action['action']
            action_failures[action_type] = action_failures.get(action_type, 0) + 1
        
        print("Falhas por tipo:")
        for action_type, count in sorted(action_failures.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {action_type}: {count} falhas")
    
    # Salvar relatório
    report = {
        'summary': summary,
        'classification': classification,
        'detailed_results': results.detailed_results[:10]  # Primeiros 10 para economia de espaço
    }
    
    with open('relatorio_usuabilidade_50_usuarios.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nRelatório salvo em: relatorio_usuabilidade_50_usuarios.json")
    
    return summary['avg_percentage']

if __name__ == "__main__":
    score = main()