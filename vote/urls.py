from django.urls import path
import vote.views

urlpatterns = [
    path('', vote.views.index, name='index'),  # Root URL shows the index page
    path("register_manager/", vote.views.register_manager, name="register_manager"),
    path("login_manager/", vote.views.login_manager, name="login_manager"),
    path("manager_dashboard/", vote.views.manager_dashboard, name="manager_dashboard"),
    
]
