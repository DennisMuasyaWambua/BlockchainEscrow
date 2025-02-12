from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CreateRepositoryView, GetRepositories

urlpatterns = [
    path('authentication/register/', RegisterView.as_view(), name='register'),
    path('authentication/login/', LoginView.as_view(), name="login"),
    path('authentication/logout/', LogoutView.as_view(), name = 'logout'),
    path('create-repo/', CreateRepositoryView.as_view(), name='github-auth'),
    path('get-repos/', GetRepositories.as_view(), name='get-repos'),
    ]