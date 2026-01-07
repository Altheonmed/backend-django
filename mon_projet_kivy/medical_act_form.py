# medical_act_form.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle # Importation nécessaire
import json
from datetime import datetime

# Importation des couleurs depuis le module
from pythoncolor import PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR

PATIENT_DATA_FILE = "patients.json"

class MedicalActFormScreen(Screen):
    """
    Écran pour la saisie et la modification des actes médicaux.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'medical_act_form'
        self.patient_id = None
        self.act_id = None
        
        # Application de la couleur de fond
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        self.title_label = Label(text="Nouvel Acte Médical", font_size='32sp', bold=True, size_hint_y=0.1, color=PRIMARY_COLOR)
        main_layout.add_widget(self.title_label)

        scroll_view = ScrollView(size_hint=(1, 0.8))
        form_layout = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        self.fields = [
            ("Date et heure:", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Nom de l'acte:", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Description:", TextInput(multiline=True, size_hint_y=None, height=dp(120), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Résultats/Observations:", TextInput(multiline=True, size_hint_y=None, height=dp(120), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
        ]

        for label_text, widget in self.fields:
            form_layout.add_widget(Label(text=label_text, halign='right', valign='middle', size_hint_x=0.4, size_hint_y=None, height=dp(40), color=TEXT_COLOR))
            widget.size_hint_x = 0.6
            form_layout.add_widget(widget)
            
        scroll_view.add_widget(form_layout)
        main_layout.add_widget(scroll_view)
        
        button_layout = BoxLayout(spacing=dp(10), size_hint_y=0.1)
        self.save_button = Button(text="Enregistrer", on_press=self.save_act_data, size_hint_y=None, height=dp(45), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        self.cancel_button = Button(text="Annuler", on_press=self.go_back_to_patient_detail, size_hint_y=None, height=dp(45), background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR)
        
        button_layout.add_widget(self.save_button)
        button_layout.add_widget(self.cancel_button)
        
        main_layout.add_widget(button_layout)
        
        self.add_widget(main_layout)

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size

    def on_enter(self, *args):
        if self.act_id:
            self.title_label.text = "Modifier l'Acte Médical"
            self.load_act_data()
        else:
            self.title_label.text = "Nouvel Acte Médical"
            self.clear_form()
            self.fields[0][1].text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    def load_act_data(self):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.show_popup("Erreur", "Fichier de données des patients non trouvé.")
            return

        patient = patients_data.get(self.patient_id)
        if patient and "actes_medicaux" in patient:
            for act in patient["actes_medicaux"]:
                if act.get("id") == self.act_id:
                    self.fields[0][1].text = act.get("date_et_heure", "")
                    self.fields[1][1].text = act.get("nom_de_l_acte", "")
                    self.fields[2][1].text = act.get("description", "")
                    self.fields[3][1].text = act.get("resultats_observations", "")
                    return
        self.show_popup("Erreur", "Acte médical non trouvé.")

    def save_act_data(self, instance):
        if not self.patient_id:
            self.show_popup("Erreur", "ID du patient manquant.")
            return

        # Vérifier si l'acte a un nom
        if not self.fields[1][1].text:
            self.show_popup("Erreur", "Le nom de l'acte ne peut pas être vide.")
            return

        act_data = {
            "id": self.act_id if self.act_id else datetime.now().strftime("%Y%m%d%H%M%S"),
            "date_et_heure": self.fields[0][1].text,
            "nom_de_l_acte": self.fields[1][1].text,
            "description": self.fields[2][1].text,
            "resultats_observations": self.fields[3][1].text,
        }

        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        if self.patient_id not in patients_data:
            self.show_popup("Erreur", "Patient non trouvé dans le fichier de données.")
            return

        patient = patients_data[self.patient_id]
        if "actes_medicaux" not in patient:
            patient["actes_medicaux"] = []

        if self.act_id:
            for i, act in enumerate(patient["actes_medicaux"]):
                if act.get("id") == self.act_id:
                    patient["actes_medicaux"][i] = act_data
                    break
        else:
            patient["actes_medicaux"].append(act_data)

        with open(PATIENT_DATA_FILE, "w") as f:
            json.dump(patients_data, f, indent=4)
        
        print(f"Acte médical enregistré avec succès pour le patient {self.patient_id}.")
        self.go_back_to_patient_detail(instance)

    def clear_form(self):
        for _, widget in self.fields:
            if isinstance(widget, TextInput):
                widget.text = ""
        self.act_id = None
        
    def go_back_to_patient_detail(self, instance):
        self.clear_form()
        self.manager.current = 'patient_detail'

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, color=TEXT_COLOR))
        
        def dismiss_popup(instance):
            popup.dismiss()
            
        close_button = Button(text="OK", size_hint_y=None, height=dp(40), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        close_button.bind(on_press=dismiss_popup)
        content.add_widget(close_button)
        
        popup = Popup(title=title,
                      content=content,
                      size_hint=(0.8, 0.4),
                      auto_dismiss=False)
        # Application de la couleur de fond au popup
        with popup.canvas.before:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=popup.pos, size=popup.size)
        popup.open()