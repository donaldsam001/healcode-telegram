import json
import requests
import httpx
import logging
from telegram import Update
from telegram.ext import ContextTypes


USE_MOCK = True
API_BASE_URL = "https://bw7ckw36-8080.asse.devtunnels.ms/"


'''
    /api/credential
'''
def call_start_api(name: str):

        response = requests.post(
            f"{API_BASE_URL}/api/credential",
            json={
                "provider_id": "telegram",
                "username": name,
            },
            timeout=10
        )
        return response.json()


'''
    /api/credential/token
'''
def call_credential_token(token: str):

        response = requests.post(
            f"{API_BASE_URL}/api/credential/token",
            json={
                "token": token,
            },
            timeout=10
        )
        return response.json()

'''
    /api/credential/me
'''
def call_credential_me():

        response = requests.get(
            f"{API_BASE_URL}/api/credential/me",
            json={
            },
            timeout=10
        )
        return response.json()



'''
    /api/git/repo   List repo
'''
def get_list_repo():

        response = requests.get(
            f"{API_BASE_URL}/api/git/repo",
            json={
            },
            timeout=10
        )
        return response.json()

'''
    /api/git/repo   update current repo
'''
def update_current_repo(git_url: str  ):

        response = requests.put(
            f"{API_BASE_URL}/api/git/repo",
            json={
                 "git_url": git_url
            },
            timeout=10
        )
        return response.json()

'''
    /api/git/repo   clone repo
'''
def clone_repo(url: str, branch: str ):

        response = requests.post(
            f"{API_BASE_URL}/api/git/repo",
            json={
                 "url": url,
                    "branch": branch
            },
            timeout=10
        )
        return response.json()


def call_repo_api(url: str, branch: str):

        response = requests.post(
            f"{API_BASE_URL}/repo",
            json={
                 "uuid": "421d15da-47da-4133-9e03-16e3d44fd93d",
                "url": url,
                "branch": branch
            },
            timeout=10
        )
        return response.json()

def call_status_api(url: str, token: str):
# get full information of alll repo status
        try:
            response = requests.get(
                f"{API_BASE_URL}/status",
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def call_fix_api(repo_name: str, issue: str):
    """
    Backend: POST /api/fix/{repo}
    Body: FixRequestModel(repo_name, trace_error, priority...)
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/fix/{repo_name}",
            json={
                "repo_name": repo_name,
                "trace_error": issue,
                "priority": 1, # Default priority
                "metadata": {}
            },
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_cancel_api( request_id: str):
    """
    Backend: DELETE /api/fix/cancel/{request_id}
    """
    try:
        response = requests.delete(
            f"{API_BASE_URL}/cancel/{request_id}",
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_healcode_api(code: str):
    # if USE_MOCK:
    #     with open("mock/mock_healcode.json", "r") as f:
    #         return json.load(f)

    # REAL API (later)
    # if code == "cred":
    #     response = requests.get(
    #         # "{API_BASE_URL}/credentials",
    #         "{API_BASE_URL}/health",
    #         json={},
    #         timeout=10
    #     )
    #     return response.json()
    if code == "start":
        # Truyền đúng dictionary thay vì chỉ gọi biến id
        response = requests.post(
            f"{API_BASE_URL}/start",
            json={"id": "dummy_id", "name": "dummy_name", "token": "dummy"},
            timeout=10
        )
        return response.json()
    
    elif code == "list":
        response = requests.get(
            f"{API_BASE_URL}/list",
            json={},
            timeout=10
        )
        return response.json()
    
    elif code == "repo":
        response = requests.get(
            f"{API_BASE_URL}/repo",
            json={},
            timeout=10
        )
        return response.json()
    
    elif code == "branch":
        response = requests.get(
            f"{API_BASE_URL}/branch",
            json={},
            timeout=10
        )
        return response.json()
    
    elif code == "cursor":
        response = requests.get(
            f"{API_BASE_URL}/cursor",
            json={},
            timeout=10
        )
        return response.json()
        
    elif code == "status":
        response = requests.get(
            f"{API_BASE_URL}/status",
            json={},
            timeout=10
        )
        return response.json()
    
    elif code == "health":
        response = requests.get(
            f"{API_BASE_URL}/health",
            json={},
            timeout=10
        )
        return response.json()
    
    elif code == "cancel":
        response = requests.get(
            f"{API_BASE_URL}/cancel/{request_id}",
            json={},
            timeout=10
        )
        return response.json()

    
# res=call_healcode_api("health")
# print(res)