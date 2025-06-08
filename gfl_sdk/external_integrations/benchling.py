import requests

API_BASE_URL = 'https://api.benchling.com/v2'
API_TOKEN = 'YOUR_BENCHLING_API_TOKEN'  # Sustituye por tu token real

def get_projects():
    '''
    Consulta básica a la API de Benchling para obtener proyectos.
    '''
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = f'{API_BASE_URL}/projects'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Benchling API error: {response.status_code}')
