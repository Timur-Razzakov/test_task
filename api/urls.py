from django.urls import path

from . import views

urlpatterns = [
    path("registratin/", views.SignUpView.as_view(), name="registration"),
    path("authorization/", views.LoginView.as_view(), name="authorization"),
    path("users_list/", views.ListUsersView.as_view(), name="users_list"),
    path("users_list/<int:pk>/", views.UserView.as_view(), name="users"),
    path("search/<str:username>/", views.UserSearchView.as_view(), name="search"),

]
