"""
Testes para Geração de PDF
Funcionalidade crítica para relatórios médicos
"""

import unittest
import tempfile
import os
from app import app, db
from models import Exame, ParametrosEcocardiograma, LaudoEcocardiograma, Medico
from utils.pdf_generator_fixed import gerar_pdf_completo


class TestPDFGeneration(unittest.TestCase):
    """Testes críticos para geração de PDF"""

    def setUp(self):
        """Configurar ambiente de teste"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Criar médico de teste
            self.medico = Medico()
            self.medico.nome = 'Dr. Teste'
            self.medico.crm = '12345-SP'
            self.medico.ativo = True
            db.session.add(self.medico)
            
            # Criar exame de teste
            self.exame = Exame()
            self.exame.nome_paciente = 'Paciente Teste'
            self.exame.data_nascimento = '01/01/1980'
            self.exame.idade = 43
            self.exame.sexo = 'Masculino'
            self.exame.data_exame = '18/06/2025'
            db.session.add(self.exame)
            db.session.flush()
            
            # Criar parâmetros de teste
            self.parametros = ParametrosEcocardiograma()
            self.parametros.exame_id = self.exame.id
            self.parametros.atrio_esquerdo = 36.0
            self.parametros.raiz_aorta = 35.0
            db.session.add(self.parametros)
            
            # Criar laudo de teste
            self.laudo = LaudoEcocardiograma()
            self.laudo.exame_id = self.exame.id
            self.laudo.modo_m_bidimensional = 'Teste modo M'
            self.laudo.conclusao = 'Exame normal'
            db.session.add(self.laudo)
            
            db.session.commit()

    def tearDown(self):
        """Limpar ambiente de teste"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_pdf_generation(self):
        """Teste geração de PDF com dados válidos"""
        with app.app_context():
            exame = Exame.query.first()
            self.assertIsNotNone(exame)
            
            # PDF deve ser gerado sem erros
            try:
                pdf_path = gerar_pdf_completo(exame.id)
                self.assertTrue(os.path.exists(pdf_path))
                self.assertTrue(os.path.getsize(pdf_path) > 1000)  # PDF não vazio
                
                # Limpar arquivo temporário
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
                    
            except Exception as e:
                self.fail(f"PDF generation failed: {str(e)}")

    def test_exam_data_integrity(self):
        """Teste integridade dos dados do exame"""
        with app.app_context():
            exame = Exame.query.first()
            self.assertEqual(exame.nome_paciente, 'Paciente Teste')
            self.assertEqual(exame.data_exame, '18/06/2025')
            
            parametros = ParametrosEcocardiograma.query.filter_by(exame_id=exame.id).first()
            self.assertIsNotNone(parametros)
            self.assertEqual(parametros.atrio_esquerdo, 36.0)
            
            laudo = LaudoEcocardiograma.query.filter_by(exame_id=exame.id).first()
            self.assertIsNotNone(laudo)
            self.assertEqual(laudo.conclusao, 'Exame normal')


if __name__ == '__main__':
    unittest.main()