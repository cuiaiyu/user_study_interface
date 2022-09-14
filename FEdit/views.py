from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Answer, Question, Choice
from django.http import HttpResponse
from django.template import loader
import random
from datetime import datetime

MAX_TEST_PER_USER = 20

MAX_TEST_PER_USER_VTION = 20
N_WARM_UP = 2

class IndexView(generic.ListView):
    template_name = 'FEdit/index.html'
    context_object_name = 'latest_question_list'
    def get_queryset(self):
        return Question.objects.order_by('id')

class IndexVitonView(generic.ListView):
    template_name = 'FEdit/index.html'
    context_object_name = 'latest_question_list'
    def get_queryset(self):
        return Question.objects.order_by('id')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'FEdit/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'FEdit/results.html'

def results(request):
    return render(request, 'FEdit/results.html', {})

def vote(request, question_id):
    # question_id = Question.objects.filter(question_cata='posetrans').order_by("?")[0]
    question = get_object_or_404(Question, pk=question_id)
    # import pdb; pdb.set_trace()
    time_id = datetime.now() if not 'time_id' in request.POST else request.POST['time_id']
    count = 0 if not 'count' in request.POST else request.POST['count']
    total_count = MAX_TEST_PER_USER + N_WARM_UP if not 'total' in request.POST else request.POST['total']
    
    count = int(count)
    total_count = int(total_count)

    selects = []
    for q in request.POST:
        # import pdb; pdb.set_trace()
        if not q[0].isdigit():
                continue
        question = Question.objects.get(pk=q)
        choice_id = request.POST['%d'%question.id]
        selected_choice =  question.choice_set.get(pk=choice_id)
        selects.append(selected_choice)
    
    # first two are warm-up questions
    if count > N_WARM_UP:
        for selected_choice in selects:
            selected_choice.votes += 1
            selected_choice.save()
            a = Answer(
                user=time_id,
                question=question.id,
                choice=selected_choice.notes,
                task=question.question_cata,
                time=str(datetime.now()),
            )
            a.save()

    if not selects:
        # Redisplay the question voting form.
        return render(request, 'FEdit/detail.html', {
            'question': question,
            'count': count,
            'time_id':time_id,
            'total': total_count,
            'error_message': "You didn't select a choice.",
        })
    

    else:

        if count >= total_count:
            return render(request, 'FEdit/results.html', {})
        q = Question.objects.filter(question_cata=question.question_cata).order_by("?")[0]
        return render(request, 'FEdit/detail.html', {
            'question': q,
            'count': count + 1,
            'total': total_count,
            'time_id':time_id,
        })


def viton(request):
    
    cata = 'viton' 
    context = {
        'cata':cata,
    }
    if request.method == "POST":
        # Redisplay the question voting form.
        # random choose between two tasks
        q = Question.objects.filter(question_cata=cata).order_by("?")[0]
        time_id = datetime.now()
        return render(request, 'FEdit/detail.html', {
            'question': q,
            'count': 1,
            'total': MAX_TEST_PER_USER_VTION + N_WARM_UP,
            'time_id':time_id,
        })
    return render(request, 'FEdit/index.html', context)

def pose(request):
    cata = 'posetrans' 
    context = {
        'cata':cata,
    }
    if request.method == "POST":
        # Redisplay the question voting form.
        # random choose between two tasks
        q = Question.objects.filter(question_cata=cata).order_by("?")[0]
        time_id = datetime.now()
        return render(request, 'FEdit/detail.html', {
            'question': q,
            'count': 1,
            'total': MAX_TEST_PER_USER + N_WARM_UP,
            'time_id':time_id,
        })
    return render(request, 'FEdit/index.html', context)

def index(request):
    # cata = 'viton' if random.random() >= 0.5 else 'posetrans'
    cata = 'posetrans'
    #latest_question_list = Question.objects.order_by('id') #('-pub_date')[:5]
    # latest_question_list = random.choice(latest_question_list, 10)
    context = {
        'cata':cata,
    }
    if request.method == "POST":
        # Redisplay the question voting form.
        # random choose between two tasks
        q = Question.objects.filter(question_cata=cata).order_by("?")[0]
        time_id = datetime.now()
        return render(request, 'FEdit/detail.html', {
            'question': q,
            'count': 1,
            'total': MAX_TEST_PER_USER + N_WARM_UP,
            'time_id':time_id,
        })
    return render(request, 'FEdit/index.html', context)

