from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='Register'),
    path('login/', views.LoginAPI.as_view(), name="Login"),
    path('requests/', views.UserRequest.as_view(), name="Requests"),

    path('members/', views.MemberListAPI.as_view(), name="Members"),
    path('village-list/', views.VillageAPI.as_view(), name="Villages"),
    path('family/<str:pk>', views.FamilyAPI.as_view(), name="Family"),
]