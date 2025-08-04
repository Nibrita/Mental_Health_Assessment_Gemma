from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
   path('dashboard/', views.dashboard, name='dashboard'),

path('start-assessment/', views.start_assessment, name='start_assessment'),
path('chat-history/', views.chat_history, name='chat_history'),
path('download-report/', views.download_report, name='download_report'),

]
