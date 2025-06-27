"""
Blueprint de Autenticação - Sistema Modular
Rotas organizadas com validações e segurança integrada
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from .services import AuthService, UserManagementService
from .decorators import login_required, admin_required, rate_limit
from .validators import AuthValidator
from .security import SecurityManager, AuditLogger
from utils.logging_system import log_user_action, log_error_with_traceback

# Criar blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=10, per_seconds=300)  # 10 tentativas por 5 minutos
def login():
    """Página de login com validações robustas"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            # Validações básicas
            if not username or not password:
                flash('Por favor, preencha todos os campos.', 'error')
                return render_template('auth/login.html')
            
            # Detectar ataques de força bruta
            ip_address = request.remote_addr
            if SecurityManager.detect_brute_force_attack(f"{ip_address}:{username}"):
                flash('Muitas tentativas de login. Tente novamente em 15 minutos.', 'error')
                AuditLogger.log_security_event('BRUTE_FORCE_DETECTED', 'HIGH', {
                    'ip': ip_address,
                    'username': username
                })
                return render_template('auth/login.html')
            
            # Tentar autenticação
            success, user, message = AuthService.authenticate_user(username, password, ip_address)
            
            if success and user:
                # Login bem-sucedido
                if AuthService.login_user_with_session(user, remember):
                    AuditLogger.log_auth_event('LOGIN_SUCCESS', user.id, {
                        'ip': ip_address,
                        'remember': remember
                    })
                    
                    next_page = request.args.get('next')
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    return redirect(url_for('index'))
                else:
                    flash('Erro interno de autenticação.', 'error')
            else:
                # Login falhado
                SecurityManager.register_failed_attempt(f"{ip_address}:{username}")
                flash(message, 'error')
                AuditLogger.log_auth_event('LOGIN_FAILED', details={
                    'ip': ip_address,
                    'username': username,
                    'reason': message
                })
        
        except Exception as e:
            log_error_with_traceback(f'Erro no login: {str(e)}')
            flash('Erro interno do sistema. Tente novamente.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout seguro com limpeza de sessões"""
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        
        if AuthService.logout_user_session():
            AuditLogger.log_auth_event('LOGOUT_SUCCESS', user_id)
            flash('Logout realizado com sucesso.', 'success')
        else:
            flash('Erro no logout.', 'error')
    
    except Exception as e:
        log_error_with_traceback(f'Erro no logout: {str(e)}')
        flash('Erro interno no logout.', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@admin_required
def list_users():
    """Lista usuários do sistema (admin apenas)"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        role_filter = request.args.get('role', '')
        
        filters = {}
        if search:
            filters['search'] = search
        if role_filter:
            filters['role'] = role_filter
        
        users_data = UserManagementService.list_users(
            page=page,
            per_page=20,
            filters=filters if filters else None
        )
        
        return render_template('auth/list_users.html', **users_data, search=search, role_filter=role_filter)
    
    except Exception as e:
        log_error_with_traceback(f'Erro ao listar usuários: {str(e)}')
        flash('Erro ao carregar usuários.', 'error')
        return redirect(url_for('index'))

@auth_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
@rate_limit(max_requests=5, per_seconds=300)  # 5 criações por 5 minutos
def create_user():
    """Criar novo usuário (admin apenas)"""
    if request.method == 'POST':
        try:
            form_data = {
                'username': request.form.get('username', '').strip(),
                'email': request.form.get('email', '').strip(),
                'password': request.form.get('password', ''),
                'role': request.form.get('role', 'user'),
                'first_name': request.form.get('first_name', '').strip(),
                'last_name': request.form.get('last_name', '').strip()
            }
            
            # Validar dados
            is_valid, field_errors = AuthValidator.validate_user_data(form_data)
            
            if not is_valid:
                for field, errors in field_errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'error')
                return render_template('auth/create_user.html')
            
            # Criar usuário
            success, user, message = UserManagementService.create_user(form_data)
            
            if success:
                AuditLogger.log_auth_event('USER_CREATED', current_user.id, {
                    'created_user_id': user.id,
                    'created_username': user.username
                })
                flash(f'Usuário {user.username} criado com sucesso.', 'success')
                return redirect(url_for('auth.list_users'))
            else:
                flash(message, 'error')
        
        except Exception as e:
            log_error_with_traceback(f'Erro ao criar usuário: {str(e)}')
            flash('Erro interno do sistema.', 'error')
    
    return render_template('auth/create_user.html')

@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Editar usuário existente (admin apenas)"""
    from .models import AuthUser
    
    user = AuthUser.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            form_data = {}
            
            # Só atualizar campos que foram fornecidos
            if request.form.get('username'):
                form_data['username'] = request.form.get('username').strip()
            if request.form.get('email'):
                form_data['email'] = request.form.get('email').strip()
            if request.form.get('password'):
                form_data['password'] = request.form.get('password')
            if request.form.get('role'):
                form_data['role'] = request.form.get('role')
            if 'first_name' in request.form:
                form_data['first_name'] = request.form.get('first_name', '').strip()
            if 'last_name' in request.form:
                form_data['last_name'] = request.form.get('last_name', '').strip()
            
            form_data['is_active_flag'] = bool(request.form.get('is_active'))
            
            # Validar apenas campos fornecidos
            if form_data:
                is_valid, field_errors = AuthValidator.validate_user_data(form_data)
                
                if not is_valid:
                    for field, errors in field_errors.items():
                        for error in errors:
                            flash(f'{field}: {error}', 'error')
                    return render_template('auth/edit_user.html', user=user)
            
            # Atualizar usuário
            success, updated_user, message = UserManagementService.update_user(user_id, form_data)
            
            if success:
                AuditLogger.log_auth_event('USER_UPDATED', current_user.id, {
                    'updated_user_id': user_id,
                    'updated_fields': list(form_data.keys())
                })
                flash(f'Usuário {updated_user.username} atualizado com sucesso.', 'success')
                return redirect(url_for('auth.list_users'))
            else:
                flash(message, 'error')
        
        except Exception as e:
            log_error_with_traceback(f'Erro ao editar usuário: {str(e)}')
            flash('Erro interno do sistema.', 'error')
    
    return render_template('auth/edit_user.html', user=user)

@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
@rate_limit(max_requests=3, per_seconds=300)  # 3 exclusões por 5 minutos
def delete_user(user_id):
    """Deletar usuário (admin apenas)"""
    try:
        # Não permitir auto-exclusão
        if user_id == current_user.id:
            flash('Você não pode deletar sua própria conta.', 'error')
            return redirect(url_for('auth.list_users'))
        
        from .models import AuthUser
        user = AuthUser.query.get_or_404(user_id)
        username = user.username
        
        success, message = UserManagementService.delete_user(user_id)
        
        if success:
            AuditLogger.log_auth_event('USER_DELETED', current_user.id, {
                'deleted_user_id': user_id,
                'deleted_username': username
            })
            flash(f'Usuário {username} deletado com sucesso.', 'success')
        else:
            flash(message, 'error')
    
    except Exception as e:
        log_error_with_traceback(f'Erro ao deletar usuário: {str(e)}')
        flash('Erro interno do sistema.', 'error')
    
    return redirect(url_for('auth.list_users'))

# APIs para AJAX
@auth_bp.route('/api/validate-username', methods=['POST'])
@admin_required
def api_validate_username():
    """API para validar username em tempo real"""
    try:
        username = request.json.get('username', '')
        is_valid, errors = AuthValidator.validate_username(username)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors
        })
    
    except Exception as e:
        log_error_with_traceback(f'Erro na validação de username: {str(e)}')
        return jsonify({'valid': False, 'errors': ['Erro interno']}), 500

