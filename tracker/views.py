from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Medication, Dose
from .forms import MedicationForm, DoseForm
import datetime
from django.db.models import Count, Q
from django.contrib import messages
from collections import defaultdict
from django.contrib.auth.decorators import login_required # Import login_required
from django.contrib.auth.forms import UserCreationForm # Import UserCreationForm
from django.contrib.auth import login # Import login function
from datetime import timedelta

# --- Authentication Views ---

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately after signup
            messages.success(request, "Inscription réussie ! Vous êtes maintenant connecté.")
            return redirect('dashboard') # Redirect to dashboard after signup
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Note: Login and Logout views will use Django's built-in views via urls.py

# --- Helper Function ---

# This function is called by views that are already protected by @login_required
def update_missed_doses(user):
    """Helper function to mark past pending doses as missed for a specific user."""
    now = timezone.now()
    missed_count = Dose.objects.filter(user=user, scheduled_time__lt=now, status='pending').update(status='missed')
    # print(f"Marked {missed_count} doses as missed for user {user.username}.") # For debugging

# --- Main Application Views (Updated for Auth) ---

@login_required
def dashboard(request):
    update_missed_doses(request.user)
    today = timezone.now().date()
    
    # Créer une liste des 3 prochains jours
    dates = [today + datetime.timedelta(days=i) for i in range(3)]
    
    all_doses_by_day = {}
    
    for current_date in dates:
        start_of_day = timezone.make_aware(datetime.datetime.combine(current_date, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(current_date, datetime.time.max))

        # Filtrer les doses pour le jour courant
        doses_day_qs = Dose.objects.filter(
            user=request.user, 
            scheduled_time__range=(start_of_day, end_of_day)
        ).order_by('scheduled_time').select_related('medication')

        doses_by_time = defaultdict(list)
        for dose in doses_day_qs:
            hour = dose.scheduled_time.hour
            if 5 <= hour < 11:
                time_slot = "Matin (5h-11h)"
            elif 11 <= hour < 14:
                time_slot = "Midi (11h-14h)"
            elif 14 <= hour < 20:
                time_slot = "Soir (14h-20h)"
            else:
                time_slot = "Coucher (20h-5h)"
            doses_by_time[time_slot].append(dose)

        # Formater la date en français
        date_str = current_date.strftime("%A %d %B %Y").capitalize()
        all_doses_by_day[date_str] = dict(doses_by_time)

    context = {
        'all_doses_by_day': all_doses_by_day,
        'time_slots': ["Matin (5h-11h)", "Midi (11h-14h)", "Soir (14h-20h)", "Coucher (20h-5h)"],
        'today_str': today.strftime("%A %d %B %Y").capitalize()
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False) # Don't save yet
            medication.user = request.user # Assign the logged-in user
            medication.save()
            messages.success(request, f"Médicament '{medication.name}' ajouté avec succès.")
            return redirect('dashboard')
        else:
             messages.error(request, "Erreur lors de l'ajout du médicament. Veuillez vérifier le formulaire.")
    else:
        form = MedicationForm()
    # Ensure the form only shows medications for the current user if needed (not applicable here)
    return render(request, 'tracker/add_medication.html', {'form': form})

@login_required
def add_dose(request):
    # Filter medication choices to only show those belonging to the current user
    medication_queryset = Medication.objects.filter(user=request.user)

    if request.method == 'POST':
        form = DoseForm(request.POST, user=request.user) # Pass user to form if needed for validation
        if form.is_valid():
            dose = form.save(commit=False)
            dose.user = request.user # Assign the logged-in user
            # Ensure the selected medication belongs to the user (already handled by form queryset)
            dose.save()
            messages.success(request, "Prise enregistrée avec succès.")
            return redirect('history')
        else:
             messages.error(request, "Erreur lors de l'enregistrement de la prise. Veuillez vérifier le formulaire.")
    else:
        form = DoseForm(user=request.user) # Pass user to form for initial queryset filtering
        med_id = request.GET.get('medication_id')
        if med_id:
            try:
                # Ensure the pre-filled medication belongs to the user
                initial_med = Medication.objects.get(pk=med_id, user=request.user)
                form.initial['medication'] = initial_med
            except Medication.DoesNotExist:
                messages.warning(request, "Médicament initial non trouvé ou non autorisé.")

    return render(request, 'tracker/add_dose.html', {'form': form})

@login_required
def update_dose_status(request, dose_id, status):
    # Ensure the dose belongs to the logged-in user
    dose = get_object_or_404(Dose, pk=dose_id, user=request.user)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        if status in ['taken', 'skipped']:
            dose.status = status
            if status == 'taken':
                dose.taken_time = timezone.now()
            else:
                dose.taken_time = None
            dose.save()
            if is_ajax:
                return JsonResponse({'status': 'success', 'new_status': dose.get_status_display(), 'taken_time_str': dose.taken_time.strftime("%H:%M") if dose.taken_time else ''})
            else:
                messages.success(request, f"Statut de la prise mis à jour : {dose.get_status_display()}.")
                return redirect('dashboard')
        else:
            # Handle invalid status
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
            else:
                messages.error(request, "Statut invalide.")
                return redirect('dashboard')
    else:
        # Reject GET requests for state changes
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)
        else:
            messages.error(request, "Méthode non autorisée.")
            return redirect('dashboard')

