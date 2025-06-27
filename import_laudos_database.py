"""
Importar Banco de Laudos de Ecocardiograma
Script para importar os templates de laudos do arquivo JSON fornecido
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import LaudoTemplate

def import_laudos_database():
    """Importa os laudos do arquivo JSON para o banco de dados"""
    
    with app.app_context():
        print("Importando banco de laudos de ecocardiograma...")
        
        # Carregar dados do JSON
        try:
            with open('attached_assets/banco_laudos_ecocardiograma_1750298093960.json', 'r', encoding='utf-8') as f:
                laudos_data = json.load(f)
        except FileNotFoundError:
            print("Arquivo JSON não encontrado. Criando dados de exemplo...")
            laudos_data = create_sample_data()
        
        # Limpar dados existentes
        LaudoTemplate.query.delete()
        db.session.commit()
        print("Dados antigos removidos")
        
        # Importar novos dados
        imported_count = 0
        for laudo_data in laudos_data:
            try:
                laudo = LaudoTemplate(
                    categoria=laudo_data.get('Categoria', 'Adulto'),
                    diagnostico=laudo_data.get('Diagnóstico', ''),
                    modo_m_bidimensional=laudo_data.get('Modo_M_Bidimensional', ''),
                    doppler_convencional=laudo_data.get('Doppler_Convencional', ''),
                    doppler_tecidual=laudo_data.get('Doppler_Tecidual', ''),
                    conclusao=laudo_data.get('Conclusão', ''),
                    ativo=True
                )
                
                db.session.add(laudo)
                imported_count += 1
                
            except Exception as e:
                print(f"Erro ao importar laudo ID {laudo_data.get('ID')}: {str(e)}")
                continue
        
        # Salvar no banco
        try:
            db.session.commit()
            print(f"✅ {imported_count} laudos importados com sucesso!")
            
            # Verificar importação
            total_laudos = LaudoTemplate.query.count()
            print(f"Total de laudos no banco: {total_laudos}")
            
            # Mostrar alguns exemplos
            exemplos = LaudoTemplate.query.limit(5).all()
            print("\nExemplos importados:")
            for exemplo in exemplos:
                print(f"- {exemplo.diagnostico} ({exemplo.categoria})")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar: {str(e)}")

def create_sample_data():
    """Cria dados de exemplo se o arquivo não existir"""
    return [
        {
            "ID": 1,
            "Categoria": "Adulto",
            "Diagnóstico": "Ecocardiograma Normal",
            "Modo_M_Bidimensional": "Avaliação bidimensional compatível com ecocardiograma normal.",
            "Doppler_Convencional": "Estudo Doppler com achados característicos de ecocardiograma normal.",
            "Doppler_Tecidual": "Doppler tecidual compatível com ecocardiograma normal, função biventricular preservada.",
            "Conclusão": "Laudo compatível com ecocardiograma normal. Seguir conduta conforme evolução clínica."
        },
        {
            "ID": 2,
            "Categoria": "Adulto", 
            "Diagnóstico": "Hipertrofia Ventricular Esquerda",
            "Modo_M_Bidimensional": "Avaliação bidimensional compatível com hipertrofia ventricular esquerda.",
            "Doppler_Convencional": "Estudo Doppler com achados característicos de hipertrofia ventricular esquerda.",
            "Doppler_Tecidual": "Doppler tecidual compatível com hipertrofia ventricular esquerda.",
            "Conclusão": "Laudo compatível com hipertrofia ventricular esquerda. Seguir conduta conforme evolução clínica."
        },
        {
            "ID": 3,
            "Categoria": "Adulto",
            "Diagnóstico": "Insuficiência Mitral Moderada", 
            "Modo_M_Bidimensional": "Avaliação bidimensional compatível com insuficiência mitral moderada.",
            "Doppler_Convencional": "Estudo Doppler com achados característicos de insuficiência mitral moderada.",
            "Doppler_Tecidual": "Doppler tecidual compatível com insuficiência mitral moderada.",
            "Conclusão": "Laudo compatível com insuficiência mitral moderada. Seguir conduta conforme evolução clínica."
        }
    ]

if __name__ == "__main__":
    import_laudos_database()