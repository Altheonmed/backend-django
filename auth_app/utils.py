from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from auth_app.models import Doctor, Workplace, Patient, Consultation, MedicalProcedure

def create_admin_group():
    """Crée le groupe 'GeneralAdmin' et lui assigne les permissions d'administration."""
    admin_group, created = Group.objects.get_or_create(name='GeneralAdmin')

    if created:
        print("Le groupe 'GeneralAdmin' a été créé et les permissions lui ont été assignées.")

        # Permissions pour les modèles
        doctor_ct = ContentType.objects.get_for_model(Doctor)
        workplace_ct = ContentType.objects.get_for_model(Workplace)
        patient_ct = ContentType.objects.get_for_model(Patient)
        consultation_ct = ContentType.objects.get_for_model(Consultation)
        medical_procedure_ct = ContentType.objects.get_for_model(MedicalProcedure)

        # Liste des permissions à accorder au groupe
        permissions_to_add = [
            # Accès complet aux médecins
            'view_doctor', 'add_doctor', 'change_doctor', 'delete_doctor',
            # Accès complet aux cliniques
            'view_workplace', 'add_workplace', 'change_workplace', 'delete_workplace',
            # Accès en lecture seule aux patients, consultations et actes médicaux pour les statistiques
            'view_patient', 'view_consultation', 'view_medicalprocedure',
        ]
        
        # Ajout des permissions au groupe
        for perm_codename in permissions_to_add:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                admin_group.permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"La permission '{perm_codename}' n'existe pas.")
        
        # Sauvegarde
        admin_group.save()