@login_required
def history(request):
    update_missed_doses(request.user)
    # Filter history for the logged-in user
    doses_query = Dose.objects.filter(user=request.user).select_related('medication').order_by('-scheduled_time')
    # Filter medication dropdown for the logged-in user
    medications = Medication.objects.filter(user=request.user).order_by('name')

    med_filter = request.GET.get('medication')
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')

    if med_filter:
        doses_query = doses_query.filter(medication_id=med_filter)
    if status_filter:
        doses_query = doses_query.filter(status=status_filter)
    if date_filter:
        try:
            filter_date = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
            doses_query = doses_query.filter(scheduled_time__date=filter_date)
        except ValueError:
            messages.warning(request, "Format de date invalide pour le filtre.")

    context = {
        'doses': doses_query,
        'medications': medications,
    }
    return render(request, 'tracker/history.html', context)

@login_required
def delete_dose(request, dose_id):
    # Ensure the dose belongs to the logged-in user
    dose = get_object_or_404(Dose, pk=dose_id, user=request.user)
    if request.method == 'POST':
        dose.delete()
        messages.success(request, "Prise supprimée de l'historique.")
        return redirect('history')
    else:
        messages.error(request, "Méthode non autorisée pour la suppression.")
        return redirect('history')

@login_required
def statistics(request):
    update_missed_doses(request.user)
    today = timezone.now().date()
    
    # Récupérer toutes les doses de l'utilisateur
    doses_qs = Dose.objects.filter(user=request.user)
    
    # Calculer les statistiques
    total_doses = doses_qs.count()
    taken_doses = doses_qs.filter(status='taken').count()
    missed_doses = doses_qs.filter(status='missed').count()
    skipped_doses = doses_qs.filter(status='skipped').count()
    pending_doses = doses_qs.filter(status='pending').count()

    # Calcul des pourcentages
    adherence_percentage = (taken_doses / total_doses * 100) if total_doses > 0 else 0
    taken_percentage = (taken_doses / total_doses * 100) if total_doses > 0 else 0
    missed_percentage = (missed_doses / total_doses * 100) if total_doses > 0 else 0
    skipped_percentage = (skipped_doses / total_doses * 100) if total_doses > 0 else 0

    # Préparation des données pour le graphique hebdomadaire
    weekly_trend = {'labels': [], 'taken': [], 'missed': [], 'skipped': []}
    
    # Trouver la première et la dernière date des doses
    if doses_qs.exists():
        first_dose = doses_qs.order_by('scheduled_time').first().scheduled_time.date()
        last_dose = doses_qs.order_by('-scheduled_time').first().scheduled_time.date()
        
        # Créer une liste de semaines entre la première et la dernière dose
        current_week_start = first_dose - timedelta(days=first_dose.weekday())
        last_week_end = last_dose + timedelta(days=(6 - last_dose.weekday()))
        
        while current_week_start <= last_week_end:
            week_end = current_week_start + timedelta(days=6)
            week_doses = doses_qs.filter(scheduled_time__date__range=[current_week_start, week_end])
            
            label = f"Sem {current_week_start.strftime('%d/%m')}"
            weekly_trend['labels'].append(label)
            weekly_trend['taken'].append(week_doses.filter(status='taken').count())
            weekly_trend['missed'].append(week_doses.filter(status='missed').count())
            weekly_trend['skipped'].append(week_doses.filter(status='skipped').count())
            
            current_week_start += timedelta(days=7)

    context = {
        'adherence_percentage': round(adherence_percentage, 1),
        'total_doses': total_doses,
        'taken_doses': taken_doses,
        'missed_doses': missed_doses,
        'skipped_doses': skipped_doses,
        'taken_percentage': round(taken_percentage, 1),
        'missed_percentage': round(missed_percentage, 1),
        'skipped_percentage': round(skipped_percentage, 1),
        'weekly_trend': weekly_trend,
    }
    return render(request, 'tracker/statistics.html', context)

@login_required
def settings(request):
    # Settings could be stored in a UserProfile model later, using session for now
    email_notifications_enabled = request.session.get(f'user_{request.user.id}_email_notifications', False)

    if request.method == 'POST':
        new_setting = request.POST.get('email_notifications') == 'on'
        request.session[f'user_{request.user.id}_email_notifications'] = new_setting
        email_notifications_enabled = new_setting
        messages.success(request, "Paramètres enregistrés.")

    context = {
        'email_notifications_enabled': email_notifications_enabled
    }
    return render(request, 'tracker/settings.html', context)

@login_required
def medications(request):
    """View to display all medications for the logged-in user."""
    medications = Medication.objects.filter(user=request.user).order_by('name')
    return render(request, 'tracker/medications.html', {'medications': medications})

@login_required
def edit_medication(request, medication_id):
    """View to edit an existing medication."""
    medication = get_object_or_404(Medication, pk=medication_id, user=request.user)
    
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            messages.success(request, f"Médicament '{medication.name}' modifié avec succès.")
            return redirect('medications')
        else:
            messages.error(request, "Erreur lors de la modification du médicament. Veuillez vérifier le formulaire.")
    else:
        form = MedicationForm(instance=medication)
    
    return render(request, 'tracker/edit_medication.html', {
        'form': form,
        'medication': medication
    })

@login_required
def delete_medication(request, medication_id):
    """View to delete a medication."""
    medication = get_object_or_404(Medication, pk=medication_id, user=request.user)
    
    if request.method == 'POST':
        name = medication.name
        medication.delete()
        messages.success(request, f"Médicament '{name}' supprimé avec succès.")
        return redirect('medications')
    
    return render(request, 'tracker/delete_medication.html', {
        'medication': medication
    })

