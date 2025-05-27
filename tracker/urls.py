from django.urls import path, include # Import include
from . import views

# Define app_name if using namespaces, otherwise remove
# app_name = 'tracker'

urlpatterns = [
    # Authentication URLs (using django.contrib.auth views)
    # path("accounts/", include("django.contrib.auth.urls")), # Includes login, logout, password reset etc.
    # Or define them manually if more control is needed:
    # path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    # path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"), # Redirect to login after logout

    # Custom signup view
    path("signup/", views.signup, name="signup"),

    # Application URLs (already defined, ensure they are protected by @login_required in views)
    path("", views.dashboard, name="dashboard"),
    path("add_medication/", views.add_medication, name="add_medication"),
    path("add_dose/", views.add_dose, name="add_dose"),
    path("history/", views.history, name="history"),
    path("statistics/", views.statistics, name="statistics"),
    path("settings/", views.settings, name="settings"),
    path("medications/", views.medications, name="medications"),
    path("medications/<int:medication_id>/edit/", views.edit_medication, name="edit_medication"),
    path("medications/<int:medication_id>/delete/", views.delete_medication, name="delete_medication"),
    path("dose/<int:dose_id>/update/<str:status>/", views.update_dose_status, name="update_dose_status"),
    path("dose/<int:dose_id>/delete/", views.delete_dose, name="delete_dose"),
]

