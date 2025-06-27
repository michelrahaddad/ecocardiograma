"""
Sistema de Ecocardiograma - Grupo Vidah
Entrada principal para deploy no Render
"""

# Import from the standard app.py file
from app import app

if __name__ == "__main__":
    # This is used for development only
    # In production, Gunicorn will import the app directly
    app.run(host="0.0.0.0", port=5000, debug=False)
