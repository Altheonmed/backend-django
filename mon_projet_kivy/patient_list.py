# patient_list.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
import json
import os
from fpdf import FPDF

from pythoncolor import PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR

PATIENT_DATA_FILE = "patients.json"
EXPORT_FILE = "patient_list.pdf"

class PatientListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'patient_list'
        
        # Application de la couleur de fond
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

        title_label = Label(text="Liste des patients", font_size='32sp', bold=True, size_hint_y=0.1, color=TEXT_COLOR)
        self.main_layout.add_widget(title_label)
        
        self.search_input = TextInput(
            hint_text="Rechercher par nom...",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=(1, 1, 1, 1),
            foreground_color=TEXT_COLOR
        )
        self.search_input.bind(text=self.load_patient_list)
        self.main_layout.add_widget(self.search_input)

        self.scrollview = ScrollView()
        self.patient_list_layout = GridLayout(cols=4, spacing=dp(15), size_hint_y=None,
                                              padding=[dp(10), 0, dp(10), 0])
        self.patient_list_layout.bind(minimum_height=self.patient_list_layout.setter('height'))
        self.scrollview.add_widget(self.patient_list_layout)
        self.main_layout.add_widget(self.scrollview)
        
        bottom_button_layout = BoxLayout(spacing=dp(10), size_hint_y=0.1)

        home_button = Button(
            text="Accueil",
            on_press=self.go_to_home,
            background_color=SECONDARY_COLOR,
            color=BACKGROUND_COLOR,
            border=(15, 15, 15, 15)
        )
        bottom_button_layout.add_widget(home_button)
        
        export_button = Button(
            text="Exporter PDF",
            on_press=self.export_patients_to_pdf,
            background_color=PRIMARY_COLOR,
            color=BACKGROUND_COLOR,
            border=(15, 15, 15, 15)
        )
        bottom_button_layout.add_widget(export_button)

        self.main_layout.add_widget(bottom_button_layout)

    def on_enter(self, *args):
        self.load_patient_list()

    def load_patient_list(self, *args):
        self.patient_list_layout.clear_widgets()
        
        self.patient_list_layout.add_widget(Label(text="ID", bold=True, size_hint_y=None, height=dp(40), color=TEXT_COLOR))
        self.patient_list_layout.add_widget(Label(text="Nom Complet", bold=True, size_hint_y=None, height=dp(40), color=TEXT_COLOR))
        self.patient_list_layout.add_widget(Label(text="Âge", bold=True, size_hint_y=None, height=dp(40), color=TEXT_COLOR))
        self.patient_list_layout.add_widget(Label(text="Actions", bold=True, size_hint_y=None, height=dp(40), color=TEXT_COLOR))

        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}
        
        patients = list(patients_data.values())

        search_text = self.search_input.text.lower()
        if search_text:
            patients = [
                p for p in patients
                if search_text in p.get('nom_complet', '').lower()
            ]

        patients.sort(key=lambda p: p.get('nom_complet', ''))
        
        if not patients:
            self.patient_list_layout.add_widget(Label(text="Aucun patient trouvé.", size_hint_x=4, color=TEXT_COLOR))
            return
        
        for patient in patients:
            patient_id = patient.get('id', 'N/A')
            self.patient_list_layout.add_widget(Label(text=patient_id, color=TEXT_COLOR))
            self.patient_list_layout.add_widget(Label(text=patient.get('nom_complet', 'N/A'), color=TEXT_COLOR))
            self.patient_list_layout.add_widget(Label(text=patient.get('age', 'N/A'), color=TEXT_COLOR))
            
            actions_layout = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(40))
            
            detail_button = Button(
                text='Détail',
                font_size='12sp',
                size_hint_x=None,
                width=dp(60),
                background_color=PRIMARY_COLOR,
                color=BACKGROUND_COLOR,
                border=(10, 10, 10, 10),
                on_press=lambda instance, id=patient_id: self.go_to_patient_detail(id)
            )
            actions_layout.add_widget(detail_button)

            edit_button = Button(
                text='Modifier',
                font_size='12sp',
                size_hint_x=None,
                width=dp(60),
                background_color=SECONDARY_COLOR,
                color=TEXT_COLOR,
                border=(10, 10, 10, 10),
                on_press=lambda instance, id=patient_id: self.go_to_patient_form_to_edit(id)
            )
            actions_layout.add_widget(edit_button)

            delete_button = Button(
                text='Supprimer',
                font_size='12sp',
                size_hint_x=None,
                width=dp(60),
                background_color=ACCENT_COLOR,
                color=BACKGROUND_COLOR,
                border=(10, 10, 10, 10),
                on_press=lambda instance, id=patient_id: self.show_delete_confirm_popup(id)
            )
            actions_layout.add_widget(delete_button)
            
            self.patient_list_layout.add_widget(actions_layout)

    def export_patients_to_pdf(self, instance):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        if not patients_data:
            self.show_export_message("Aucun patient à exporter.", "Erreur")
            return

        home_screen = self.manager.get_screen('home')
        doctor_name = home_screen.doctor_name if home_screen else "Dr. [Nom Inconnu]"

        patients = list(patients_data.values())
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt="Liste des patients", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Médecin : {doctor_name}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', size=10)
        pdf.cell(40, 10, "ID", border=1)
        pdf.cell(100, 10, "Nom Complet", border=1)
        pdf.cell(40, 10, "Âge", border=1, ln=True)

        pdf.set_font("Arial", size=10)
        for patient in patients:
            pdf.cell(40, 10, patient.get('id', 'N/A'), border=1)
            pdf.cell(100, 10, patient.get('nom_complet', 'N/A'), border=1)
            pdf.cell(40, 10, patient.get('age', 'N/A'), border=1, ln=True)
            
        pdf.output(EXPORT_FILE)
        
        self.show_export_message(f"La liste des patients a été exportée avec succès dans {os.path.abspath(EXPORT_FILE)}", "Exportation réussie", on_ok=lambda *args: self.open_file(EXPORT_FILE))

    def open_file(self, filepath):
        """Ouvre un fichier avec le programme par défaut du système."""
        if os.name == 'nt':
            os.startfile(filepath)
        elif os.uname().sysname == 'Darwin':
            os.system(f'open "{filepath}"')
        else:
            os.system(f'xdg-open "{filepath}"')

    def show_export_message(self, message, title, on_ok=None):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(
            text=message,
            color=TEXT_COLOR,
            font_size='18sp',
            halign='center'
        ))
        
        close_button = Button(
            text="OK", 
            background_color=SECONDARY_COLOR, 
            color=BACKGROUND_COLOR, 
            border=(10, 10, 10, 10)
        )
        content.add_widget(close_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            title_align='center',
            title_size='22sp',
            title_color=TEXT_COLOR,
            separator_color=TEXT_COLOR,
            # Paramètres pour un arrière-plan transparent
            background='transparent.png', 
            separator_height=0
        )

        if on_ok:
            close_button.bind(on_press=lambda *args: (on_ok(), popup.dismiss()))
        else:
            close_button.bind(on_press=popup.dismiss)
        
        popup.open()

    def show_delete_confirm_popup(self, patient_id):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(
            text=f"Êtes-vous sûr de vouloir supprimer le patient avec l'ID {patient_id} ?",
            color=TEXT_COLOR,
            font_size='18sp',
            halign='center'
        ))
        
        button_layout = BoxLayout(spacing=dp(10))
        
        yes_button = Button(
            text="Oui",
            background_color=ACCENT_COLOR,
            color=BACKGROUND_COLOR,
            border=(10, 10, 10, 10)
        )
        no_button = Button(
            text="Non",
            background_color=SECONDARY_COLOR,
            color=BACKGROUND_COLOR,
            border=(10, 10, 10, 10)
        )
        
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        content.add_widget(button_layout)
        
        popup = Popup(
            title="Confirmation de suppression",
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            title_align='center',
            title_size='22sp',
            title_color=TEXT_COLOR,
            separator_color=TEXT_COLOR,
            # Paramètres pour un arrière-plan transparent
            background='transparent.png', 
            separator_height=0
        )

        yes_button.bind(on_press=lambda *args: self.delete_patient(patient_id, popup))
        no_button.bind(on_press=popup.dismiss)
        
        popup.open()

    def delete_patient(self, patient_id, popup):
        popup.dismiss()

        if not patient_id:
            print("Erreur: ID du patient manquant.")
            return

        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}
        
        if patient_id in patients_data:
            del patients_data[patient_id]
            
            with open(PATIENT_DATA_FILE, "w") as f:
                json.dump(patients_data, f, indent=4)
            
            print(f"Patient {patient_id} supprimé avec succès.")
        
        self.load_patient_list()

    def go_to_patient_detail(self, patient_id):
        home_screen = self.manager.get_screen('home')
        doctor_name = home_screen.doctor_name if home_screen else None
        
        detail_screen = self.manager.get_screen('patient_detail')
        
        detail_screen.patient_id = patient_id
        detail_screen.doctor_name = doctor_name
        
        self.manager.current = 'patient_detail'

    def go_to_patient_form_to_edit(self, patient_id):
        self.manager.get_screen('patient_form').patient_id = patient_id
        self.manager.current = 'patient_form'

    def go_to_home(self, instance):
        self.manager.current = 'home'

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size