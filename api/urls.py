from django.urls import path

from . import views

# для view на  SQL запросах
urlpatterns = [
    path("registratin/", views.CreateUserView.as_view(), name="registration"),
    path("authorization/", views.LoginView.as_view(), name="authorization"),
    path("users_list/", views.GetAllUsersView.as_view(), name="users_list"),
    path("users_list/<int:pk>/", views.GetUserView.as_view(), name="users"),
    path("update_user/<int:pk>/", views.UpdateUserView.as_view(), name="update_user"),
    path("delete_user/<int:pk>/", views.DeleteUserView.as_view(), name="delete_user"),
    path("search_user/<str:username>/", views.SearchUserView.as_view(), name="search"),

]
