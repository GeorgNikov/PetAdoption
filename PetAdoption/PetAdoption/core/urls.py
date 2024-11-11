from django.urls import path, include
from . import views
from .views import about_view, contact_view, FAQView
from ..accounts.views import UserLoginView, UserRegisterView

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('captcha/', include('captcha.urls')),
    path('faq/', FAQView.as_view(), name='faq'),
    #path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name='register'),

]