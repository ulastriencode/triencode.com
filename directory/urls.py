from django.urls import path
from .views import DirectoryUserListView

urlpatterns = [
    path("directory-users/", DirectoryUserListView.as_view(), name="directory-user-list"),
]
