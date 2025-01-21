import requests
from blockchain_escrow_backend.settings import GITHUB_TOKEN

def authenticate_request():
    url = "https://github.com/KibokoDao-Africa/"

    response = requests.get(url,headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    })
    print(response)
    return response