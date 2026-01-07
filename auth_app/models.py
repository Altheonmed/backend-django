import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Import requis pour RegistrationCode

# --- Modèle RegistrationCode (NOUVEAU) ---
class RegistrationCode(models.Model):
    """Modèle pour stocker les codes d'accès requis pour l'inscription des Docteurs."""
    
    # Utilisez un UUID pour un code d'accès sécurisé et non séquentiel
    code = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        editable=False
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Utilisé"
    )
    email_associated = models.EmailField(
        blank=True, 
        null=True, 
        unique=True, 
        verbose_name="Email associé (optionnel)"
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    used_by_doctor = models.OneToOneField(
        'Doctor', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Docteur ayant utilisé le code"
    )

    def __str__(self):
        return f"Code: {self.code} - Utilisé: {self.is_used}"

    class Meta:
        verbose_name = "Code d'Enregistrement"
        verbose_name_plural = "Codes d'Enregistrement"
        ordering = ['-created_at']

# --- Modèle Workplace ---
class Workplace(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()
    is_public = models.BooleanField(default=False)
    creator = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_workplaces')

    class Meta:
        verbose_name_plural = "Workplaces"

    def __str__(self):
        return self.name

# --- Modèle Doctor ---
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100, default='Généraliste')
    license_number = models.CharField(max_length=50, unique=True, null=False)
    workplaces = models.ManyToManyField('Workplace', related_name='doctors', blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        # Utilise l'objet User pour un nom cohérent
        return f"Dr. {self.user.first_name} {self.user.last_name}"

    @property
    def full_name(self):
        """Retourne le nom complet du docteur à partir du modèle User."""
        return self.user.get_full_name()

# --- Modèle Patient ---
class Patient(models.Model):
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=200, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=20, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    assigned_doctors = models.ManyToManyField('Doctor', related_name='assigned_patients', blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# --- Modèle Appointment ---
class Appointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='appointments')
    workplace = models.ForeignKey('Workplace', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    appointment_date = models.DateTimeField()
    reason_for_appointment = models.TextField()
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Rendez-vous de {self.patient.first_name} avec Dr. {self.doctor.user.first_name}"

# --- Modèle Consultation ---
class Consultation(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='consultations')
    consultation_date = models.DateTimeField(auto_now_add=True)
    reason_for_consultation = models.TextField()
    medical_report = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    attachments = models.FileField(upload_to='consultation_attachments/', blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sp2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Consultation de {self.patient.first_name} {self.patient.last_name} le {self.consultation_date.strftime('%Y-%m-%d')}"

# --- Modèle MedicalProcedure ---
class MedicalProcedure(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='medical_procedures')
    procedure_type = models.CharField(max_length=200)
    procedure_date = models.DateField()
    result = models.TextField(blank=True, null=True)
    attachments = models.FileField(upload_to='procedure_attachments/', blank=True, null=True)
    operator = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='operated_procedures')

    def __str__(self):
        return f"Acte médical pour {self.patient.first_name} {self.patient.last_name}: {self.procedure_type}"

# --- Modèle Referral (corrigé) ---
class Referral(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='referrals')
    referred_to = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='referred_patients', help_text="Médecin référé")
    referred_by = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_by_me', help_text="Médecin qui a effectué le référencement")
    specialty_requested = models.CharField(max_length=100)
    reason_for_referral = models.TextField()
    attached_documents = models.FileField(upload_to='referral_documents/', blank=True, null=True)
    date_of_referral = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True) # <-- AJOUTÉ

    def __str__(self):
        return f"Référencement pour {self.patient.first_name} {self.patient.last_name} à Dr. {self.referred_to.user.first_name}"

# --- Modèle ForumPost ---
class ForumPost(models.Model):
    author = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post de {self.author.user.username}: {self.title}"

# --- Modèle DeletedAppointment ---
class DeletedAppointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, related_name='deleted_appointments')
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, related_name='deleted_appointments')
    workplace = models.ForeignKey('Workplace', on_delete=models.SET_NULL, null=True, related_name='deleted_appointments')
    appointment_date = models.DateTimeField()
    reason_for_appointment = models.TextField()
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deletion_reason = models.CharField(max_length=50)
    deletion_comment = models.TextField(blank=True, null=True)
    deletion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deleted Appointment for {self.patient.unique_id if self.patient else 'N/A'} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"

# --- Modèle ForumComment ---
class ForumComment(models.Model):
    post = models.ForeignKey('ForumPost', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"Commentaire de {self.author.user.username} sur '{self.post.title}'"

# --- Modèle Note ---
class Note(models.Model):
    author = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='notes')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    title = models.CharField(max_length=200, default='Sans titre')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note de {self.author.user.first_name}"