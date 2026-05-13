# ============================================================
# FILE: frontend/app.py
# Mô tả: Flask Web Application — Login + Dashboard + Superset Embed
# ============================================================

import fnmatch
import io
import json
import os
import secrets
from datetime import datetime
from pathlib import Path

import requests
from urllib.parse import urlsplit
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, Response
)
from flask import Blueprint

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
except ImportError:
    Credentials = None
    Flow = None
    MediaIoBaseDownload = None
    build = None

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
GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
GOOGLE_DRIVE_SHEET_MIME = 'application/vnd.google-apps.spreadsheet'
GOOGLE_DRIVE_XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
GOOGLE_DRIVE_STORE_PATH = Path(os.environ.get(
    'GOOGLE_DRIVE_STORE_PATH',
    Path(app.instance_path) / 'google_drive_connections.json',
))


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


# ---- Google Drive Connection ----

def _drive_dependencies_ready():
    return all((Credentials, Flow, MediaIoBaseDownload, build))


def _drive_client_config():
    client_id = os.environ.get('GOOGLE_DRIVE_CLIENT_ID', '').strip()
    client_secret = os.environ.get('GOOGLE_DRIVE_CLIENT_SECRET', '').strip()
    if not client_id or not client_secret:
        return None
    return {
        'web': {
            'client_id': client_id,
            'client_secret': client_secret,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'redirect_uris': [_drive_redirect_uri()],
        }
    }


def _drive_redirect_uri():
    return os.environ.get(
        'GOOGLE_DRIVE_REDIRECT_URI',
        url_for('api_google_drive_callback', _external=True),
    )


def _require_drive_runtime():
    if not _drive_dependencies_ready():
        return 'Thieu thu vien Google Drive. Cai dat google-api-python-client, google-auth va google-auth-oauthlib.'
    if not _drive_client_config():
        return 'Thieu GOOGLE_DRIVE_CLIENT_ID hoac GOOGLE_DRIVE_CLIENT_SECRET.'
    return None


def _drive_store_load():
    try:
        if not GOOGLE_DRIVE_STORE_PATH.exists():
            return {}
        return json.loads(GOOGLE_DRIVE_STORE_PATH.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}


def _drive_store_save(data):
    GOOGLE_DRIVE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOOGLE_DRIVE_STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _drive_user_key():
    return str(session.get('user_id') or '')


def _drive_default_config():
    return {
        'folder_id': '',
        'tenant_scope': 'current',
        'file_pattern': '*.xlsx;*.xls;*.csv',
        'selected_files': [],
        'schedule_time': '23:30',
    }


def _drive_entry():
    user_key = _drive_user_key()
    if not user_key:
        return {}
    return _drive_store_load().get(user_key, {})


def _drive_safe_config(payload):
    selected_files = payload.get('selected_files') or []
    if not isinstance(selected_files, list):
        selected_files = []

    config = _drive_default_config()
    config.update({
        'folder_id': str(payload.get('folder_id') or '').strip(),
        'tenant_scope': str(payload.get('tenant_scope') or 'current').strip(),
        'file_pattern': str(payload.get('file_pattern') or config['file_pattern']).strip(),
        'selected_files': [
            {
                'id': str(item.get('id') or '').strip(),
                'name': str(item.get('name') or '').strip(),
                'mimeType': str(item.get('mimeType') or '').strip(),
            }
            for item in selected_files
            if isinstance(item, dict) and str(item.get('id') or '').strip()
        ][:50],
        'schedule_time': str(payload.get('schedule_time') or config['schedule_time']).strip(),
    })
    if session.get('role') != 'superadmin' or config['tenant_scope'] not in ('current', 'all'):
        config['tenant_scope'] = 'current'
    return config


def _drive_credentials_from_entry(entry):
    creds_data = entry.get('credentials') or {}
    if not creds_data.get('token') and not creds_data.get('refresh_token'):
        return None
    expiry = creds_data.get('expiry')
    return Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.environ.get('GOOGLE_DRIVE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_DRIVE_CLIENT_SECRET'),
        scopes=GOOGLE_DRIVE_SCOPES,
        expiry=datetime.fromisoformat(expiry) if expiry else None,
    )


def _drive_save_entry(entry):
    user_key = _drive_user_key()
    if not user_key:
        return
    store = _drive_store_load()
    store[user_key] = entry
    _drive_store_save(store)


def _drive_delete_entry():
    user_key = _drive_user_key()
    if not user_key:
        return
    store = _drive_store_load()
    store.pop(user_key, None)
    _drive_store_save(store)


def _drive_build_flow(state=None):
    if _drive_redirect_uri().startswith(('http://localhost', 'http://127.0.0.1')):
        os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
    flow = Flow.from_client_config(
        _drive_client_config(),
        scopes=GOOGLE_DRIVE_SCOPES,
        state=state,
    )
    flow.redirect_uri = _drive_redirect_uri()
    return flow


