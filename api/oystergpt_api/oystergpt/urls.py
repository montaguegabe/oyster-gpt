from __future__ import annotations

from django.urls import path

from . import views

# api-core mounts these under /api/oystergpt/.
urlpatterns = [
    path("", views.page, name="oystergpt-page"),
    path("chat/", views.ChatView.as_view(), name="oystergpt-chat"),
]
