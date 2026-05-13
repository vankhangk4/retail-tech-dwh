# ============================================================
# FILE: frontend/app.py
# Mô tả: Flask Web Application — Login + Dashboard + Superset Embed
# ============================================================

import os
import requests
from urllib.parse import urlsplit
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, Response
)
from flask import Blueprint

app = Flask(__name__, template_folder='templates', static_folder='static', root_path=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['SESSION_COOKIE_NAME'] = os.environ.get(
    'FRONTEND_SESSION_COOKIE_NAME',
    'dwh_frontend_session'
)

# ---- Configuration ----
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
SUPERSET_PUBLIC_URL = os.environ.get('SUPERSET_PUBLIC_URL', SUPERSET_URL)


def _origin_from_url(value):
    """Return scheme://host[:port] for CSP source lists."""
    parsed = urlsplit((value or '').strip())
    if not parsed.scheme or not parsed.netloc:
        return None
    return f'{parsed.scheme}://{parsed.netloc}'


def _build_csp():
    """Build a CSP that protects the app without breaking current embeds."""
    frame_sources = ["'self'"]
    connect_sources = ["'self'"]

    for superset_url in (SUPERSET_URL, SUPERSET_PUBLIC_URL):
        superset_origin = _origin_from_url(superset_url)
        if superset_origin and superset_origin not in frame_sources:
            frame_sources.append(superset_origin)
        if superset_origin and superset_origin not in connect_sources:
            connect_sources.append(superset_origin)

    directives = {
        'default-src': ["'self'"],
        'base-uri': ["'self'"],
        'connect-src': connect_sources,
        'font-src': ["'self'", 'data:'],
        'form-action': ["'self'"],
        'frame-ancestors': ["'self'"],
        'frame-src': frame_sources,
        'img-src': ["'self'", 'data:'],
        'object-src': ["'none'"],
        'script-src': ["'self'"],
        'script-src-attr': ["'none'"],
        'style-src': ["'self'"],
        'style-src-attr': ["'none'"],
    }
    return '; '.join(
        f"{directive} {' '.join(sources)}"
        for directive, sources in directives.items()
    )


SECURITY_HEADERS = {
    'Content-Security-Policy': _build_csp(),
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}


@app.after_request
def apply_security_headers(response):
    """Apply baseline security headers to every frontend response."""
    for header, value in SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)
    return response


@app.route('/robots.txt')
def robots_txt():
    return Response('User-agent: *\nDisallow:\n', mimetype='text/plain')

# ---- Proxy API calls to Auth Gateway ----

