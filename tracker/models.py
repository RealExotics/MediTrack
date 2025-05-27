from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # Import User model

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link to user
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g., 10mg, 1 tablet")
    instructions = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

    class Meta:
        # Optional: Ensure medication names are unique per user?
        # unique_together = [["user", "name"]]
        pass

class Dose(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("taken", "Prise"),
        ("missed", "Manquée"),
        ("skipped", "Sautée"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link to user
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name="doses")
    scheduled_time = models.DateTimeField()
    taken_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medication.name} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')} - {self.get_status_display()}"

    class Meta:
        ordering = ["scheduled_time"]

    @property
    def is_due_today(self):
        return self.scheduled_time.date() == timezone.now().date()

