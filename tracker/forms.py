from django import forms
from .models import Medication, Dose

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        # Exclude the user field, it will be set in the view
        fields = ["name", "dosage", "instructions", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "instructions": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "dosage": forms.TextInput(attrs={"class": "form-control"}),
        }

class DoseForm(forms.ModelForm):
    # Override the __init__ method to filter the medication queryset
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None) # Get the user passed from the view
        super().__init__(*args, **kwargs)
        if user:
            # Filter the queryset for the medication field
            self.fields["medication"].queryset = Medication.objects.filter(user=user)

    class Meta:
        model = Dose
        # Exclude the user field, it will be set in the view
        fields = ["medication", "scheduled_time", "status", "notes"]
        widgets = {
            # Ensure Bootstrap classes are applied here too
            "medication": forms.Select(attrs={"class": "form-select"}),
            "scheduled_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