@app.route('/api/login', methods=['POST'])
def api_login():
    """Proxy login request to Auth Gateway."""
    data = request.get_json()
    try:
        r = requests.post(
            f'{API_BASE_URL}/api/login',
            json={'username': data['username'], 'password': data['password']},
            timeout=10
        )
        if r.status_code == 200:
            resp = r.json()
            session['access_token'] = resp['access_token']
            # Decode token to get user info
            import jwt
            payload = jwt.decode(resp['access_token'], options={"verify_signature": False})
            session['user_id'] = payload.get('user_id')
            session['tenant_id'] = payload.get('tenant_id')
            session['role'] = payload.get('role')
            return jsonify({'success': True, 'role': session['role']})
        elif r.status_code == 401:
            return jsonify({'success': False, 'message': 'Sai tai khoan hoac mat khau'}), 401
        elif r.status_code == 403:
            return jsonify({'success': False, 'message': 'Tai khoan bi khoa hoac cua hang khong hoat dong'}), 403
        else:
            return jsonify({'success': False, 'message': 'Loi he thong'}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/dashboard-token', methods=['GET'])
def api_dashboard_token():
    """Proxy dashboard-token request to Auth Gateway with dashboard_id."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401

    dashboard_id = request.args.get('dashboard_id', '1')
    tenant_id = request.args.get('tenant_id', '').strip() or None
    try:
        dashboard_id = int(dashboard_id)
    except ValueError:
        dashboard_id = 1

    try:
        params = {'dashboard_id': dashboard_id}
        if tenant_id:
            params['tenant_id'] = tenant_id
        r = requests.get(
            f'{API_BASE_URL}/api/dashboard-token',
            params=params,
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        if r.status_code == 200:
            return jsonify(r.json())
        else:
            return jsonify({'error': 'Khong lay duoc dashboard token', 'dashboard_id': dashboard_id}), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/me', methods=['GET'])
def api_me():
    """Proxy /me request to Auth Gateway."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401

    try:
        r = requests.get(
            f'{API_BASE_URL}/api/me',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout — clear session."""
    session.clear()
    return jsonify({'success': True})


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check."""
    try:
        r = requests.get(f'{API_BASE_URL}/health', timeout=5)
        return jsonify({'api': 'ok' if r.status_code == 200 else 'error'}), 200
    except:
        return jsonify({'api': 'unreachable'}), 200


# ---- Pages ----

@app.route('/')
def index():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register')
def register():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html',
        SUPERSET_URL=SUPERSET_PUBLIC_URL,
    )


@app.route('/api/register', methods=['POST'])
def api_register():
    """Proxy register request to Auth Gateway."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    username  = data.get('username', '').strip()
    password  = data.get('password', '')
    role      = data.get('role', 'viewer')
    tenant_id = data.get('tenant_id', '').strip() or None

    # Basic validation
    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': 'Tên đăng nhập phải từ 3 ký tự'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Mật khẩu phải ít nhất 6 ký tự'}), 400
    if role == 'user':
        role = 'viewer'
    if role not in ('viewer', 'admin'):
        return jsonify({'success': False, 'message': 'Vai trò không hợp lệ'}), 400
    if not tenant_id:
        return jsonify({'success': False, 'message': 'Vui lòng chọn cửa hàng'}), 400

    try:
        r = requests.post(
            f'{API_BASE_URL}/api/register',
            json={'username': username, 'password': password,
                  'role': role, 'tenant_id': tenant_id},
            timeout=10
        )
        if r.status_code == 200:
            return jsonify(r.json()), 200
        elif r.status_code == 409:
            return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại'}), 409
        else:
            detail = r.json().get('detail', 'Lỗi hệ thống') if r.content else 'Lỗi hệ thống'
            return jsonify({'success': False, 'message': detail}), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Không kết nối được Auth Gateway'}), 503


@app.route('/login')
def login():
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html',
        SUPERSET_URL=SUPERSET_PUBLIC_URL,
    )


@app.route('/settings')
def settings():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    return render_template(
        'settings.html',
        user={
            'role': session.get('role', 'viewer'),
            'tenant_id': session.get('tenant_id'),
            'user_id': session.get('user_id'),
        },
        SUPERSET_URL=SUPERSET_PUBLIC_URL,
    )


@app.route('/api/me/profile', methods=['GET'])
def api_me_profile_get():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.get(
            f'{API_BASE_URL}/api/me/profile',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/me/profile', methods=['PUT'])
def api_me_profile_put():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    data = request.get_json()
    try:
        r = requests.put(
            f'{API_BASE_URL}/api/me/profile',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/me/password', methods=['PUT'])
def api_me_password():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    data = request.get_json()
    try:
        r = requests.put(
            f'{API_BASE_URL}/api/me/password',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/me/avatar', methods=['POST'])
def api_me_avatar_post():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    data = request.get_json()
    try:
        r = requests.post(
            f'{API_BASE_URL}/api/me/avatar',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=15
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/me/avatar', methods=['DELETE'])
def api_me_avatar_delete():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.delete(
            f'{API_BASE_URL}/api/me/avatar',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503


@app.route('/api/me/login-history', methods=['GET'])
def api_me_login_history():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.get(
            f'{API_BASE_URL}/api/me/login-history',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'items': []}), 200


@app.route('/dashboard')
def dashboard():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    return render_template(
        'dashboard.html',
        user={
            'role': session.get('role', 'viewer'),
            'tenant_id': session.get('tenant_id'),
            'user_id': session.get('user_id'),
        },
        SUPERSET_URL=SUPERSET_PUBLIC_URL,
    )


# ---- KPI Summary API (lấy trực tiếp từ SQL Server) ----

@app.route('/api/kpi')
def api_kpi():
    """Trả về KPI summary nhanh — gọi trực tiếp SQL Server qua API Gateway."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401

    try:
        r = requests.get(
            f'{API_BASE_URL}/api/kpi',
            headers={
                'Authorization': 'Bearer ' + session.get('access_token', ''),
                'X-Tenant-ID': session.get('tenant_id', ''),
            },
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'error': 'Khong lay duoc KPI'}), 503


# ---- Admin Proxy Endpoints ----

@app.route('/api/tenants', methods=['GET'])
def api_tenants():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.get(f'{API_BASE_URL}/api/tenants',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'tenants': []}), 200


@app.route('/api/tenants', methods=['POST'])
def api_create_tenant():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') not in ('admin', 'superadmin'):
        return jsonify({'error': 'Chi admin moi co quyen tao tenant'}), 403
    data = request.get_json()
    try:
        r = requests.post(
            f'{API_BASE_URL}/api/tenants',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'error': 'Loi tao tenant'}), 500


@app.route('/api/users', methods=['GET'])
def api_users():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.get(f'{API_BASE_URL}/api/users',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'users': []}), 200


