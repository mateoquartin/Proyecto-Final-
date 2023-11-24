from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import taskForm
from .models import task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def home(request):

    return render(request, 'home.html')


def quien_soy(request):

    return render(request, 'quiensoy.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "Error": "Usuario ya existente"
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "Error": "Las contraseñas no coinciden"
        })


@login_required
@login_required
def tasks(request):
    query = request.GET.get('q')
    if query:
        task_list = task.objects.filter(
            Q(user=request.user) &
            (Q(titulo__icontains=query) | Q(description__icontains=query)) &
            Q(dia_completado__isnull=True)
        )
    else:
        task_list = task.objects.filter(
            user=request.user, dia_completado__isnull=True)
    return render(request, 'tasks.html', {'tasks': task_list, 'query': query})


@login_required
def tasks_completed(request):
    task_list = task.objects.filter(
        user=request.user, dia_completado__isnull=False).order_by('-dia_completado')
    return render(request, 'tasks.html', {'tasks': task_list})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {
            'form': taskForm
        })

    else:
        try:
            form = taskForm(request.POST)
            nueva_tarea = form.save(commit=False)
            nueva_tarea.user = request.user
            nueva_tarea.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': taskForm,
                'error': "Por favor proporciona un dato valido "
            })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        tarea_encontrada = get_object_or_404(task, pk=task_id)
        form = taskForm(instance=tarea_encontrada)
        return render(request, 'task_detail.html', {'task': tarea_encontrada, 'form': form})
    else:
        try:
            tarea_encontrada = get_object_or_404(task, pk=task_id)
            form = taskForm(request.POST, instance=tarea_encontrada)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': tarea_encontrada, 'form': form,
                                                        'error': "Error actualizando tarea"})


@login_required
def complete_task(request, task_id):
    tarea_encontrada = get_object_or_404(task, pk=task_id, user=request.user)
    if request.method == 'POST':
        tarea_encontrada.dia_completado = timezone.now()
        tarea_encontrada.save()
        return redirect('tasks')


@login_required
def delete_task(request, task_id):
    tarea_encontrada = get_object_or_404(task, pk=task_id, user=request.user)
    if request.method == 'POST':
        tarea_encontrada.delete()
        return redirect('tasks')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST
                            ['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': "Usuario o contraseña incorrectos"
            })
        else:
            login(request, user)
            return redirect("tasks")
