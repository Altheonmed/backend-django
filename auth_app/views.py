# Fichier : votre_app/views.py

from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import viewsets, generics, status, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Count, F, Value
from django.db.models.functions import Concat # Import de Concat pour le nom complet
import uuid

from .models import (
    Patient, Doctor, Appointment, Consultation, MedicalProcedure,
    Referral, ForumPost, ForumComment, Workplace, DeletedAppointment, Note
)
from .serializers import (
    PatientSerializer, DoctorSerializer, AppointmentSerializer, ConsultationSerializer,
    MedicalProcedureSerializer, ReferralSerializer,
    ForumPostSerializer, ForumCommentSerializer, DoctorRetrieveSerializer,
    PatientListSerializer, UserLoginSerializer, WorkplaceSerializer, DoctorUpdateSerializer,
    DoctorRegistrationSerializer, DeletedAppointmentSerializer, NoteSerializer,
    # Import du nouveau Serializer pour les stats
    GlobalStatsSerializer 
)
from .permissions import IsDoctor, IsCreator

# --- Vues d'Authentification et d'Utilisateur ---
class DoctorRegisterView(generics.CreateAPIView):
    serializer_class = DoctorRegistrationSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise serializers.ValidationError({"error": "Cet email ou numéro de licence est déjà utilisé."})
        except Exception as e:
            raise serializers.ValidationError({"error": f"Une erreur est survenue lors de la création du compte: {e}"})

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not hasattr(user, 'doctor'):
                return Response({"message": "Compte non reconnu comme un médecin."}, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            user_data = {
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}",
            }
            if hasattr(user, 'doctor'):
                user_data["specialty"] = user.doctor.specialty
            return Response({
                "message": "Connexion réussie",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]
    def get(self, request):
        return Response({"message": "Bienvenue sur la ressource protégée !"}, status=status.HTTP_200_OK)

class DoctorProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorUpdateSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    
    def get_object(self):
        return get_object_or_404(Doctor, user=self.request.user)

class DoctorProfileView(generics.RetrieveAPIView):
    serializer_class = DoctorRetrieveSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Doctor, user=self.request.user)

# --- ViewSets pour les ressources API ---
class PatientViewSet(ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = self.request.user.doctor
        return Patient.objects.filter(
            Q(consultations__doctor=doctor) |
            Q(assigned_doctors=doctor) |
            Q(referrals__referred_to=doctor)
        ).distinct().prefetch_related('medical_procedures', 'consultations')
    
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                patient = serializer.save()
                doctor = self.request.user.doctor
                Consultation.objects.create(
                    patient=patient,
                    doctor=doctor,
                    reason_for_consultation="Consultation initiale (ajout du patient par le médecin)"
                )
                patient.assigned_doctors.add(doctor)
        except IntegrityError:
            raise serializers.ValidationError({"error": "Erreur lors de la création du patient et de la consultation initiale."})

class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

class WorkplaceViewSet(viewsets.ModelViewSet):
    queryset = Workplace.objects.all()
    serializer_class = WorkplaceSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated, IsDoctor]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsDoctor, IsCreator]
        else:
            self.permission_classes = [IsAuthenticated, IsDoctor]
        return super().get_permissions()

    def perform_create(self, serializer):
        try:
            doctor_profile = Doctor.objects.get(user=self.request.user)
            serializer.save(creator=doctor_profile)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("Seuls les docteurs peuvent créer une clinique.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        workplace = self.get_object()
        doctors_in_clinic = workplace.doctors.all()
        
        all_patients = Patient.objects.filter(
            Q(appointments__workplace=workplace) |
            Q(consultations__doctor__in=doctors_in_clinic) |
            Q(medical_procedures__operator__in=doctors_in_clinic)
        ).distinct().count()
        
        all_appointments = Appointment.objects.filter(workplace=workplace).count()
        all_consultations = Consultation.objects.filter(doctor__in=doctors_in_clinic).count()
        all_medical_procedures = MedicalProcedure.objects.filter(operator__in=doctors_in_clinic).count()

        doctor_stats = []
        for doctor in doctors_in_clinic:
            consultations_count = Consultation.objects.filter(doctor=doctor).count()
            appointments_count = Appointment.objects.filter(doctor=doctor).count()
            procedures_count = MedicalProcedure.objects.filter(operator=doctor).count()
            
            doctor_stats.append({
                "id": doctor.id,
                "name": f"Dr. {doctor.user.first_name} {doctor.user.last_name}",
                "consultations": consultations_count,
                "appointments": appointments_count,
                "medical_procedures": procedures_count
            })

        data = {
            "total_stats": {
                "doctors": doctors_in_clinic.count(),
                "patients": all_patients,
                "appointments": all_appointments,
                "consultations": all_consultations,
                "medical_procedures": all_medical_procedures,
            },
            "doctors_breakdown": doctor_stats
        }

        return Response(data, status=status.HTTP_200_OK)

class DeletedAppointmentsListView(generics.ListAPIView):
    queryset = DeletedAppointment.objects.all().order_by('-deletion_date')
    serializer_class = DeletedAppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

class AppointmentViewSet(ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user.doctor)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        deletion_reason = request.data.get('reason', 'unknown')
        deletion_comment = request.data.get('comment', '')

        DeletedAppointment.objects.create(
            patient=instance.patient,
            doctor=instance.doctor,
            workplace=instance.workplace,
            appointment_date=instance.appointment_date,
            reason_for_appointment=instance.reason_for_appointment,
            deleted_by=request.user,
            deletion_reason=deletion_reason,
            deletion_comment=deletion_comment
        )
        
        self.perform_destroy(instance)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user.doctor)

