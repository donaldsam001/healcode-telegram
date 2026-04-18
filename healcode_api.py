import requests
import logging

# Cấu hình log cơ bản nếu cần
logger = logging.getLogger(__name__)

USE_MOCK = False
API_BASE_URL = "https://bw7ckw36-8080.asse.devtunnels.ms" # Loại bỏ dấu / ở cuối để dễ nối chuỗi

def _get_headers(token: str = None) -> dict:
    """Hàm hỗ trợ tạo headers, tự động thêm Bearer token nếu có."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

# ==========================================
# HEALTH & ROOT
# ==========================================

def call_health_api():
    """GET /health - Kiểm tra trạng thái server"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# CREDENTIAL
# ==========================================

def call_credential_create(username: str, provider_id: str = "telegram"):
    """POST /api/credential - Tạo hoặc lấy thông tin credential"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/credential",
            json={"provider_id": provider_id, "username": username},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_credential_token(token: str, auth_token: str):
    """POST /api/credential/token - Gửi token (yêu cầu Auth)"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/credential/token",
            headers=_get_headers(auth_token),
            json={"token": token},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_credential_me(auth_token: str):
    """GET /api/credential/me - Lấy thông tin profile hiện tại"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/credential/me",
            headers=_get_headers(auth_token),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# GIT REPO & BRANCH
# ==========================================

def get_list_repo(auth_token: str):
    """GET /api/git/repo - Lấy danh sách Repo"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/git/repo",
            headers=_get_headers(auth_token),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def update_current_repo(git_url: str, auth_token: str):
    """PUT /api/git/repo - Cập nhật repo hiện tại đang làm việc"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/git/repo",
            headers=_get_headers(auth_token),
            json={"git_url": git_url},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def add_repo(url: str, branch: str = "main", auth_token: str = None):
    """POST /api/git/repo - Thêm/Clone một repo mới"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/git/repo",
            headers=_get_headers(auth_token),
            json={"url": url, "branch": branch},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def switch_branch(branch: str, auth_token: str):
    """PUT /api/git/branche - Chuyển đổi Git Branch (Lưu ý: API ghi là 'branche')"""
    print(123)
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/git/branche",
            headers=_get_headers(auth_token),
            json={"branch": branch},
            timeout=10
        )
        print(123456)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_git_status(auth_token: str):
    """GET /api/git/status - Xem trạng thái/Vị trí hiện tại của Git"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/git/status",
            headers=_get_headers(auth_token),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# FIX REQUESTS
# ==========================================

def call_fix_api(trace_error: str, auth_token: str, priority: int = 1, metadata: dict = None):
    """
    POST /api/fix - Gửi yêu cầu sửa lỗi.
    Theo spec, trace_error truyền cả ở query và body.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/fix",
            headers=_get_headers(auth_token),
            params={"trace_error": trace_error},
            json={
                "trace_error": trace_error,
                "priority": priority,
                "metadata": metadata
            },
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_fix_status(request_id: str, auth_token: str):
    """GET /api/fix/status/{request_id} - Xem trạng thái của tiến trình Fix"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/fix/status/{request_id}",
            headers=_get_headers(auth_token),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_cancel_fix(request_id: str, auth_token: str):
    """DELETE /api/fix/cancel/{request_id} - Hủy tiến trình Fix"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/fix/cancel/{request_id}",
            headers=_get_headers(auth_token),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# QUEUE & TASKS
# ==========================================

def get_queue_stats(auth_token: str):
    """GET /api/queue/stats - Thống kê hàng đợi"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/queue/stats",
            headers=_get_headers(auth_token),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_all_tasks(auth_token: str, status: str = None):
    """GET /api/queue/tasks - Lấy tất cả tasks (có thể filter theo status)"""
    try:
        params = {"status": status} if status else {}
        response = requests.get(
            f"{API_BASE_URL}/api/queue/tasks",
            headers=_get_headers(auth_token),
            params=params,
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_repo_tasks(auth_token: str, status: str = None):
    """GET /api/repos/tasks - Lấy các tasks của repo cụ thể"""
    try:
        params = {"status": status} if status else {}
        response = requests.get(
            f"{API_BASE_URL}/api/repos/tasks",
            headers=_get_headers(auth_token),
            params=params,
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}