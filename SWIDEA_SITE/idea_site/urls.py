from django.urls import path
from . import views


app_name = 'idea_site'

urlpatterns = [
    path('', views.idea_list, name='idea_list'),
    path('ideas/create/', views.idea_create, name='idea_create'),
    path('ideas/<int:pk>/', views.idea_detail, name='idea_detail'),
    path('ideas/<int:pk>/update/', views.idea_update, name='idea_update'),
    path('ideas/<int:pk>/delete/', views.idea_delete, name='idea_delete'),
    path('ideas/<int:pk>/interest/', views.idea_interest, name='idea_interest'),
    path('ideas/<int:pk>/star/', views.idea_star, name='idea_star'),

    #개발툴
    path('devtools/', views.devtool_list, name='devtool_list'),
    path('devtools/create/',views.devtool_create, name='devtool_create'),
    path('devtools/<int:pk>/', views.devtool_detail, name='devtool_detail'),
    path('devtools/<int:pk>/update/', views.devtool_update, name='devtool_update'),
    path('devtools/<int:pk>/delete/', views.devtool_delete, name='devtool_delete'),
    

]