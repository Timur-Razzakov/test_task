from django.urls import path


from . import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("user_list/", views.ListUsersView.as_view(), name="uuser_list"),
    path("user_list/<int:pk>/", views.UserView.as_view(), name="edit_user"),
    path("search/<str:username>/", views.UserSearchView.as_view(), name="search"),

]