def _drive_match_file(name, mime_type, pattern_text):
    patterns = [
        pattern.strip().lower()
        for pattern in (pattern_text or '').split(';')
        if pattern.strip()
    ] or ['*.xlsx', '*.xls', '*.csv']
    candidates = [name.lower()]
    if mime_type == GOOGLE_DRIVE_SHEET_MIME and not Path(name).suffix:
        candidates.append(f'{name}.xlsx'.lower())
    return any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates for pattern in patterns)


def _drive_download_file(service, drive_file):
    file_id = drive_file['id']
    name = drive_file['name']
    mime_type = drive_file.get('mimeType')
    if mime_type == GOOGLE_DRIVE_SHEET_MIME:
        request_obj = service.files().export_media(fileId=file_id, mimeType=GOOGLE_DRIVE_XLSX_MIME)
        filename = name if name.lower().endswith('.xlsx') else f'{name}.xlsx'
        content_type = GOOGLE_DRIVE_XLSX_MIME
    else:
        request_obj = service.files().get_media(fileId=file_id)
        filename = name
        content_type = mime_type or 'application/octet-stream'

    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request_obj)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return filename, buffer.read(), content_type


def _drive_file_item(raw_file):
    size = raw_file.get('size')
    return {
        'id': raw_file.get('id'),
        'name': raw_file.get('name'),
        'mimeType': raw_file.get('mimeType'),
        'modifiedTime': raw_file.get('modifiedTime'),
        'size': int(size) if str(size or '').isdigit() else None,
        'isGoogleSheet': raw_file.get('mimeType') == GOOGLE_DRIVE_SHEET_MIME,
    }


def _drive_escape_query_value(value):
    return str(value or '').replace('\\', '\\\\').replace("'", "\\'")


@app.route('/api/google-drive/status', methods=['GET'])
def api_google_drive_status():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    entry = _drive_entry()
    return jsonify({
        'connected': bool((entry.get('credentials') or {}).get('refresh_token') or (entry.get('credentials') or {}).get('token')),
        'config': {**_drive_default_config(), **(entry.get('config') or {})},
        'runtime_ready': _require_drive_runtime() is None,
        'runtime_error': _require_drive_runtime(),
    })


@app.route('/api/google-drive/config', methods=['POST'])
def api_google_drive_config():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    entry = _drive_entry()
    entry['config'] = _drive_safe_config(request.get_json(silent=True) or {})
    entry['updated_at'] = datetime.utcnow().isoformat()
    _drive_save_entry(entry)
    return jsonify({'success': True, 'config': entry['config']})


@app.route('/api/google-drive/connect-url', methods=['GET'])
def api_google_drive_connect_url():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    runtime_error = _require_drive_runtime()
    if runtime_error:
        return jsonify({'error': runtime_error}), 503
    state = secrets.token_urlsafe(24)
    session['google_drive_oauth_state'] = state
    flow = _drive_build_flow(state=state)
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    if getattr(flow, 'code_verifier', None):
        session['google_drive_code_verifier'] = flow.code_verifier
    return jsonify({'url': auth_url})


@app.route('/api/google-drive/callback', methods=['GET'])
def api_google_drive_callback():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    runtime_error = _require_drive_runtime()
    if runtime_error:
        return redirect(url_for('settings', tab='drive', drive_error=runtime_error))

    expected_state = session.pop('google_drive_oauth_state', None)
    if not expected_state or request.args.get('state') != expected_state:
        return redirect(url_for('settings', tab='drive', drive_error='OAuth state khong hop le'))

    error = request.args.get('error')
    if error:
        return redirect(url_for('settings', tab='drive', drive_error=error))

    try:
        flow = _drive_build_flow(state=expected_state)
        code_verifier = session.pop('google_drive_code_verifier', None)
        if code_verifier:
            flow.code_verifier = code_verifier
        flow.fetch_token(code=request.args.get('code'))
        credentials = flow.credentials
        existing = _drive_entry()
        existing['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token or (existing.get('credentials') or {}).get('refresh_token'),
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
        }
        existing['connected_at'] = datetime.utcnow().isoformat()
        existing.setdefault('config', _drive_default_config())
        _drive_save_entry(existing)
        return redirect(url_for('settings', tab='drive', drive='connected'))
    except Exception as exc:
        return redirect(url_for('settings', tab='drive', drive_error=str(exc)))


@app.route('/api/google-drive/disconnect', methods=['POST'])
def api_google_drive_disconnect():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    _drive_delete_entry()
    return jsonify({'success': True})


