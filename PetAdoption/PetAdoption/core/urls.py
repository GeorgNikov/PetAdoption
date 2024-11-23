from django.urls import path, include
from . import views
from .views import about_view, contact_view, FAQView, SheltersView
from ..accounts.views import UserRegisterView

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('captcha/', include('captcha.urls')),
    path('faq/', FAQView.as_view(), name='faq'),
    path('shelters/', SheltersView.as_view(), name='shelters'),
    path('register/', UserRegisterView.as_view(), name='register'),

]