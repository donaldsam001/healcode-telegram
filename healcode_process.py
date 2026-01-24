from healcode_api import call_healcode_api

def apply_healcode(file_path):
    with open(file_path, "r") as f:
        code = f.read()

    result = call_healcode_api(code)

    with open(file_path, "w") as f:
        f.write(result["patched_code"])

    return result["suggestions"]
