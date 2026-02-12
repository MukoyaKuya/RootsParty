from django.urls import path
from . import views

app_name = 'aspirants'

urlpatterns = [
    path('register/', views.aspirant_registration, name='aspirant_registration'),
    path('register/<str:draft_token>/', views.aspirant_registration, name='aspirant_registration_draft'),
    path('status/', views.aspirant_status, name='aspirant_status'),
    path('check-id/', views.check_aspirant_id, name='check_aspirant_id'),
    path('list/', views.aspirant_list, name='aspirant_list'),
    path('<uuid:uuid>/', views.aspirant_detail, name='aspirant_detail'),
    path('roles/<slug:slug>/', views.role_detail, name='role_detail'),
    
    # MP Selection flow
    path('mps/', views.mp_list, name='mp_list'),
    path('mps/county/<slug:slug>/', views.mp_county_detail, name='mp_county_detail'),
    path('mps/candidate/<slug:constituency_slug>/', views.mp_candidate_detail, name='mp_candidate_detail'),
    
    # PDF Downloads (Staff only)
    path('download/profile/<uuid:uuid>/', views.download_aspirant_pdf, name='download_aspirant_pdf'),
    path('download/report/', views.download_aspirants_list_pdf, name='download_aspirants_list_pdf'),
]
