# patient_detail.py
dfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import os
import subprocess
import platform

from pythoncolor import PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR, ACCENT_COLOR

PATIENT_DATA_FILE = "patients.json"
USERS_FILE = "users.json"


def load_users():
    """Charge les données des utilisateurs depuis un fichier JSON."""
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class AutoHeightLabel(Label):
    """
    Un Label qui ajuste automatiquement sa hauteur en fonction de son contenu.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(texture_size=self.on_texture_size)
        self.bind(width=self.on_width)
        self.size_hint_y = None
        self.text_size = (self.width, None)

    def on_texture_size(self, instance, value):
        # La correction est ici : on prend uniquement la hauteur (index 1)
        self.height = value[1]

    def on_width(self, instance, value):
        self.text_size = (self.width, None)


class PatientDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'patient_detail'
        self.patient_id = None
        self.doctor_name = None

        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        self.title_label = Label(text="Détails du patient", font_size='32sp', bold=True, size_hint_y=0.1, color=TEXT_COLOR)
        self.main_layout.add_widget(self.title_label)

        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.scroll_view.add_widget(self.content_layout)
        self.main_layout.add_widget(self.scroll_view)

        self.detail_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        self.detail_layout.bind(minimum_height=self.detail_layout.setter('height'))
        self.content_layout.add_widget(self.detail_layout)

        self.add_consultation_button = Button(
            text="Ajouter une consultation",
            size_hint_y=None,
            height=dp(40),
            background_color=PRIMARY_COLOR,
            color=BACKGROUND_COLOR,
            border=(15, 15, 15, 15),
            on_press=self.go_to_consultation_form
        )
        self.content_layout.add_widget(self.add_consultation_button)

        self.add_act_button = Button(
            text="Ajouter un acte médical",
            size_hint_y=None,
            height=dp(40),
            background_color=SECONDARY_COLOR,
            color=BACKGROUND_COLOR,
            border=(15, 15, 15, 15),
            on_press=self.go_to_medical_act_form
        )
        self.content_layout.add_widget(self.add_act_button)

        self.consultation_list_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.consultation_list_layout.bind(minimum_height=self.consultation_list_layout.setter('height'))
        self.content_layout.add_widget(self.consultation_list_layout)

        self.medical_act_list_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.medical_act_list_layout.bind(minimum_height=self.medical_act_list_layout.setter('height'))
        self.content_layout.add_widget(self.medical_act_list_layout)

        button_layout = BoxLayout(spacing=dp(10), size_hint_y=0.1)
        export_button = Button(text="Exporter vers PDF", on_press=self.export_to_pdf, background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR, border=(15, 15, 15, 15))
        back_button = Button(text="Retour à la liste", on_press=self.go_to_patient_list, background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR, border=(15, 15, 15, 15))
        button_layout.add_widget(export_button)
        button_layout.add_widget(back_button)
        self.main_layout.add_widget(button_layout)

        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        if self.patient_id:
            self.display_patient_details()
            self.display_all_consultations()
            self.display_all_medical_acts()

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
import json

from reportlab.p
    def display_patient_details(self):
        self.detail_layout.clear_widgets()
        self.consultation_list_layout.clear_widgets()
        self.medical_act_list_layout.clear_widgets()

        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        patient = patients_data.get(self.patient_id)
        if patient:
            self.title_label.text = f"Détails du patient : {patient.get('nom_complet', '')}"

            grid_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
            grid_layout.bind(minimum_height=grid_layout.setter('height'))

            for key, value in patient.items():
                if key not in ["consultations", "antecedants_medicaux", "actes_medicaux"]:
                    display_key = key.replace('_', ' ').capitalize()
                    grid_layout.add_widget(Label(text=f"[b]{display_key}[/b]:", markup=True, halign='left', valign='top', size_hint_y=None, height=dp(25), color=TEXT_COLOR))
                    grid_layout.add_widget(Label(text=str(value), halign='left', valign='top', size_hint_y=None, height=dp(25), color=TEXT_COLOR))

            self.detail_layout.add_widget(grid_layout)

            if "antecedants_medicaux" in patient:
                self.detail_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
                self.detail_layout.add_widget(Label(text="Antécédents médicaux:", bold=True, halign='left', valign='top', size_hint_y=None, height=dp(25), color=TEXT_COLOR))
                self.detail_layout.add_widget(
                    AutoHeightLabel(
                        text=patient["antecedants_medicaux"],
                        halign='left',
                        valign='top',
                        markup=True,
                        width=self.content_layout.width - dp(40),
                        color=TEXT_COLOR
                    )
                )

        else:
            self.title_label.text = "Patient non trouvé"
            self.detail_layout.add_widget(Label(text="Les détails de ce patient n'ont pas pu être chargés.", color=TEXT_COLOR))

    def display_all_consultations(self):
        self.consultation_list_layout.clear_widgets()

        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        patient = patients_data.get(self.patient_id)
        if patient and "consultations" in patient and patient["consultations"]:
            self.consultation_list_layout.add_widget(Label(text="Historique des consultations", bold=True, font_size='18sp', halign='left',
                                                            size_hint_y=None, height=dp(30), color=TEXT_COLOR))
            for consultation in patient["consultations"]:
                cons_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
                cons_layout.bind(minimum_height=cons_layout.setter('height'))
                with cons_layout.canvas.before:
                    Color(1, 1, 1, 1)
                    cons_layout_rect = Rectangle(pos=cons_layout.pos, size=cons_layout.size)
                cons_layout.bind(pos=lambda instance, value: setattr(cons_layout_rect, 'pos', value),
                                 size=lambda instance, value: setattr(cons_layout_rect, 'size', value))

                header_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(40))
                date_label = Label(text=f"Consultation du {consultation.get('date_et_heure', 'N/A')}", bold=True, font_size='16sp', halign='left', size_hint_x=0.6, color=TEXT_COLOR)
                header_layout.add_widget(date_label)

                modify_button = Button(text="Modifier", size_hint_x=0.2, size_hint_y=None, height=dp(40),
                                         background_color=SECONDARY_COLOR, color=TEXT_COLOR, border=(10, 10, 10, 10),
                                         on_press=lambda instance, cons_id=consultation['id']: self.go_to_consultation_form_to_edit(cons_id))
                header_layout.add_widget(modify_button)

                delete_button = Button(text="Supprimer", size_hint_x=0.2, size_hint_y=None, height=dp(40),
                                         background_color=ACCENT_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10),
                                         on_press=lambda instance, cons_id=consultation['id']: self.show_delete_consultation_popup(cons_id))
                header_layout.add_widget(delete_button)

                cons_layout.add_widget(header_layout)

                details_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
                details_grid.bind(minimum_height=details_grid.setter('height'))
                for key, value in consultation.items():
                    if key not in ["id", "date_et_heure"]:
                        display_key = key.replace('_', ' ').capitalize()
                        details_grid.add_widget(Label(text=f"{display_key}:", bold=True, halign='left', valign='top', size_hint_y=None, height=dp(25), color=TEXT_COLOR))
                        details_grid.add_widget(AutoHeightLabel(text=str(value), halign='left', valign='top', markup=True, width=self.content_layout.width - dp(60), color=TEXT_COLOR))

                cons_layout.add_widget(details_grid)
                self.consultation_list_layout.add_widget(cons_layout)
                self.consultation_list_layout.add_widget(Label(size_hint_y=None, height=dp(10)))
        else:
            self.consultation_list_layout.add_widget(Label(text="Historique des consultations", bold=True, font_size='18sp', halign='left',
                                                            size_hint_y=None, height=dp(30), color=TEXT_COLOR))
            self.consultation_list_layout.add_widget(Label(text="Aucune consultation enregistrée.", halign='left', size_hint_y=None, height=dp(25), color=TEXT_COLOR))


    def go_to_consultation_form(self, instance=None):
        consultation_form_screen = self.manager.get_screen('consultation_form')
        consultation_form_screen.patient_id = self.patient_id
        consultation_form_screen.consultation_id = None
        self.manager.current = 'consultation_form'

    def go_to_consultation_form_to_edit(self, consultation_id):
        consultation_form_screen = self.manager.get_screen('consultation_form')
        consultation_form_screen.patient_id = self.patient_id
        consultation_form_screen.consultation_id = consultation_id
        self.manager.current = 'consultation_form'

    def go_to_patient_list(self, instance):
        self.manager.current = 'patient_list'

    def show_delete_consultation_popup(self, consultation_id):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(text="Êtes-vous sûr de vouloir supprimer cette consultation ?",
                                 color=TEXT_COLOR, font_size='18sp', halign='center'))

        button_layout = BoxLayout(spacing=dp(10))
        yes_button = Button(text="Oui", background_color=ACCENT_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10))
        no_button = Button(text="Non", background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10))
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        content.add_widget(button_layout)

        popup = Popup(title="Confirmation de suppression",
                      content=content,
                      size_hint=(0.7, 0.4),
                      auto_dismiss=False,
                      title_align='center',
                      title_size='22sp',
                      title_color=TEXT_COLOR,
                      separator_color=TEXT_COLOR,
                      background='transparent.png',
                      separator_height=0)

        yes_button.bind(on_press=lambda *args: self.delete_consultation(consultation_id, popup))
        no_button.bind(on_press=popup.dismiss)

        popup.open()

    def delete_consultation(self, consultation_id, popup):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        if self.patient_id in patients_data and "consultations" in patients_data.get(self.patient_id, {}):
            patients_data.get(self.patient_id)["consultations"] = [
                c for c in patients_data.get(self.patient_id, {}).get("consultations", []) if c.get("id") != consultation_id
            ]

            with open(PATIENT_DATA_FILE, "w") as f:
                json.dump(patients_data, f, indent=4)

            print(f"Consultation {consultation_id} supprimée avec succès.")
            self.display_all_consultations()

        popup.dismiss()

    def go_to_medical_act_form(self, instance=None):
        medical_act_form_screen = self.manager.get_screen('medical_act_form')
        medical_act_form_screen.patient_id = self.patient_id
        medical_act_form_screen.act_id = None
        self.manager.current = 'medical_act_form'

    def go_to_medical_act_form_to_edit(self, act_id):
        medical_act_form_screen = self.manager.get_screen('medical_act_form')
        medical_act_form_screen.patient_id = self.patient_id
        medical_act_form_screen.act_id = act_id
        self.manager.current = 'medical_act_form'

    def show_delete_medical_act_popup(self, act_id):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(text="Êtes-vous sûr de vouloir supprimer cet acte médical ?",
                                 color=TEXT_COLOR, font_size='18sp', halign='center'))

        button_layout = BoxLayout(spacing=dp(10))
        yes_button = Button(text="Oui", background_color=ACCENT_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10))
        no_button = Button(text="Non", background_color=SECONDARY_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10))
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        content.add_widget(button_layout)

        popup = Popup(title="Confirmation de suppression",
                      content=content,
                      size_hint=(0.7, 0.4),
                      auto_dismiss=False,
                      title_align='center',
                      title_size='22sp',
                      title_color=TEXT_COLOR,
                      separator_color=TEXT_COLOR,
                      background='transparent.png',
                      separator_height=0)

        yes_button.bind(on_press=lambda *args: self.delete_medical_act(act_id, popup))
        no_button.bind(on_press=popup.dismiss)

        popup.open()

    def delete_medical_act(self, act_id, popup):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        if self.patient_id in patients_data and "actes_medicaux" in patients_data.get(self.patient_id, {}):
            patients_data.get(self.patient_id)["actes_medicaux"] = [
                act for act in patients_data.get(self.patient_id, {}).get("actes_medicaux", []) if act.get("id") != act_id
            ]

            with open(PATIENT_DATA_FILE, "w") as f:
                json.dump(patients_data, f, indent=4)

            print(f"Acte médical {act_id} supprimé avec succès.")
            self.display_all_medical_acts()

        popup.dismiss()

    def display_all_medical_acts(self):
        self.medical_act_list_layout.clear_widgets()

        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            patients_data = {}

        patient = patients_data.get(self.patient_id)
        if patient and "actes_medicaux" in patient and patient["actes_medicaux"]:
            self.medical_act_list_layout.add_widget(Label(text="Historique des actes médicaux", bold=True, font_size='18sp', halign='left',
                                                            size_hint_y=None, height=dp(30), color=TEXT_COLOR))
            for act in patient["actes_medicaux"]:
                act_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
                act_layout.bind(minimum_height=act_layout.setter('height'))
                with act_layout.canvas.before:
                    Color(1, 1, 1, 1)
                    act_layout_rect = Rectangle(pos=act_layout.pos, size=act_layout.size)
                act_layout.bind(pos=lambda instance, value: setattr(act_layout_rect, 'pos', value),
                                 size=lambda instance, value: setattr(act_layout_rect, 'size', value))

                header_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(40))
                date_label = Label(text=f"Acte du {act.get('date_et_heure', 'N/A')}", bold=True, font_size='16sp', halign='left', size_hint_x=0.6, color=TEXT_COLOR)
                header_layout.add_widget(date_label)

                modify_button = Button(text="Modifier", size_hint_x=0.2, size_hint_y=None, height=dp(40),
                                         background_color=SECONDARY_COLOR, color=TEXT_COLOR, border=(10, 10, 10, 10),
                                         on_press=lambda instance, act_id=act['id']: self.go_to_medical_act_form_to_edit(act_id))
                header_layout.add_widget(modify_button)

                delete_button = Button(text="Supprimer", size_hint_x=0.2, size_hint_y=None, height=dp(40),
                                         background_color=ACCENT_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10),
                                         on_press=lambda instance, act_id=act['id']: self.show_delete_medical_act_popup(act_id))
                header_layout.add_widget(delete_button)

                act_layout.add_widget(header_layout)

                details_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
                details_grid.bind(minimum_height=details_grid.setter('height'))
                for key, value in act.items():
                    if key not in ["id", "date_et_heure"]:
                        display_key = key.replace('_', ' ').capitalize()
                        details_grid.add_widget(Label(text=f"{display_key}:", bold=True, halign='left', valign='top', size_hint_y=None, height=dp(25), color=TEXT_COLOR))
                        details_grid.add_widget(AutoHeightLabel(text=str(value), halign='left', valign='top', markup=True, width=self.content_layout.width - dp(60), color=TEXT_COLOR))

                act_layout.add_widget(details_grid)
                self.medical_act_list_layout.add_widget(act_layout)
                self.medical_act_list_layout.add_widget(Label(size_hint_y=None, height=dp(10)))
        else:
            self.medical_act_list_layout.add_widget(Label(text="Historique des actes médicaux", bold=True, font_size='18sp', halign='left',
                                                            size_hint_y=None, height=dp(30), color=TEXT_COLOR))
            self.medical_act_list_layout.add_widget(Label(text="Aucun acte médical enregistré.", halign='left', size_hint_y=None, height=dp(25), color=TEXT_COLOR))

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size

    def export_to_pdf(self, instance):
        try:
            with open(PATIENT_DATA_FILE, "r") as f:
                patients_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.show_export_popup("Erreur", "Fichier de données des patients non trouvé.")
            return

        patient = patients_data.get(self.patient_id)
        if not patient:
            self.show_export_popup("Erreur", "Détails du patient non trouvés.")
            return

        file_name = f"fiche_patient_{patient.get('id', 'inconnu')}.pdf"

        doc = SimpleDocTemplate(file_name, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CustomBold', fontName='Helvetica-Bold', fontSize=12, leading=18, textColor=colors.HexColor("#333333")))
        styles.add(ParagraphStyle(name='CustomNormal', fontName='Helvetica', fontSize=12, leading=18, textColor=colors.HexColor("#333333")))
        styles.add(ParagraphStyle(name='SubHeader', fontName='Helvetica-Bold', fontSize=14, leading=18, spaceAfter=12, textColor=colors.HexColor("#333333")))
        styles.add(ParagraphStyle(name='Multiline', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=14, spaceAfter=12, textColor=colors.HexColor("#333333")))

        if self.doctor_name:
            users_data = load_users()
            doctor_specialty = users_data.get(self.doctor_name, {}).get('specialty', 'Spécialité non définie')
            story.append(Paragraph(f"<b>{self.doctor_name}</b>", styles['h2']))
            story.append(Paragraph(f"<b>{doctor_specialty}</b>", styles['Normal']))
            story.append(Spacer(1, 20))

        style_title = styles['h1']
        style_title.alignment = TA_CENTER
        story.append(Paragraph(f"Fiche Patient : {patient.get('nom_complet', '')}", style_title))
        story.append(Spacer(1, 30))

        story.append(Paragraph("<b>Informations du patient</b>", styles['h2']))
        for key, value in patient.items():
            if key not in ["consultations", "actes_medicaux"]:
                display_key = key.replace('_', ' ').capitalize()
                story.append(Paragraph(f"<b>{display_key}:</b> {str(value)}", styles['CustomNormal']))

        story.append(Spacer(1, 30))
        story.append(Paragraph("<b>Historique des consultations</b>", styles['h2']))
        if "consultations" in patient and patient["consultations"]:
            for consultation in patient["consultations"]:
                story.append(Spacer(1, 15))
                story.append(Paragraph(f"<b>Consultation du {consultation.get('date_et_heure', 'N/A')}</b>", styles['SubHeader']))

                for key, value in consultation.items():
                    if key not in ["id", "date_et_heure"]:
                        display_key = key.replace('_', ' ').capitalize()
                        text_to_display = str(value).replace('\n', '<br/>')
                        story.append(Paragraph(f"<b>{display_key}:</b> {text_to_display}", styles['Multiline']))
        else:
            story.append(Paragraph("Aucune consultation enregistrée.", styles['Normal']))

        story.append(Spacer(1, 30))
        story.append(Paragraph("<b>Historique des actes médicaux</b>", styles['h2']))
        if "actes_medicaux" in patient and patient["actes_medicaux"]:
            for act in patient["actes_medicaux"]:
                story.append(Spacer(1, 15))
                story.append(Paragraph(f"<b>Acte du {act.get('date_et_heure', 'N/A')}</b>", styles['SubHeader']))
                for key, value in act.items():
                    if key not in ["id", "date_et_heure"]:
                        display_key = key.replace('_', ' ').capitalize()
                        text_to_display = str(value).replace('\n', '<br/>')
                        story.append(Paragraph(f"<b>{display_key}:</b> {text_to_display}", styles['Multiline']))
        else:
            story.append(Paragraph("Aucun acte médical enregistré.", styles['Normal']))

        doc.build(story)
        self.open_pdf_file(file_name)
        self.show_export_popup("Succès", f"Fiche patient exportée avec succès vers {file_name} et ouverte.")

    def open_pdf_file(self, filename):
        if platform.system() == 'Windows':
            os.startfile(filename)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', filename])
        else:
            subprocess.call(['xdg-open', filename])

    def show_export_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(text=message, color=TEXT_COLOR, font_size='18sp', halign='center'))

        def dismiss_popup(instance):
            popup.dismiss()

        close_button = Button(text="OK", size_hint_y=None, height=dp(40), background_color=PRIMARY_COLOR, color=BACKGROUND_COLOR, border=(10, 10, 10, 10))
        close_button.bind(on_press=dismiss_popup)
        content.add_widget(close_button)

        popup = Popup(title=title,
                      content=content,
                      size_hint=(0.8, 0.4),
                      auto_dismiss=False,
                      title_align='center',
                      title_size='22sp',
                      title_color=TEXT_COLOR,
                      separator_color=TEXT_COLOR,
                      background='transparent.png',
                      separator_height=0)
        popup.open()