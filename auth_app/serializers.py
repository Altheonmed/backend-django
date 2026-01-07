from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction # Import requis pour gérer la transaction atomique
from .models import (
    Patient, Doctor, Appointment, Consultation, MedicalProcedure,
    Referral, ForumPost, ForumComment, Workplace, DeletedAppointment, Note,
    RegistrationCode # NOUVEL IMPORT
)
from datetime import date

# --- Sérialiseurs de base ---

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class WorkplaceSerializer(serializers.ModelSerializer):
    creator_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Workplace
        fields = ['id', 'name', 'address', 'is_public', 'creator', 'creator_details']
        read_only_fields = ['creator']
        
    def get_creator_details(self, obj):
        # Évite les erreurs de circularité si un Doctor est sérialisé avec ses workplaces
        if obj.creator:
            return {
                'id': obj.creator.id,
                'full_name': obj.creator.full_name,
                'specialty': obj.creator.specialty
            }
        return None

# --- Sérialiseurs Doctor ---

class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'email', 'specialty', 'license_number', 'phone_number', 'address', 'workplaces']
        depth = 1 # Pour inclure les détails des workplaces

class DoctorRetrieveSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    workplaces = WorkplaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'email', 'specialty', 'license_number', 'phone_number', 'address', 'workplaces']

class DoctorUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'email', 'specialty', 'license_number', 'phone_number', 'address', 'workplaces']
        extra_kwargs = {'workplaces': {'required': False}}

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user_instance = instance.user

        if 'first_name' in user_data:
            user_instance.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user_instance.last_name = user_data['last_name']
        if 'email' in user_data:
            new_email = user_data['email']
            if User.objects.exclude(pk=user_instance.pk).filter(email=new_email).exists():
                raise serializers.ValidationError({"email": "Cet email est déjà utilisé."})
            user_instance.username = new_email
            user_instance.email = new_email
        user_instance.save()
        
        # Mise à jour des champs du docteur
        for attr, value in validated_data.items():
            if attr == 'workplaces':
                instance.workplaces.set(value)
            else:
                setattr(instance, attr, value)
        
        instance.save()
        return instance

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    registration_code = serializers.CharField(write_only=True, required=True) 
    
    class Meta:
        model = Doctor
        fields = ['email', 'password', 'first_name', 'last_name', 'license_number', 'specialty', 'workplaces', 'registration_code'] 
        extra_kwargs = {
            'license_number': {'required': True, 'write_only': True},
            'specialty': {'required': False, 'write_only': True},
            'workplaces': {'required': False}
        }
        
    def validate(self, data):
        """
        Valide le code d'enregistrement (lecture avec .get()).
        """
        code_str = data.get('registration_code') 
        
        if not code_str:
            raise serializers.ValidationError({"registration_code": "Le code d'enregistrement est requis."})
        
        try:
            # Tente de récupérer un code non utilisé correspondant à l'UUID fourni
            code_obj = RegistrationCode.objects.get(code=code_str, is_used=False)
            
            # Si un email spécifique est associé au code, vérifie la correspondance
            if code_obj.email_associated and code_obj.email_associated != data['email']:
                 raise serializers.ValidationError({"registration_code": "Ce code d'enregistrement n'est pas associé à cet email."})
            
            # Stocke l'objet code validé pour l'utiliser dans create()
            self.code_object = code_obj 
            
        except (RegistrationCode.DoesNotExist, ValueError): # ValueError pour UUID invalide
            raise serializers.ValidationError({"registration_code": "Code d'enregistrement invalide ou déjà utilisé."})
        
        # Validation existante (email/licence)
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Un utilisateur avec cet email existe déjà."})
            
        if Doctor.objects.filter(license_number=data['license_number']).exists():
            raise serializers.ValidationError({"license_number": "Ce numéro de licence est déjà utilisé."})
            
        return data # Retourne le dictionnaire 'data' INTACT (avec 'registration_code')

    @transaction.atomic 
    def create(self, validated_data):
        """
        Crée l'utilisateur et le docteur.
        
        CORRECTION: Suppression de l'argument 'is_doctor=True' dans create_user.
        """
        validated_data.pop('registration_code') 
        
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        workplaces_data = validated_data.pop('workplaces', [])

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            # is_doctor=True <- LIGNE SUPPRIMÉE/COMMENTÉE POUR CORRIGER L'ERREUR
        )
        doctor = Doctor.objects.create(user=user, **validated_data)
        doctor.workplaces.set(workplaces_data)
        
        # MARQUER LE CODE COMME UTILISÉ
        self.code_object.is_used = True
        self.code_object.used_by_doctor = doctor
        self.code_object.save()
        
        return doctor

