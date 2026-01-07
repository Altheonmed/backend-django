# patient_form.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
import json
from kivy.uix.scrollview import ScrollView  # 1. Importez ScrollView

# Importation des couleurs depuis le module
from pythoncolor import PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR

PATIENT_DATA_FILE = "patients.json"

class PatientFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'patient_form'
        self.patient_id = None
        
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        self.title_label = Label(text="Fiche Patient", font_size='32sp', bold=True, size_hint_y=0.15, color=PRIMARY_COLOR)
        main_layout.add_widget(self.title_label)

        # 2. Créez un ScrollView et ajoutez le GridLayout à l'intérieur
        scroll_view = ScrollView(size_hint=(1, 1)) 
        
        form_layout = GridLayout(
            cols=2, 
            spacing=dp(8),
            size_hint_y=None,  # 3. Supprimez la hauteur fixe et laissez-le s'ajuster
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        self.field_widgets = {
            "id": TextInput(multiline=False, size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "nom_complet": TextInput(multiline=False, size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "age": TextInput(multiline=False, input_type='number', size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "date_de_naissance": TextInput(multiline=False, size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "sexe": self.create_gender_buttons(),
            "groupe_sanguin": self.create_blood_group_buttons(),
            "adresse": TextInput(multiline=False, size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "numero_telephone": TextInput(multiline=False, input_type='tel', size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "email": TextInput(multiline=False, input_type='mail', size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "personne_a_contacter": TextInput(multiline=False, size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "numero_personne_a_contacter": TextInput(multiline=False, input_type='tel', size_hint_y=None, height=dp(35), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
            "antecedants_medicaux": TextInput(multiline=True, size_hint_y=None, height=dp(70), background_color=(1, 1, 1, 1), foreground_color=TEXT_COLOR),
        }

        self.field_order = [
            ("ID du patient:", "id"),
            ("Nom complet:", "nom_complet"),
            ("Âge:", "age"),
            ("Date de naissance (AAAA-MM-JJ):", "date_de_naissance"),
            ("Sexe:", "sexe"),
            ("Groupe sanguin:", "groupe_sanguin"),
            ("Adresse:", "adresse"),
            ("Numéro de téléphone:", "numero_telephone"),
            ("Email:", "email"),
            ("Personne à contacter:", "personne_a_contacter"),
            ("Numéro de la personne à contacter:", "numero_personne_a_contacter"),
            ("Antécédents médicaux:", "antecedants_medicaux"),
        ]

        for label_text, field_key in self.field_order:
            widget = self.field_widgets[field_key]
            form_layout.add_widget(Label(text=label_text, halign='right', valign='middle', size_hint_x=0.4, size_hint_y=None, height=dp(35), color=TEXT_COLOR))
            widget.size_hint_x = 0.6
            if isinstance(widget, BoxLayout) and "Groupe sanguin" in label_text:
                widget.height = dp(70) 
            form_layout.add_widget(widget)
        
        scroll_view.add_widget(form_layout) # 2. Ajoutez le GridLayout au ScrollView
        main_layout.add_widget(scroll_view) # 2. Ajoutez le ScrollView à votre layout principal
        
        button_layout = BoxLayout(spacing=dp(10), size_hint_y=0.1)
        self.save_button = Button(text="Enregistrer", on_press=self.save_patient_data, size_hint_y=None, height=dp(40), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR)
        self.cancel_button = Button(text="Annuler", on_press=self.go_back_to_home, size_hint_y=None, height=dp(40), background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR)
        
        button_layout.add_widget(self.save_button)
        button_layout.add_widget(self.cancel_button)
        
        main_layout.add_widget(button_layout)
        
        self.add_widget(main_layout)

    def on_enter(self, *args):
        if self.patient_id:
            self.title_label.text = "Modifier la fiche patient"
            self.load_patient_data()
        else:
            self.title_label.text = "Ajouter un nouveau patient"
            self.clear_form()
            self.field_widgets["id"].readonly = False

    def load_patient_data(self):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients = {}
            self.show_validation_popup("Erreur: Impossible de charger les données du patient.", "Erreur")
            return

        patient = patients.get(self.patient_id)
        if patient:
            self.field_widgets["id"].text = patient.get("id", "")
            self.field_widgets["nom_complet"].text = patient.get("nom_complet", "")
            self.field_widgets["age"].text = str(patient.get("age", ""))
            self.field_widgets["date_de_naissance"].text = patient.get("date_de_naissance", "")
            
            gender = patient.get("sexe", "")
            if gender in self.gender_buttons:
                self.gender_buttons[gender].state = 'down'
            
            blood_group = patient.get("groupe_sanguin", "")
            if blood_group in self.blood_group_buttons:
                self.blood_group_buttons[blood_group].state = 'down'
            
            self.field_widgets["adresse"].text = patient.get("adresse", "")
            self.field_widgets["numero_telephone"].text = patient.get("numero_telephone", "")
            self.field_widgets["email"].text = patient.get("email", "")
            self.field_widgets["personne_a_contacter"].text = patient.get("personne_a_contacter", "")
            self.field_widgets["numero_personne_a_contacter"].text = patient.get("numero_personne_a_contacter", "")
            self.field_widgets["antecedants_medicaux"].text = patient.get("antecedants_medicaux", "")
            
            self.field_widgets["id"].readonly = True
        else:
            self.show_validation_popup("Erreur: Patient non trouvé.", "Erreur")
            self.clear_form()

    def create_gender_buttons(self):
        gender_layout = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(35))
        self.gender_buttons = {
            'Homme': ToggleButton(text='Homme', group='sexe', state='normal', background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR),
            'Femme': ToggleButton(text='Femme', group='sexe', state='normal', background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR)
        }
        for btn in self.gender_buttons.values():
            gender_layout.add_widget(btn)
        return gender_layout

    def create_blood_group_buttons(self):
        blood_group_layout = GridLayout(cols=4, spacing=dp(5), size_hint_y=None)
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        self.blood_group_buttons = {}
        for group in blood_groups:
            btn = ToggleButton(
                text=group, 
                group='blood_group', 
                state='normal', 
                background_color=SECONDARY_COLOR, 
                color=BACKGROUND_COLOR
            )
            self.blood_group_buttons[group] = btn
            blood_group_layout.add_widget(btn)
        return blood_group_layout

    def get_selected_gender(self):
        for gender, btn in self.gender_buttons.items():
            if btn.state == 'down':
                return gender
        return None

    def get_selected_blood_group(self):
        for blood_group, btn in self.blood_group_buttons.items():
            if btn.state == 'down':
                return blood_group
        return None

    def save_patient_data(self, instance):
        patient_id = self.field_widgets["id"].text
        nom_complet = self.field_widgets["nom_complet"].text

        if not patient_id or not nom_complet:
            self.show_validation_popup("Veuillez remplir au moins l'ID du patient et le nom complet.", "Champs obligatoires")
            return
        
        new_patient_data = {
            "id": patient_id,
            "nom_complet": nom_complet,
            "age": self.field_widgets["age"].text,
            "date_de_naissance": self.field_widgets["date_de_naissance"].text,
            "sexe": self.get_selected_gender(),
            "groupe_sanguin": self.get_selected_blood_group(),
            "adresse": self.field_widgets["adresse"].text,
            "numero_telephone": self.field_widgets["numero_telephone"].text,
            "email": self.field_widgets["email"].text,
            "personne_a_contacter": self.field_widgets["personne_a_contacter"].text,
            "numero_personne_a_contacter": self.field_widgets["numero_personne_a_contacter"].text,
            "antecedants_medicaux": self.field_widgets["antecedants_medicaux"].text,
        }
        
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients = {}

        if patient_id in patients:
            existing_data = patients[patient_id]
            existing_data.update(new_patient_data)
            patients[patient_id] = existing_data
        else:
            patients[patient_id] = new_patient_data
        
        with open(PATIENT_DATA_FILE, "w") as f:
            json.dump(patients, f, indent=4)

        print(f"Patient {new_patient_data['nom_complet']} enregistré avec succès.")
        self.manager.current = 'patient_list'

    def clear_form(self):
        for field_key, widget in self.field_widgets.items():
            if isinstance(widget, TextInput):
                widget.text = ""
                widget.readonly = False
            elif isinstance(widget, BoxLayout):
                for btn in widget.children:
                    if isinstance(btn, ToggleButton):
                        btn.state = 'normal'
        self.patient_id = None
        self.title_label.text = "Ajouter un nouveau patient"

    def go_back_to_home(self, instance):
        self.clear_form()
        self.manager.current = 'home'

    def show_validation_popup(self, message, title="Information"):
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
        with popup.canvas.before:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=popup.pos, size=popup.size)
        popup.open()

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size