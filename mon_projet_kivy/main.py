# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

# Importation de tous les écrans de l'application
from patient_form import PatientFormScreen
from patient_list import PatientListScreen
from patient_detail import PatientDetailScreen
from consultation_form import ConsultationFormScreen
from medical_act_form import MedicalActFormScreen
from auth import LoginScreen, CreateProfileScreen, load_users
from home_screen import HomeScreen

# Importation des couleurs et de la classe BaseScreen
from pythoncolor import PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR
from base_screen import BaseScreen  # Assurez-vous d'importer cette classe

class MainScreenManager(ScreenManager):
    current_doctor_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # --- Ajout du fond de couleur au ScreenManager ---
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        # ------------------------------------------------

        # Ajout des écrans d'authentification
        self.login_screen = LoginScreen(name='login')
        self.login_screen.bind(login_success=self.on_login_success)
        self.add_widget(self.login_screen)
        
        # Ajout des autres écrans
        self.add_widget(CreateProfileScreen(name='create_profile'))
        self.add_widget(PatientFormScreen(name='patient_form'))
        self.add_widget(PatientListScreen(name='patient_list'))
        self.add_widget(PatientDetailScreen(name='patient_detail'))
        self.add_widget(ConsultationFormScreen(name='consultation_form'))
        self.add_widget(MedicalActFormScreen(name='medical_act_form'))
        
        # L'application démarre toujours sur l'écran de connexion
        self.current = 'login'

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size

    def on_login_success(self, instance, value):
        """
        Gère la transition vers l'écran d'accueil après une connexion réussie.
        """
        if value:
            users = load_users()
            username = instance.last_username
            
            if username in users:
                doctor_data = users[username]
                doctor_name = doctor_data.get('username')
                specialty = doctor_data.get('specialty', 'Spécialité non définie')

                self.current_doctor_name = doctor_name
                
                # Crée et ajoute dynamiquement l'écran d'accueil
                # Le recréer à chaque login permet de mettre à jour les informations
                if self.has_screen('home'):
                    self.remove_widget(self.get_screen('home'))
                
                # Utilisez la classe HomeScreen qui hérite de BaseScreen
                home_screen = HomeScreen(
                    name='home',
                    doctor_name=doctor_name,
                    specialty=specialty
                )
                self.add_widget(home_screen)
                self.current = 'home'
    
    def go_to_patient_detail(self, patient_id):
        """
        Navigue vers l'écran de détails du patient en lui passant l'ID.
        """
        detail_screen = self.get_screen('patient_detail')
        detail_screen.patient_id = patient_id
        detail_screen.doctor_name = self.current_doctor_name
        self.current = 'patient_detail'
        
class MedicalApp(App):
    def build(self):
        self.title = 'Altheon Connect'
        return MainScreenManager()

if __name__ == '__main__':
    MedicalApp().run()