# Fichier auth.py

import json
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from pythoncolor import PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR, SECONDARY_COLOR, ACCENT_COLOR

# Constante pour la clé d'accès
ACCESS_KEY = "ma-cle-secrete-ultra-complexe-256bits"
USERS_FILE = "users.json"

# --- Fonctions pour la gestion des fichiers JSON ---
def load_users():
    """Charge les données des utilisateurs depuis un fichier JSON."""
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users_data):
    """Sauvegarde les données des utilisateurs dans un fichier JSON."""
    with open(USERS_FILE, "w") as f:
        json.dump(users_data, f, indent=4)

# --- Écrans de l'application ---
class LoginScreen(Screen):
    """Écran de connexion pour les médecins."""
    login_success = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        self.last_username = "" 
        
        # --- Application du fond de l'écran ---
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        # -------------------------------------

        main_layout = BoxLayout(orientation='vertical', padding=dp(50), spacing=dp(20))
        
        login_form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(0.8, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        login_form.add_widget(Label(text="Bienvenue, veuillez vous identifier", font_size='24sp', size_hint_y=None, height=dp(50), color=TEXT_COLOR))
        
        login_form.add_widget(Label(text="Nom d'utilisateur:", size_hint_y=None, height=dp(30), color=TEXT_COLOR))
        self.username_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)
        login_form.add_widget(self.username_input)
        
        login_form.add_widget(Label(text="Mot de passe:", size_hint_y=None, height=dp(30), color=TEXT_COLOR))
        self.password_input = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)
        login_form.add_widget(self.password_input)
        
        self.login_button = Button(text="Se connecter", size_hint_y=None, height=dp(50), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        self.login_button.bind(on_press=self.on_login)
        login_form.add_widget(self.login_button)
        
        self.error_label = Label(text="", color=ACCENT_COLOR, size_hint_y=None, height=dp(30))
        login_form.add_widget(self.error_label)
        
        main_layout.add_widget(login_form)
        
        self.create_profile_button = Button(text="Créer un nouveau profil", size_hint_y=None, height=dp(50), background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR)
        self.create_profile_button.bind(on_press=self.show_access_key_popup)
        main_layout.add_widget(self.create_profile_button)
        
        self.add_widget(main_layout)

    def on_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        users = load_users()
        
        if username in users and users[username]['password'] == password:
            self.error_label.text = "Connexion réussie !"
            self.last_username = username
            self.login_success = True
        else:
            self.error_label.text = "Nom d'utilisateur ou mot de passe invalide."
            
    def show_access_key_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text="Veuillez saisir la clé d'accès spéciale:", size_hint_y=None, height=dp(30), color=TEXT_COLOR))
        access_key_input = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)
        content.add_widget(access_key_input)
        
        def validate_key(instance):
            if access_key_input.text == ACCESS_KEY:
                popup.dismiss()
                self.manager.current = 'create_profile'
            else:
                access_key_input.text = ""
                content.add_widget(Label(text="Clé d'accès invalide!", color=ACCENT_COLOR, size_hint_y=None, height=dp(30)))
                
        validate_button = Button(text="Valider", size_hint_y=None, height=dp(40), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        validate_button.bind(on_press=validate_key)
        content.add_widget(validate_button)
        
        popup = Popup(title="Clé d'accès requise",
                      content=content,
                      size_hint=(0.8, 0.4),
                      auto_dismiss=False)
        popup.open()
        
    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size

# --- Écran de création de profil ---
class CreateProfileScreen(Screen):
    """Écran pour la création d'un nouveau profil."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'create_profile'

        # --- Application du fond de l'écran ---
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        # -------------------------------------
        
        self.layout = BoxLayout(orientation='vertical', padding=dp(50), spacing=dp(20),
                                 size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.layout)
        
        self.title_label = Label(text="Création de Profil Médecin", font_size='24sp', size_hint_y=None, height=dp(50), color=TEXT_COLOR)
        self.layout.add_widget(self.title_label)

        self.form_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        self.form_layout.add_widget(Label(text="Nom d'utilisateur:", size_hint_y=None, height=dp(30), color=TEXT_COLOR))
        self.new_username_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)
        self.form_layout.add_widget(self.new_username_input)
        
        self.form_layout.add_widget(Label(text="Mot de passe:", size_hint_y=None, height=dp(30), color=TEXT_COLOR))
        self.new_password_input = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)
        self.form_layout.add_widget(self.new_password_input)
        
        self.form_layout.add_widget(Label(text="Spécialité:", size_hint_y=None, height=dp(30), color=TEXT_COLOR))
        self.specialty_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)
        self.form_layout.add_widget(self.specialty_input)
        
        self.create_button = Button(text="Créer le profil", size_hint_y=None, height=dp(50), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        self.create_button.bind(on_press=self.on_create_profile)
        self.form_layout.add_widget(self.create_button)
        
        self.error_label = Label(text="", color=ACCENT_COLOR, size_hint_y=None, height=dp(30))
        self.form_layout.add_widget(self.error_label)
        
        self.layout.add_widget(self.form_layout)
        
        self.back_button = Button(text="Retour", size_hint_y=None, height=dp(50), background_color=(0.5, 0.5, 0.5, 1), color=BACKGROUND_COLOR)
        self.back_button.bind(on_press=self.on_back)
        self.layout.add_widget(self.back_button)

    def on_create_profile(self, instance):
        new_username = self.new_username_input.text
        new_password = self.new_password_input.text
        specialty = self.specialty_input.text
        
        if not new_username or not new_password:
            self.error_label.text = "Nom d'utilisateur et mot de passe sont obligatoires."
            return
            
        users = load_users()
        
        if new_username in users:
            self.error_label.text = "Nom d'utilisateur déjà pris."
        else:
            users[new_username] = {
                'username': new_username,
                'password': new_password,
                'specialty': specialty
            }
            save_users(users)
            self.error_label.text = "Profil créé avec succès !"
            self.manager.current = 'login'
            
    def on_back(self, instance):
        self.manager.current = 'login'
        self.new_username_input.text = ""
        self.new_password_input.text = ""
        self.specialty_input.text = ""
        self.error_label.text = ""

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size