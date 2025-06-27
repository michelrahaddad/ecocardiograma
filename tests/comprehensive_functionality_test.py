"""
Teste de Funcionalidade Completa - Sistema de Ecocardiograma
Score: 0-100 pontos baseado em funcionalidades testadas

Testa todos os botões, fluxos, PDFs, salvamentos, rotas front/back
"""

import requests
import json
import time
from datetime import datetime
import os
import sys

# Configurações do teste
BASE_URL = "http://localhost:5000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "VidahAdmin2025!"}
USER_CREDENTIALS = {"username": "usuario", "password": "Usuario123!"}

class ComprehensiveFunctionalityTest:
    def __init__(self):
        self.score = 0
        self.max_score = 100
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, points, details=""):
        """Registra resultado do teste"""
        status = "✅ PASS" if success else "❌ FAIL"
        if success:
            self.score += points
        
        result = {
            "test": test_name,
            "status": status,
            "points": f"{points}/{points}" if success else f"0/{points}",
            "details": details
        }
        self.test_results.append(result)
        print(f"{status} {test_name} ({result['points']} pts) - {details}")
        
    def test_home_page_access(self):
        """Teste 1: Acesso à página inicial (5 pts)"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            success = response.status_code == 200 and "Sistema de Ecocardiograma" in response.text
            self.log_test("Acesso Página Inicial", success, 5, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Acesso Página Inicial", False, 5, f"Erro: {str(e)}")
    
    def test_login_flow(self):
        """Teste 2: Fluxo de login completo (10 pts)"""
        try:
            # Acessar página de login
            login_page = self.session.get(f"{BASE_URL}/auth/login")
            if login_page.status_code != 200:
                self.log_test("Fluxo de Login", False, 10, "Página de login inacessível")
                return
            
            # Fazer login
            login_data = {
                "username": ADMIN_CREDENTIALS["username"],
                "password": ADMIN_CREDENTIALS["password"]
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
            success = response.status_code in [200, 302]
            self.log_test("Fluxo de Login", success, 10, f"Login admin status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Fluxo de Login", False, 10, f"Erro: {str(e)}")
    
    def test_exam_creation_flow(self):
        """Teste 3: Criação de exame completo (15 pts)"""
        try:
            # Acessar formulário de novo exame
            new_exam_page = self.session.get(f"{BASE_URL}/novo-exame")
            if new_exam_page.status_code != 200:
                self.log_test("Criação de Exame", False, 15, "Formulário inacessível")
                return
            
            # Dados do exame de teste
            exam_data = {
                "nome_paciente": "Teste Funcionalidade Silva",
                "data_exame": datetime.now().strftime("%Y-%m-%d"),
                "medico_solicitante": "Dr. Teste Completo",
                "idade_paciente": "45 anos",
                "data_nascimento": "1979-01-01"
            }
            
            response = self.session.post(f"{BASE_URL}/novo-exame", data=exam_data, allow_redirects=False)
            success = response.status_code in [200, 302]
            self.log_test("Criação de Exame", success, 15, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Criação de Exame", False, 15, f"Erro: {str(e)}")
    
    def test_parameters_form(self):
        """Teste 4: Formulário de parâmetros (12 pts)"""
        try:
            # Assumindo exame ID 1 (criado no teste anterior)
            params_page = self.session.get(f"{BASE_URL}/parametros/1")
            if params_page.status_code != 200:
                self.log_test("Formulário Parâmetros", False, 12, "Formulário inacessível")
                return
            
            # Dados dos parâmetros
            params_data = {
                "atrio_esquerdo": "36",
                "raiz_aorta": "35",
                "aorta_ascendente": "33",
                "vd_diametro": "18",
                "vd_basal": "32",
                "ddve": "45",
                "dsve": "32",
                "septo": "9",
                "parede_posterior": "8",
                "fluxo_pulmonar": "1.0",
                "fluxo_mitral": "0.9",
                "fluxo_aortico": "1.0",
                "fluxo_tricuspide": "0.5"
            }
            
            response = self.session.post(f"{BASE_URL}/parametros/1", data=params_data)
            success = response.status_code in [200, 302]
            self.log_test("Formulário Parâmetros", success, 12, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Formulário Parâmetros", False, 12, f"Erro: {str(e)}")
    
    def test_report_creation(self):
        """Teste 5: Criação de laudo (10 pts)"""
        try:
            # Acessar formulário de laudo
            report_page = self.session.get(f"{BASE_URL}/laudo/1")
            if report_page.status_code != 200:
                self.log_test("Criação de Laudo", False, 10, "Formulário inacessível")
                return
            
            # Dados do laudo
            report_data = {
                "conclusao": "Exame ecocardiográfico dentro dos padrões de normalidade. Função sistólica do ventrículo esquerdo preservada.",
                "observacoes": "Paciente colaborativo durante todo o exame. Imagens de boa qualidade técnica."
            }
            
            response = self.session.post(f"{BASE_URL}/laudo/1", data=report_data)
            success = response.status_code in [200, 302]
            self.log_test("Criação de Laudo", success, 10, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Criação de Laudo", False, 10, f"Erro: {str(e)}")
    
    def test_pdf_generation(self):
        """Teste 6: Geração de PDF (15 pts)"""
        try:
            # Gerar PDF do exame (usar ID existente)
            pdf_response = self.session.get(f"{BASE_URL}/gerar-pdf/2")
            
            if pdf_response.status_code == 200:
                # Verificar se é um PDF válido
                content_type = pdf_response.headers.get('content-type', '')
                is_pdf = 'application/pdf' in content_type or pdf_response.content.startswith(b'%PDF')
                pdf_size = len(pdf_response.content)
                
                success = is_pdf and pdf_size > 1000  # PDF deve ter pelo menos 1KB
                details = f"Tipo: {content_type}, Tamanho: {pdf_size} bytes"
                self.log_test("Geração de PDF", success, 15, details)
            else:
                self.log_test("Geração de PDF", False, 15, f"Status: {pdf_response.status_code}")
                
        except Exception as e:
            self.log_test("Geração de PDF", False, 15, f"Erro: {str(e)}")
    
    def test_user_management(self):
        """Teste 7: Gerenciamento de usuários (12 pts)"""
        try:
            # Acessar página de usuários
            users_page = self.session.get(f"{BASE_URL}/auth/users")
            if users_page.status_code != 200:
                self.log_test("Gerenciamento Usuários", False, 12, "Página inacessível")
                return
            
            # Criar novo usuário
            user_data = {
                "username": "teste_funcionalidade",
                "email": "teste@funcionalidade.com",
                "password": "TesteFuncional123!",
                "role": "user"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/users/create", data=user_data)
            success = response.status_code in [200, 302]
            self.log_test("Gerenciamento Usuários", success, 12, f"Criação usuário: {response.status_code}")
            
        except Exception as e:
            self.log_test("Gerenciamento Usuários", False, 12, f"Erro: {str(e)}")
    
    def test_search_functionality(self):
        """Teste 8: Funcionalidade de busca (8 pts)"""
        try:
            # Testar busca de pacientes
            search_page = self.session.get(f"{BASE_URL}/prontuario")
            if search_page.status_code != 200:
                self.log_test("Funcionalidade Busca", False, 8, "Página de busca inacessível")
                return
            
            # Buscar paciente
            search_data = {"nome_paciente": "Teste"}
            response = self.session.post(f"{BASE_URL}/buscar-pacientes", data=search_data)
            success = response.status_code == 200
            self.log_test("Funcionalidade Busca", success, 8, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Funcionalidade Busca", False, 8, f"Erro: {str(e)}")
    
    def test_api_endpoints(self):
        """Teste 9: Endpoints de API (10 pts)"""
        api_tests = [
            ("/api/hora-atual", 2),
            ("/api/verificar-duplicatas", 2),
            ("/api/templates-laudo", 3),
            ("/api/patologias", 3)
        ]
        
        total_points = 0
        successful_apis = 0
        
        for endpoint, points in api_tests:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    successful_apis += 1
                    total_points += points
            except:
                pass
        
        success = successful_apis >= 2  # Pelo menos 2 APIs funcionando
        self.log_test("Endpoints de API", success, total_points, f"{successful_apis}/4 APIs funcionando")
    
    def test_maintenance_panel(self):
        """Teste 10: Painel de manutenção (8 pts)"""
        try:
            # Acessar painel de manutenção (URL secreta)
            maintenance_page = self.session.get(f"{BASE_URL}/admin-vidah-sistema-2025")
            success = maintenance_page.status_code == 200
            self.log_test("Painel de Manutenção", success, 8, f"Status: {maintenance_page.status_code}")
            
        except Exception as e:
            self.log_test("Painel de Manutenção", False, 8, f"Erro: {str(e)}")
    
    def test_logout_flow(self):
        """Teste 11: Fluxo de logout (5 pts)"""
        try:
            response = self.session.get(f"{BASE_URL}/auth/logout", allow_redirects=False)
            success = response.status_code in [200, 302]
            self.log_test("Fluxo de Logout", success, 5, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Fluxo de Logout", False, 5, f"Erro: {str(e)}")
    
    def run_all_tests(self):
        """Executa todos os testes de funcionalidade"""
        print("=== TESTE DE FUNCIONALIDADE COMPLETA ===")
        print("Sistema de Ecocardiograma - Grupo Vidah")
        print("=" * 50)
        
        # Executar todos os testes em ordem
        self.test_home_page_access()
        self.test_login_flow()
        self.test_exam_creation_flow()
        self.test_parameters_form()
        self.test_report_creation()
        self.test_pdf_generation()
        self.test_user_management()
        self.test_search_functionality()
        self.test_api_endpoints()
        self.test_maintenance_panel()
        self.test_logout_flow()
        
        # Calcular score final
        print("\n" + "=" * 50)
        print("RESULTADOS FINAIS")
        print("=" * 50)
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']} ({result['points']} pts)")
        
        print(f"\nSCORE FINAL: {self.score}/{self.max_score} ({(self.score/self.max_score)*100:.1f}%)")
        
        # Classificação
        if self.score >= 90:
            classification = "EXCELENTE ⭐⭐⭐⭐⭐"
        elif self.score >= 80:
            classification = "MUITO BOM ⭐⭐⭐⭐"
        elif self.score >= 70:
            classification = "BOM ⭐⭐⭐"
        elif self.score >= 60:
            classification = "REGULAR ⭐⭐"
        else:
            classification = "PRECISA MELHORAR ⭐"
        
        print(f"CLASSIFICAÇÃO: {classification}")
        
        return self.score, self.test_results

if __name__ == "__main__":
    test = ComprehensiveFunctionalityTest()
    score, results = test.run_all_tests()