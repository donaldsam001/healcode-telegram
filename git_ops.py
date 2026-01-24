import subprocess

def run(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr

def clone_repo(repo_url):
    return run(f"git clone {repo_url}")

def pull_repo(path):
    return run("git pull", cwd=path)

def commit_and_push(path, message="Healcode AI update"):
    run("git add .", cwd=path)
    run(f'git commit -m "{message}"', cwd=path)
    return run("git push", cwd=path)