@app.route('/api/users', methods=['POST'])
def api_create_user():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') not in ('admin', 'superadmin'):
        return jsonify({'error': 'Chi admin moi co quyen tao user'}), 403
    data = request.get_json()
    try:
        r = requests.post(
            f'{API_BASE_URL}/api/users',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'error': 'Loi tao user'}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def api_user_detail(user_id):
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.get(
            f'{API_BASE_URL}/api/users/{user_id}',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'error': 'Loi tai chi tiet user'}), 500


@app.route('/api/tenants/<tenant_id>', methods=['PUT'])
def api_update_tenant(tenant_id):
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') not in ('admin', 'superadmin'):
        return jsonify({'error': 'Chi admin moi co quyen sua tenant'}), 403
    data = request.get_json()
    try:
        r = requests.put(
            f'{API_BASE_URL}/api/tenants/{tenant_id}',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'error': 'Loi sua tenant'}), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') not in ('admin', 'superadmin'):
        return jsonify({'error': 'Chi admin moi co quyen sua user'}), 403
    data = request.get_json()
    try:
        r = requests.put(
            f'{API_BASE_URL}/api/users/{user_id}',
            json=data,
            headers={
                'Authorization': f'Bearer {session["access_token"]}',
                'Content-Type': 'application/json',
            },
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'error': 'Loi sua user'}), 500


@app.route('/api/etl/logs', methods=['GET'])
def api_etl_logs():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    try:
        r = requests.get(f'{API_BASE_URL}/api/etl/logs',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10)
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'logs': []}), 200


# ---- Upload Proxy Endpoints ----

@app.route('/api/upload/<tenant_id>', methods=['POST'])
def api_upload_file(tenant_id):
    """Proxy upload NHIEU file to Auth Gateway."""
    if 'access_token' not in session:
        return jsonify({'success': False, 'message': 'Chua dang nhap'}), 401

    if session.get('role') == 'viewer' and session.get('tenant_id') != tenant_id:
        return jsonify({'success': False, 'message': 'Khong co quyen upload cho tenant nay'}), 403

    files = request.files.getlist('files')
    if not files:
        return jsonify({'success': False, 'message': 'Khong co file nao duoc chon'}), 400

    valid_files = [f for f in files if f.filename]
    if not valid_files:
        return jsonify({'success': False, 'message': 'Ten file rong'}), 400

    try:
        # Build list of tuples with same key 'files' for FastAPI list[UploadFile]
        file_list = []
        for f in valid_files:
            file_list.append(('files', (f.filename, f.read(), f.content_type)))
        r = requests.post(
            f'{API_BASE_URL}/api/upload/{tenant_id}',
            files=file_list,
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=120
        )
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Khong ket noi duoc Auth Gateway'}), 503
    except Exception as e:
        return jsonify({'success': False, 'message': f'Loi upload: {str(e)}'}), 500


@app.route('/api/upload/<tenant_id>/files', methods=['GET'])
def api_list_files(tenant_id):
    """Proxy list uploaded files."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') == 'viewer' and session.get('tenant_id') != tenant_id:
        return jsonify({'error': 'Khong co quyen'}), 403
    try:
        r = requests.get(
            f'{API_BASE_URL}/api/upload/{tenant_id}/files',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'tenant_id': tenant_id, 'files': []}), 200


@app.route('/api/upload/<tenant_id>/files/<path:filename>', methods=['DELETE'])
def api_delete_file(tenant_id, filename):
    """Proxy delete uploaded file (admin only)."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') not in ('admin', 'superadmin'):
        return jsonify({'error': 'Chi admin moi co quyen xoa file'}), 403
    try:
        r = requests.delete(
            f'{API_BASE_URL}/api/upload/{tenant_id}/files/{filename}',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'success': False, 'message': 'Loi xoa file'}), 500


@app.route('/api/upload/<tenant_id>/etl', methods=['POST'])
def api_trigger_etl(tenant_id):
    """Proxy trigger ETL."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') == 'viewer' and session.get('tenant_id') != tenant_id:
        return jsonify({'error': 'Khong co quyen'}), 403
    try:
        r = requests.post(
            f'{API_BASE_URL}/api/upload/{tenant_id}/etl',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=60
        )
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'success': False, 'message': 'Loi trigger ETL'}), 500


@app.route('/api/upload/<tenant_id>/etl/status', methods=['GET'])
def api_etl_status(tenant_id):
    """Proxy ETL status."""
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') == 'viewer' and session.get('tenant_id') != tenant_id:
        return jsonify({'error': 'Khong co quyen'}), 403
    try:
        r = requests.get(
            f'{API_BASE_URL}/api/upload/{tenant_id}/etl/status',
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10
        )
        return jsonify(r.json()), r.status_code
    except:
        return jsonify({'tenant_id': tenant_id, 'recent_logs': []}), 200


if __name__ == '__main__':
    port = int(os.environ.get('FRONTEND_PORT', 3000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
