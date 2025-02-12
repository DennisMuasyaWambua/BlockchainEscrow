import requests, json, logging, yaml, base64
import blockchain_escrow_backend.settings as settings
from blockchain_escrow_backend.settings import GITHUB_TOKEN
from rest_framework.response import Response
from rest_framework import status

def authenticate_request():
    url = "https://github.com/KibokoDao-Africa/"

    response = requests.get(url,headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    })
    print(response)
    return response


def create_github_actions_workflow(repo):
        github_api_endpoint = "https://api.github.com"
        github_token = settings.GITHUB_TOKEN
        github_username = "KibokoDao-Africa"

        workflow_content = {
            "name": "CI",
            "on": {
                "push": {
                    "branches": ["main"]
                },
                "pull_request": {
                    "branches": ["main"]
                }
            },
            "jobs": {
                "test-python": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v2"},
                        {"name": "Set up Python", "uses": "actions/setup-python@v2", "with": {"python-version": "3.9"}},
                        {"name": "Install dependencies", "run": "python -m pip install --upgrade pip\npip install pytest"},
                        {"name": "Test with pytest", "run": "pytest"}
                    ]
                },
                "test-javascript": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v2"},
                        {"name": "Use Node.js", "uses": "actions/setup-node@v2", "with": {"node-version": "14"}},
                        {"run": "npm ci"},
                        {"run": "npm test"}
                    ]
                },
                "test-java": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v2"},
                        {"name": "Set up JDK 11", "uses": "actions/setup-java@v2", "with": {"java-version": "11", "distribution": "adopt"}},
                        {"name": "Build with Maven", "run": "mvn clean verify"}
                    ]
                }
            }
        }

        # Test the YAML generation separately
        print(yaml.dump(workflow_content, sort_keys=False, default_flow_style=False))

        yaml_content = yaml.dump(workflow_content, sort_keys=False, default_flow_style=False)

        # Base64 encode the YAML content
        encoded_content = base64.b64encode(yaml_content.encode()).decode()

        url = f"{github_api_endpoint}/repos/{github_username}/{repo.name}/contents/.github/testcases.yml"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "message": "Add GitHub Actions workflow",
            "content": encoded_content,
            "branch": "main"  
         }

        response = requests.put(url, headers=headers, json=data)

        
        if response.status_code == 201:
            print("GitHub Actions workflow created successfully.")
            return Response(
                    {"status": True, "message": "Workflow created successfully"},
                    status=status.HTTP_201_CREATED,
                )

        else:
            print(f"Error creating GitHub Actions workflow: {response.status_code} - {response.text}")
            return Response(
                    {"status": True, "message": f"Error creating GitHub Actions workflow: {response.status_code} - {response.text}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )