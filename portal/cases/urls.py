# portal/cases/urls.py
from django.urls import path
from .views import CaseListView, CaseDetailView

# CaseStatusLogListView eklediysen buraya import et
try:
    from .views import CaseStatusLogListView
    HAS_LOG = True
except Exception:
    HAS_LOG = False

urlpatterns = [
    path("", CaseListView.as_view(), name="case-list"),
    path("<int:pk>/", CaseDetailView.as_view(), name="case-detail"),
    path("<int:pk>/status-logs/", CaseStatusLogListView.as_view(), name="case-status-logs"),
]

if HAS_LOG:
    urlpatterns += [
        path("<int:pk>/status-logs/", CaseStatusLogListView.as_view(), name="case-status-logs"),
    ]
