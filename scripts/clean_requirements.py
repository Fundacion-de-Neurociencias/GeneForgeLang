import requests


def is_valid_pypi_package(pkg):
    url = f"https://pypi.org/pypi/{pkg}/json"
    try:
        response = requests.get(url, timeout=3)
        return response.status_code == 200
    except:
        return False


with open("requirements.txt", "r") as f:
    lines = f.readlines()

cleaned = []
for line in lines:
    pkg = line.strip().split("==")[0] if "==" in line else line.strip()
    if pkg and is_valid_pypi_package(pkg):
        cleaned.append(line.strip())

with open("requirements.txt", "w") as f:
    f.write("\n".join(cleaned) + "\n")

print("[✔] Cleaned requirements.txt — only valid PyPI packages remain.")