class ConsultationViewSet(ModelViewSet):
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    
    def get_queryset(self, *args, **kwargs):
        return Consultation.objects.filter(doctor=self.request.user.doctor).order_by('-consultation_date')

    def perform_create(self, serializer):
        doctor = self.request.user.doctor
        serializer.save(doctor=doctor)

class MedicalProcedureViewSet(ModelViewSet):
    serializer_class = MedicalProcedureSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        return MedicalProcedure.objects.filter(operator=self.request.user.doctor)

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user.doctor)

# REFERENCEMENT: Un seul ViewSet pour la création et la modification
class ReferralViewSet(ModelViewSet):
    # queryset = Referral.objects.all() <-- Nous n'utilisons plus ça
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    
    # CORRECTION : Filtre le queryset pour n'afficher que les références impliquant le médecin connecté
    def get_queryset(self):
        current_doctor = self.request.user.doctor
        return Referral.objects.filter(
            Q(referred_by=current_doctor) |  # Références faites par ce médecin
            Q(referred_to=current_doctor)    # Références reçues par ce médecin
        ).order_by('-date_of_referral').distinct()

    def perform_create(self, serializer):
        # Assigner automatiquement le médecin connecté en tant que référent
        # et le patient depuis la requête
        serializer.save(referred_by=self.request.user.doctor)
    
    def perform_update(self, serializer):
        # Permettre à tout médecin connecté de modifier le référencement
        serializer.save()

# Note: PatientReferralViewSet est supprimé car le ReferralViewSet générique gère toutes les opérations.

class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.doctor)

class ForumCommentViewSet(viewsets.ModelViewSet):
    queryset = ForumComment.objects.all().order_by('created_at')
    serializer_class = ForumCommentSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.doctor)

class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self, *args, **kwargs):
        return self.request.user.doctor.notes.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.doctor)

# Vue pour les patients du docteur
class DoctorPatientListView(generics.ListAPIView):
    serializer_class = PatientListSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    
    def get_queryset(self, *args, **kwargs):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        queryset = Patient.objects.filter(
            Q(consultations__doctor=doctor) |
            Q(assigned_doctors=doctor) |
            Q(referrals__referred_to=doctor)
        ).distinct()
        
        patient_id_filter = self.request.query_params.get('id', None)
        if patient_id_filter:
            try:
                uuid.UUID(patient_id_filter)
                queryset = queryset.filter(unique_id=patient_id_filter)
            except ValueError:
                queryset = Patient.objects.none()
        return queryset

