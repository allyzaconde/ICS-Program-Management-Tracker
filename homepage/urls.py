from django.urls import path
from . import views

urlpatterns = [
    path('', views.students, name='students'),
    path('students', views.students, name='students'),
    path('faculty', views.faculty, name='faculty'),
    path('program', views.program, name='program'),
    path('about', views.about, name='about'),
    path('search', views.search, name='search'),
    path('_export=csv', views.export, name='export'),
    path('sign_up', views.sign_up, name='sign_up')
]