@app.route('/api/google-drive/files', methods=['GET'])
def api_google_drive_files():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401

    runtime_error = _require_drive_runtime()
    if runtime_error:
        return jsonify({'error': runtime_error}), 503

    entry = _drive_entry()
    credentials = _drive_credentials_from_entry(entry)
    if not credentials:
        return jsonify({'error': 'Chua ket noi Google Drive'}), 400

    try:
        service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
        search_text = request.args.get('q', '').strip()
        query = (
            "trashed = false and ("
            "mimeType = 'application/vnd.google-apps.spreadsheet' or "
            "mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or "
            "mimeType = 'application/vnd.ms-excel' or "
            "mimeType = 'text/csv' or "
            "name contains '.xlsx' or name contains '.xls' or name contains '.csv' or "
            "name contains '.XLSX' or name contains '.XLS' or name contains '.CSV'"
            ")"
        )
        if search_text:
            query = f"({query}) and name contains '{_drive_escape_query_value(search_text)}'"
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, modifiedTime, size)',
            orderBy='modifiedTime desc',
            pageSize=100,
        ).execute()
        return jsonify({
            'files': [_drive_file_item(item) for item in response.get('files', [])],
            'selected_files': (entry.get('config') or {}).get('selected_files') or [],
        })
    except Exception as exc:
        return jsonify({'error': f'Loi tai danh sach file Google Drive: {str(exc)}'}), 500


@app.route('/api/google-drive/sync', methods=['POST'])
def api_google_drive_sync():
    if 'access_token' not in session:
        return jsonify({'error': 'Chua dang nhap'}), 401
    if session.get('role') not in ('admin', 'superadmin'):
        return jsonify({'error': 'Chi quan tri vien moi duoc dong bo du lieu nguon'}), 403

    runtime_error = _require_drive_runtime()
    if runtime_error:
        return jsonify({'error': runtime_error}), 503

    entry = _drive_entry()
    config = {**_drive_default_config(), **(entry.get('config') or {})}

    tenant_id = session.get('tenant_id')
    if session.get('role') == 'superadmin' and config.get('tenant_scope') == 'all':
        return jsonify({'error': 'Dong bo toan he thong can cau hinh mapping thu muc theo tung chi nhanh.'}), 400
    if not tenant_id:
        return jsonify({'error': 'Khong xac dinh duoc chi nhanh de dong bo'}), 400

    credentials = _drive_credentials_from_entry(entry)
    if not credentials:
        return jsonify({'error': 'Chua ket noi Google Drive'}), 400

    try:
        service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
        selected_files = config.get('selected_files') or []
        if selected_files:
            matched_files = []
            for selected in selected_files:
                file_id = selected.get('id')
                if not file_id:
                    continue
                matched_files.append(service.files().get(
                    fileId=file_id,
                    fields='id, name, mimeType, modifiedTime, size',
                ).execute())
        else:
            if not config.get('folder_id'):
                return jsonify({'error': 'Chua chon file Google Drive de dong bo'}), 400
            files = []
            page_token = None
            while True:
                response = service.files().list(
                    q=f"'{config['folder_id']}' in parents and trashed = false",
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, modifiedTime, size)',
                    pageToken=page_token,
                ).execute()
                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            matched_files = [
                item for item in files
                if _drive_match_file(item['name'], item.get('mimeType'), config.get('file_pattern'))
            ]

        if not matched_files:
            return jsonify({'success': False, 'message': 'Khong tim thay file Google Drive phu hop.', 'files': []}), 404

        upload_files = []
        synced = []
        for item in matched_files:
            filename, content, content_type = _drive_download_file(service, item)
            upload_files.append(('files', (filename, content, content_type)))
            synced.append({'filename': filename, 'drive_file_id': item['id']})

        upload_response = requests.post(
            f'{API_BASE_URL}/api/upload/{tenant_id}',
            files=upload_files,
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=180,
        )
        response_body = upload_response.json() if upload_response.content else {}
        if not upload_response.ok:
            return jsonify({
                'success': False,
                'message': response_body.get('detail') or response_body.get('message') or 'Dong bo file vao staging that bai.',
                'upload_response': response_body,
            }), upload_response.status_code

        should_run_etl = bool((request.get_json(silent=True) or {}).get('run_etl'))
        etl_response_body = None
        if should_run_etl:
            etl_response = requests.post(
                f'{API_BASE_URL}/api/upload/{tenant_id}/etl',
                headers={'Authorization': f'Bearer {session["access_token"]}'},
                timeout=60,
            )
            etl_response_body = etl_response.json() if etl_response.content else {}
            if not etl_response.ok:
                return jsonify({
                    'success': False,
                    'message': 'Da dong bo file nhung khong kich hoat duoc ETL.',
                    'synced_files': synced,
                    'upload_response': response_body,
                    'etl_response': etl_response_body,
                }), etl_response.status_code

        return jsonify({
            'success': True,
            'tenant_id': tenant_id,
            'synced_files': synced,
            'upload_response': response_body,
            'etl_response': etl_response_body,
            'message': f'Da dong bo {len(synced)} file tu Google Drive.',
        })
    except Exception as exc:
        return jsonify({'success': False, 'error': f'Loi dong bo Google Drive: {str(exc)}'}), 500


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
        params = {}
        if session.get('role') == 'admin' and session.get('tenant_id'):
            params['tenant_id'] = session.get('tenant_id')
        r = requests.get(f'{API_BASE_URL}/api/etl/logs',
            params=params,
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            timeout=10)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Khong ket noi duoc Auth Gateway'}), 503
    except Exception as exc:
        return jsonify({'error': f'Loi lay ETL logs: {str(exc)}'}), 500


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
