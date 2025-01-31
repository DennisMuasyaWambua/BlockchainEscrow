from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User,Repo
from testcases.serializers import UserSerializers, RepoSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .utils import authenticate_request
import jwt, requests, logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework import status

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = authenticate(username=email, password=password)

        if user is None:
            raise AuthenticationFailed("Please provide correct username and password")

        token = RefreshToken.for_user(user)

       
        
        return Response({
            "status": True,
            "message": "Login Successful",
            'access_token': str(token.access_token),
            'expires_in': '3600',
            'token_type': 'Bearer',
        })

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.GET('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated!")
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")
        user = User.objects.filter(id =payload['id']).first()
        serializer = UserSerializers(user)
        return Response(serializer.data)
    
class LogoutView(APIView):
      def post(self,request):
          response = Response()
          response.delete_cookie('jwt')
          response.data = {
              'message': 'Successfully logged out',
          }
          return response
      
class CreateRepositoryView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class = RepoSerializer
    def post(self, request):
        url = "https://api.github.com/orgs/KibokoDao-Africa/repos"

        # Serialize data
        serializer = self.serializer_class(data=request.data)

        payload = None

        if serializer.is_valid():
            # Extract validated data
            owner = request.user
            name = serializer.validated_data.get("name")
            description = serializer.validated_data.get("description", "")
            private = serializer.validated_data.get("private", False)
            has_issues = serializer.validated_data.get("has_issues", True)
            has_projects = serializer.validated_data.get("has_projects", True)
            has_wiki = serializer.validated_data.get("has_wiki", True)

            print(owner)

            # Prepare API request payload (without `owner`)
            payload = {
                "name": name,
                "description": description,
                "private": private,
                "has_issues": has_issues,
                "has_projects": has_projects,
                "has_wiki": has_wiki,
            }
            print(payload)

            # Make API request to GitHub
            response = requests.post(
                url,
                json=payload,  # Use `json` to send a JSON payload
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            # Log the response for debugging
            print(response.status_code, response.json())

            logging.info(response.status_code, response.json())

            if response.status_code == 201:
                # Save the repository locally
                repo = Repo.objects.create(
                    owner=owner,
                    name=name,
                    description=description,
                    private=private,
                    has_issues=has_issues,
                    has_projects=has_projects,
                    has_wiki=has_wiki,
                )
                # Create the GitHub Actions workflow
                self.create_github_actions_workflow(repo)

                return Response(
                    {"status": True, "message": "Repository created successfully"},
                    status=status.HTTP_201_CREATED,
                )

            # Handle API errors
            return Response(
                {
                    "status": False,
                    "message": "Repository creation failed",
                    "error": response.json(),
                },
                status=response.status_code,
            )
        print(payload)
        return Response(
            {"status": False, "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    def create_github_actions_workflow(self, repo):
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

        url = f"{github_api_endpoint}/repos/{github_username}/{repo.name}/actions/workflows"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json"
        }
        data = {
            "content": json.dumps(workflow_content).encode().decode("utf-8"),
            "message": "Add GitHub Actions workflow"
        }

        response = requests.put(url, headers=headers, data=json.dumps(data))
        if response.status_code == 201:
            print("GitHub Actions workflow created successfully.")
            return Response(
                    {"status": True, "message": "Workflow created successfully"},
                    status=status.HTTP_201_CREATED,
                )

        else:
            print(f"Error creating GitHub Actions workflow: {response.status_code} - {response.json()['message']}")
            return Response(
                    {"status": True, "message": "Workflow not created"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
