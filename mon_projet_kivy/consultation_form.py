# consultation_form.py

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

class ConsultationFormScreen(Screen):
    """
    Écran pour la saisie des informations d'une nouvelle consultation.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'consultation_form'
        self.patient_id = None
        self.consultation_id = None
        
        # Application de la couleur de fond
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        self.title_label = Label(text="Nouvelle Consultation", font_size='32sp', bold=True, size_hint_y=0.1, color=PRIMARY_COLOR)
        main_layout.add_widget(self.title_label)

        scroll_view = ScrollView(size_hint=(1, 0.8))
        form_layout = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Les champs sont réorganisés pour une meilleure lisibilité
        self.fields = [
            ("Date et heure:", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Motif de consultation:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Symptômes actuels:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Poids (kg):", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Taille (cm):", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("SPO2 (%):", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Tension (mmHg):", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Température (°C):", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Antécédents médicaux:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Résultats d'examens:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Diagnostic:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Traitement prescrit:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Recommandations:", TextInput(multiline=True, size_hint_y=None, height=dp(80), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
            ("Prochain rendez-vous:", TextInput(multiline=False, size_hint_y=None, height=dp(40), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR)),
        ]

        for label_text, widget in self.fields:
            form_layout.add_widget(Label(text=label_text, halign='right', valign='middle', size_hint_x=0.4, size_hint_y=None, height=dp(40), color=TEXT_COLOR))
            widget.size_hint_x = 0.6
            form_layout.add_widget(widget)
            
        scroll_view.add_widget(form_layout)
        main_layout.add_widget(scroll_view)
        
        button_layout = BoxLayout(spacing=dp(10), size_hint_y=0.1)
        self.save_button = Button(text="Enregistrer", on_press=self.save_consultation_data, size_hint_y=None, height=dp(45), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        self.cancel_button = Button(text="Annuler", on_press=self.go_back_to_patient_detail, size_hint_y=None, height=dp(45), background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR)
        
        button_layout.add_widget(self.save_button)
        button_layout.add_widget(self.cancel_button)
        
        main_layout.add_widget(button_layout)
        
        self.add_widget(main_layout)

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size
    
    def on_enter(self, *args):
        if self.consultation_id:
            self.title_label.text = "Modifier la Consultation"
            self.load_consultation_data()
        else:
            self.title_label.text = "Nouvelle Consultation"
            self.clear_form()
            self.fields[0][1].text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    def load_consultation_data(self):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.show_popup("Erreur", "Fichier de données des patients non trouvé.")
            return

        patient = patients_data.get(self.patient_id)
        if patient and "consultations" in patient:
            for cons in patient["consultations"]:
                if cons.get("id") == self.consultation_id:
                    self.fields[0][1].text = cons.get("date_et_heure", "")
                    self.fields[1][1].text = cons.get("motif_de_consultation", "")
                    self.fields[2][1].text = cons.get("symptomes_actuels", "")
                    self.fields[3][1].text = cons.get("poids", "")
                    self.fields[4][1].text = cons.get("taille", "")
                    self.fields[5][1].text = cons.get("spo2", "")
                    self.fields[6][1].text = cons.get("tension", "")
                    self.fields[7][1].text = cons.get("temperature", "")
                    self.fields[8][1].text = cons.get("antecedants_medicaux", "")
                    self.fields[9][1].text = cons.get("resultats_d_examens", "")
                    self.fields[10][1].text = cons.get("diagnostic", "")
                    self.fields[11][1].text = cons.get("traitement_prescrit", "")
                    self.fields[12][1].text = cons.get("recommandations", "")
                    self.fields[13][1].text = cons.get("prochain_rendez_vous", "")
                    return
        self.show_popup("Erreur", "Consultation non trouvée.")

    def save_consultation_data(self, instance):
        if not self.patient_id:
            self.show_popup("Erreur", "ID du patient manquant.")
            return
        
        # Vérifier si au moins un champ essentiel est rempli
        if not self.fields[1][1].text:
            self.show_popup("Erreur", "Le motif de consultation ne peut pas être vide.")
            return

        consultation_data = {
            "id": self.consultation_id if self.consultation_id else datetime.now().strftime("%Y%m%d%H%M%S"),
            "date_et_heure": self.fields[0][1].text,
            "motif_de_consultation": self.fields[1][1].text,
            "symptomes_actuels": self.fields[2][1].text,
            "poids": self.fields[3][1].text,
            "taille": self.fields[4][1].text,
            "spo2": self.fields[5][1].text,
            "tension": self.fields[6][1].text,
            "temperature": self.fields[7][1].text,
            "antecedants_medicaux": self.fields[8][1].text,
            "resultats_d_examens": self.fields[9][1].text,
            "diagnostic": self.fields[10][1].text,
            "traitement_prescrit": self.fields[11][1].text,
            "recommandations": self.fields[12][1].text,
            "prochain_rendez_vous": self.fields[13][1].text,
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
        if "consultations" not in patient:
            patient["consultations"] = []

        if self.consultation_id:
            for i, cons in enumerate(patient["consultations"]):
                if cons.get("id") == self.consultation_id:
                    patient["consultations"][i] = consultation_data
                    break
        else:
            patient["consultations"].append(consultation_data)

        with open(PATIENT_DATA_FILE, "w") as f:
            json.dump(patients_data, f, indent=4)
        
        print(f"Consultation enregistrée avec succès pour le patient {self.patient_id}.")
        self.go_back_to_patient_detail(instance)

    def clear_form(self):
        for _, widget in self.fields:
            if isinstance(widget, TextInput):
                widget.text = ""
        self.consultation_id = None
        
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