# --- Sérialiseurs Patient ---

class PatientListSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['unique_id', 'first_name', 'last_name', 'date_of_birth', 'age']
        
    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
            return age
        return None

class SimpleConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['id', 'consultation_date', 'reason_for_consultation', 'medical_report', 'diagnosis', 'medications', 'weight', 'height', 'sp2', 'temperature', 'blood_pressure']

class MedicalProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalProcedure
        fields = '__all__'
        read_only_fields = ('operator',)

class ReferralSerializer(serializers.ModelSerializer):
    referred_to_details = DoctorSerializer(source='referred_to', read_only=True)
    referred_by_details = DoctorSerializer(source='referred_by', read_only=True)
    patient_details = PatientListSerializer(source='patient', read_only=True)

    class Meta:
        model = Referral
        fields = [
            'id', 'patient', 'referred_to', 'referred_by',
            'specialty_requested', 'reason_for_referral', 'attached_documents',
            'date_of_referral', 'comments', 
            'referred_to_details', 'referred_by_details', 'patient_details'
        ]
        read_only_fields = ('referred_by', 'date_of_referral', 'referred_to_details', 'referred_by_details', 'patient_details')

class PatientSerializer(serializers.ModelSerializer):
    consultations = SimpleConsultationSerializer(many=True, read_only=True)
    medical_procedures = MedicalProcedureSerializer(many=True, read_only=True)
    referrals = ReferralSerializer(many=True, read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('unique_id', 'age')
        
    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
            return age
        return None

# --- Autres sérialiseurs ---

class AppointmentSerializer(serializers.ModelSerializer):
    patient_details = PatientListSerializer(source='patient', read_only=True)
    workplace_details = WorkplaceSerializer(source='workplace', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'patient_details', 'doctor', 'workplace', 'workplace_details', 'appointment_date', 'reason_for_appointment', 'status']
        read_only_fields = ('doctor', 'status', 'patient_details', 'workplace_details',)

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ('doctor', 'consultation_date',)

class ForumCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.user.first_name', read_only=True)
    author_specialty = serializers.CharField(source='author.specialty', read_only=True)

    class Meta:
        model = ForumComment
        fields = ['id', 'post', 'author', 'author_name', 'author_specialty', 'content', 'created_at', 'is_private']
        read_only_fields = ['author']

class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.user.first_name', read_only=True)
    author_specialty = serializers.CharField(source='author.specialty', read_only=True)
    comments = ForumCommentSerializer(many=True, read_only=True)

    class Meta:
        model = ForumPost
        fields = ['id', 'author', 'author_name', 'author_specialty', 'title', 'content', 'created_at', 'comments']
        read_only_fields = ['author']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'patient', 'author']
        read_only_fields = ('author', 'created_at')

class DeletedAppointmentSerializer(serializers.ModelSerializer):
    patient_details = PatientListSerializer(source='patient', read_only=True)
    doctor_details = DoctorRetrieveSerializer(source='doctor', read_only=True)
    workplace_details = WorkplaceSerializer(source='workplace', read_only=True)
    deleted_by_name = serializers.CharField(source='deleted_by.username', read_only=True)

    class Meta:
        model = DeletedAppointment
        fields = ['id', 'patient_details', 'doctor_details', 'workplace_details', 'appointment_date', 'reason_for_appointment', 'deletion_date', 'deletion_reason', 'deletion_comment', 'deleted_by_name']

# ----------------------------------------------------------------------
# NOUVEAU SERIALIZEUR POUR LES STATISTIQUES GLOBALES
# ----------------------------------------------------------------------

class GlobalStatsSerializer(serializers.Serializer):
    # STATS GLOBALES
    total_doctors = serializers.IntegerField(read_only=True)
    total_workplaces = serializers.IntegerField(read_only=True)
    total_patients = serializers.IntegerField(read_only=True)
    total_consultations = serializers.IntegerField(read_only=True)
    total_referrals = serializers.IntegerField(read_only=True)
    total_procedures = serializers.IntegerField(read_only=True)
    
    # STATS PAR WORKPLACE
    stats_by_workplace = serializers.ListField(child=serializers.DictField(), read_only=True)
    
    # STATS PAR DOCTOR
    stats_by_doctor = serializers.ListField(child=serializers.DictField(), read_only=True)