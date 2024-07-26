from django.contrib import admin
from django.urls import path

from tests.test_integrations.test_drf.drf_test_project.views import View

urlpatterns = [
    path("some_view_prefix", View.as_view()),
    path("admin/", admin.site.urls),
]
