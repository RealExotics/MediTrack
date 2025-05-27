from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Import auth views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Include tracker app URLs (signup is defined there)
    path("", include("tracker.urls")),

    # Add Django built-in auth URLs
    # Use custom template for login
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    # Use default logout view, redirect to login page after logout
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # Add other auth URLs if needed (password reset, etc.) later
    # path("accounts/", include("django.contrib.auth.urls")), # This includes more than just login/logout
]

# Add settings for login/logout redirects if not handled by views
# LOGIN_REDIRECT_URL = "/"  # Or 'dashboard'
# LOGOUT_REDIRECT_URL = "/login/" # Or wherever you want to redirect after logout

