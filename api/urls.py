from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='Register'),
    path('login/', views.LoginAPI.as_view(), name="Login"),
    path('requests/', views.UserRequest.as_view(), name="Requests"),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', views.ForgotPasswordAPI.as_view(), name='forgot-password'),

    path('members/', views.MemberListAPI.as_view(), name="Members"),
    path('village-list/', views.VillageAPI.as_view(), name="Villages"),
    path('family/<str:pk>', views.FamilyAPI.as_view(), name="Family"),
    path('add-member/<str:pk>', views.MemberAPI.as_view(), name="Add-Member"),
    path('event/<str:pk>', views.EventAPI.as_view(), name="Event"),
    path('events/', views.EventListAPI.as_view(), name="Event-List"),
    path('content/', views.ContentListAPI.as_view(), name="Content"),
    path('committee-members/', views.CommitteeMemberListAPI.as_view(), name="Committee-Members"),
    path('blogs/', views.BlogListAPI.as_view(), name="Blogs"),
    
    path('homepage', views.homepage, name="Homepage"),
]