# Fichier : votre_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import (
    ProtectedView, DoctorRegisterView, UserLoginView,
    DoctorProfileUpdateView, DoctorProfileView,
    DoctorPatientListView,
    PatientViewSet, DoctorViewSet, AppointmentViewSet, ConsultationViewSet,
    MedicalProcedureViewSet,
    # REFERENCEMENT: Utilisation d'un seul ViewSet pour la gestion globale
    ReferralViewSet, 
    NoteViewSet, ForumPostViewSet, ForumCommentViewSet, WorkplaceViewSet, DeletedAppointmentsListView,
    DoctorStatsView, DoctorPatientStatsView,
    # Import de la nouvelle vue
    GlobalStatsView 
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'medical-procedures', MedicalProcedureViewSet, basename='medical-procedure')
# REFERENCEMENT: Route générique pour toutes les opérations CRUD sur les référencements
router.register(r'referrals', ReferralViewSet, basename='referral') 
router.register(r'workplaces', WorkplaceViewSet, basename='workplace')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'forum/posts', ForumPostViewSet, basename='forum-post')
router.register(r'forum/comments', ForumCommentViewSet, basename='forum-comment')

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/doctor/', DoctorRegisterView.as_view(), name='doctor_register'),
    path('profile/', DoctorProfileView.as_view(), name='profile_detail'),
    path('profile/update/', DoctorProfileUpdateView.as_view(), name='profile_update'),
    path('doctors/me/patients/', DoctorPatientListView.as_view(), name='my_patients'),
    path('appointments/deleted/', DeletedAppointmentsListView.as_view(), name='deleted_appointments_list'), 
    path('doctors/stats/', DoctorStatsView.as_view(), name='doctor-stats'),
    path('doctors/patients/stats/', DoctorPatientStatsView.as_view(), name='doctor-patient-stats'),
    
    # NOUVELLE ROUTE POUR LES STATISTIQUES GLOBALES
    path('stats/global/', GlobalStatsView.as_view(), name='global-stats'),
    
    path('', include(router.urls)), 
    path('protected/', ProtectedView.as_view(), name='protected'),
]