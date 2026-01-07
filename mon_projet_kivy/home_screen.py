# home_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle # Importation nécessaire
from pythoncolor import PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR

class HomeScreen(Screen):
    def __init__(self, doctor_name=None, specialty=None, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        
        self.doctor_name = doctor_name
        
        # Le layout principal utilise la couleur de fond
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(50),
            spacing=dp(20)
        )
        
        # --- CORRECTION : Application de la couleur de fond avec le canvas ---
        with layout.canvas.before:
            Color(*BACKGROUND_COLOR) # Définir la couleur à partir de votre module
            self.background_rect = Rectangle(size=self.size, pos=self.pos)
        
        # S'assurer que le rectangle de fond s'ajuste avec la taille et la position
        self.bind(pos=self.update_rect, size=self.update_rect)
        # --------------------------------------------------------------------
        
        title_label = Label(
            text=f"Bienvenue, {doctor_name}",
            font_size='32sp',
            bold=True,
            size_hint_y=0.2,
            color=TEXT_COLOR # Couleur de texte
        )
        layout.add_widget(title_label)

        specialty_label = Label(
            text=f"Spécialité: {specialty}",
            font_size='20sp',
            size_hint_y=0.1,
            color=TEXT_COLOR # Couleur de texte
        )
        layout.add_widget(specialty_label)
        
        button_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.5)

        # Bouton "Ajouter un nouveau patient"
        add_patient_button = Button(
            text="Ajouter un nouveau patient",
            size_hint_y=None,
            height=dp(60),
            background_color=PRIMARY_COLOR, # Couleur de fond
            color=BACKGROUND_COLOR          # Couleur du texte (blanc)
        )
        add_patient_button.bind(on_press=self.go_to_patient_form)
        button_layout.add_widget(add_patient_button)

        # Bouton "Liste des patients"
        list_patient_button = Button(
            text="Liste des patients",
            size_hint_y=None,
            height=dp(60),
            background_color=SECONDARY_COLOR, # Couleur de fond
            color=BACKGROUND_COLOR          # Couleur du texte (blanc)
        )
        list_patient_button.bind(on_press=self.go_to_patient_list)
        button_layout.add_widget(list_patient_button)

        # Bouton "Déconnexion"
        logout_button = Button(
            text="Déconnexion",
            size_hint_y=None,
            height=dp(60),
            background_color=(0.5, 0.5, 0.5, 1), # Gris pour le bouton de déconnexion
            color=BACKGROUND_COLOR
        )
        logout_button.bind(on_press=self.go_to_login)
        button_layout.add_widget(logout_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size
    
    def go_to_patient_form(self, instance):
        self.manager.current = 'patient_form'

    def go_to_patient_list(self, instance):
        self.manager.current = 'patient_list'

    def go_to_login(self, instance):
        self.manager.current = 'login'