@auth_bp.route('/api/validate-email', methods=['POST'])
@admin_required
def api_validate_email():
    """API para validar email em tempo real"""
    try:
        email = request.json.get('email', '')
        is_valid, errors = AuthValidator.validate_email(email)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors
        })
    
    except Exception as e:
        log_error_with_traceback(f'Erro na validação de email: {str(e)}')
        return jsonify({'valid': False, 'errors': ['Erro interno']}), 500

@auth_bp.route('/api/password-strength', methods=['POST'])
def api_password_strength():
    """API para verificar força da senha"""
    try:
        password = request.json.get('password', '')
        username = request.json.get('username', '')
        
        is_valid, errors, strength_checks = AuthValidator.validate_password(password, username)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors,
            'strength': strength_checks
        })
    
    except Exception as e:
        log_error_with_traceback(f'Erro na validação de senha: {str(e)}')
        return jsonify({'valid': False, 'errors': ['Erro interno']}), 500

@auth_bp.route('/api/csrf-token')
def api_csrf_token():
    """API para obter token CSRF"""
    try:
        token = SecurityManager.generate_csrf_token()
        return jsonify({'csrf_token': token})
    
    except Exception as e:
        log_error_with_traceback(f'Erro ao gerar token CSRF: {str(e)}')
        return jsonify({'error': 'Erro interno'}), 500

# Rota para inicialização do sistema
@auth_bp.route('/initialize-system')
def initialize_system():
    """Criar usuário administrador padrão se não existir"""
    try:
        from .models import AuthUser
        
        # Verificar se já existe algum usuário administrador
        admin_exists = AuthUser.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # Criar usuário administrador padrão
            admin_data = {
                'username': 'admin',
                'email': 'admin@grupovidah.com.br',
                'password': 'VidahAdmin2025!',
                'role': 'admin',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_verified': True
            }
            
            success, user, message = UserManagementService.create_user(admin_data)
            
            if success:
                AuditLogger.log_auth_event('SYSTEM_INITIALIZED', user.id)
                flash('Sistema inicializado! Usuário: admin | Senha: VidahAdmin2025!', 'success')
            else:
                flash(f'Erro na inicialização: {message}', 'error')
        else:
            flash('Sistema já possui usuário administrador configurado.', 'info')
        
        return redirect(url_for('auth.login'))
    
    except Exception as e:
        log_error_with_traceback(f'Erro na inicialização do sistema: {str(e)}')
        flash('Erro na inicialização do sistema.', 'error')
        return redirect(url_for('auth.login'))

# Error handlers para o blueprint
@auth_bp.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@auth_bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@auth_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return render_template('errors/429.html'), 429