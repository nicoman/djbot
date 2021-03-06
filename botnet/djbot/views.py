import django_rq
import ast
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from botnet.djbot.models import Computadora, Aula
from django.shortcuts import render, redirect
from botnet.djbot.forms import FormularioAulas, FormularioListaTareas
from botnet.djbot.forms import FormularioResultados
from botnet.djbot.funciones import *
from redis_cache import get_redis_connection


@login_required
def indice(request):
    formulario_aula = FormularioAulas(request.POST or None)
    formulario_tareas = FormularioListaTareas(request.POST or None)
    contexto = {'formulario_aula': formulario_aula,
        'formulario_tarea': formulario_tareas}
    if formulario_aula.is_valid() and formulario_tareas.is_valid():
        valores = dict(formulario_tareas.cleaned_data.items() +
                formulario_aula.cleaned_data.items())
        salas = {}
        for each in valores['aulas']:
            salas[each] = []
            for compu in Computadora.objects.filter(aula=each):
                salas[each].append(compu.ip)
        try:
            django_rq.enqueue(ejecutar_tareas, tareas=valores['tareas'],
                              salas=salas)
        except:
            return HttpResponse("<h1>Estas ejecutando redis??</h1>")
        return redirect('mostrar_resultados')
    return render(request, 'botnet/index.html', contexto)


@login_required
def prender(request, lista_de_salas):
    pass
    salas = lista_de_salas.split(',')
    for nombreAula in salas:
        computadoras = Computadora.objects.filter(aula=nombreAula)
        unAula = Aula.objects.get(nombre=nombreAula)
        compus = []
        for each in computadoras.values():
            compus = each['nombre']
            unAula.maquina_intermediaria
            fabfile.ejecutar('etherwake -i ' + unAula.interfaz + ' ' +
            each['mac'], [unAula.maquina_intermediaria])
    return HttpResponse(compus)


@login_required
def mostrar_resultados(request):
    form_aula = FormularioAulas(request.POST or None)
    form_resultados = FormularioResultados(request.POST or None)
    compus = None
    if form_aula.is_valid() and form_resultados.is_valid():
        resultados = dict(form_resultados.cleaned_data.items())
        valores = dict(form_aula.cleaned_data.items())
        if resultados['mostrar'] == 'todos':
            compus = mostrar_aula(valores['aulas'])
        if resultados['mostrar'] == 'uno':
            compus = mostrar_computadora(valores['aulas'], resultados['ip'])
    cache = get_redis_connection('default')
    apagadas = cache.get('apagadas')
    if apagadas:
        apagadas = ast.literal_eval(apagadas)
    else:
        apagadas = ''
    return render(request, 'botnet/mostrar_resultados.html',
            {'formulario': FormularioAulas(), 'computadoras': compus,
            'mostrar': FormularioResultados(), 'apagadas': apagadas})