# Vues pour les statistiques du docteur
class DoctorStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request, *args, **kwargs):
        doctor = request.user.doctor
        
        total_patients = doctor.assigned_patients.count()
        total_consultations = doctor.consultations.count()
        total_medical_procedures = doctor.operated_procedures.count()

        data = {
            'total_patients': total_patients,
            'total_consultations': total_consultations,
            'total_medical_procedures': total_medical_procedures,
        }
        return Response(data, status=status.HTTP_200_OK)

class DoctorPatientStatsView(generics.ListAPIView):
    serializer_class = PatientListSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        doctor = self.request.user.doctor
        
        patients = doctor.assigned_patients.all()

        patients = patients.annotate(
            consultations_count=Count('consultations', filter=Q(consultations__doctor=doctor), distinct=True),
            medical_procedures_count=Count('medical_procedures', filter=Q(medical_procedures__operator=doctor), distinct=True),
            referrals_count=Count('referrals', filter=Q(referrals__referred_by=doctor), distinct=True)
        )
        return patients

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for patient in queryset:
            data.append({
                'unique_id': patient.unique_id,
                'full_name': f"{patient.first_name} {patient.last_name}",
                'consultations_count': patient.consultations_count,
                'medical_procedures_count': patient.medical_procedures_count,
                'referrals_count': patient.referrals_count,
            })
        return Response(data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------
# VUE POUR LES STATISTIQUES GLOBALES 
# ----------------------------------------------------------------------

class GlobalStatsView(APIView):
    """
    Vue pour récupérer les statistiques globales de l'application, 
    y compris les totaux et les agrégations par clinique et par médecin.
    """
    permission_classes = [IsAuthenticated, IsDoctor] 

    def get(self, request, format=None):
        
        # 1. STATISTIQUES GLOBALES
        global_stats = {
            'total_doctors': Doctor.objects.count(),
            'total_workplaces': Workplace.objects.count(),
            'total_patients': Patient.objects.count(),
            'total_consultations': Consultation.objects.count(),
            'total_referrals': Referral.objects.count(),
            'total_procedures': MedicalProcedure.objects.count(),
        }

        # 2. STATISTIQUES AGRÉGÉES PAR CLINIQUE (WORKPLACE)
        stats_by_workplace = Workplace.objects.annotate(
            consultation_count=Count('doctors__consultations', distinct=True),
            patient_count=Count('doctors__assigned_patients', distinct=True),
            procedure_count=Count('doctors__operated_procedures', distinct=True)
        ).values(
            'id', 
            'name', 
            'consultation_count', 
            'patient_count', 
            'procedure_count'
        ).order_by('name')

        # 3. STATISTIQUES AGRÉGÉES PAR MÉDECIN (DOCTOR)
        stats_by_doctor = Doctor.objects.annotate(
            full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name')),
            consultation_count=Count('consultations', distinct=True),
            patient_count=Count('assigned_patients', distinct=True), 
            referral_count=Count('referred_by_me', distinct=True), 
            procedure_count=Count('operated_procedures', distinct=True)
        ).values(
            'id', 
            'full_name', 
            'specialty',
            'consultation_count', 
            'patient_count', 
            'referral_count', 
            'procedure_count'
        ).order_by('full_name')

        # COMBINAISON ET SÉRIALISATION
        data = {
            **global_stats,
            'stats_by_workplace': list(stats_by_workplace),
            'stats_by_doctor': list(stats_by_doctor),
        }

        # Le sérialiseur est uniquement là pour documenter la structure des données.
        serializer = GlobalStatsSerializer(data) 
        return Response(serializer.data)