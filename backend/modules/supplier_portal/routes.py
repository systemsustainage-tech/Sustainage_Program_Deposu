from flask import Blueprint, render_template, request, redirect, url_for, flash, session

supplier_portal_bp = Blueprint('supplier_portal', __name__, url_prefix='/supplier_portal')

@supplier_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Placeholder login logic
        username = request.form.get('username')
        password = request.form.get('password')
        # TODO: Implement actual supplier authentication
        if username == 'supplier' and password == 'supplier':
            session['supplier_logged_in'] = True
            return redirect(url_for('supplier_portal.dashboard'))
        else:
            flash('Giriş başarısız.', 'danger')
    return render_template('supplier_login.html', title='Tedarikçi Girişi')

@supplier_portal_bp.route('/dashboard')
def dashboard():
    if not session.get('supplier_logged_in'):
        return redirect(url_for('supplier_portal.login'))
    return "Supplier Dashboard (Placeholder)"
