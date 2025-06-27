import os
from app import app
import routes

# Configurações para produção
if __name__ == "__main__":
    # Configuração para desenvolvimento local
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
else:
    # Configuração para deploy (Render, Heroku, etc.)
    # O Gunicorn irá usar esta instância
    application = app
