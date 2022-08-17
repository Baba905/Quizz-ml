from cgitb import html
from multiprocessing import context
from random import choice
from traceback import print_tb
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .models import Categorie, QuizProfile, Question, AttemptedQuestion, Parcours, Choice
from .forms import UserLoginForm, RegistrationForm, AddWithExcel
from rest_framework.views import APIView
from rest_framework.response import Response
from quizz import serializers
import pandas as pd

created = False
def home(request):
    context = {}
    return render(request, 'quiz/home.html', context=context)


@login_required()
def user_home(request):
    global created
    parcours = Parcours.objects.all()
    created = False
    context = {'liste_parcours': parcours}
    return render(request, 'quiz/user_home.html', context=context)


def leaderboard(request):

    top_quiz_profiles = QuizProfile.objects.filter(user = request.user).order_by('-id')[:500]
    total_count = top_quiz_profiles.count()
    context = {
        'top_quiz_profiles': top_quiz_profiles,
        'total_count': total_count,
    }
    return render(request, 'quiz/leaderboard.html', context=context)


@login_required()
def play(request,id_parcours):
    
    #quiz_profile, created = QuizProfile.objects.get_or_create(user=request.user)
    parcours= Parcours.objects.get(id=id_parcours)
    categories_parcours = list(parcours.categorie.all())
    global created
    print(f" request.method= {request.method}")
    print(f" first {created}")
    if request.method == 'POST':
        print(f" POST method {created}")
        print(len(list(QuizProfile.objects.filter(user = request.user))))
        list_quizprofile = list(QuizProfile.objects.filter(user = request.user))
        quiz_profile = list_quizprofile[-1]
        #print(quiz_profile.id)

        question_pk = request.POST.get('question_pk')
        #print(question_pk)chrome://whats-new/
        attempted_question = quiz_profile.attempts.select_related('question').get(question_id=question_pk)

        choice_pk = request.POST.get('choice_pk')

        try:
            selected_choice = attempted_question.question.choices.get(pk=choice_pk)
        except ObjectDoesNotExist:
            raise Http404

        quiz_profile.evaluate_attempt(attempted_question, selected_choice)

        return redirect(f'/play/{id_parcours}')
    else:
        #print(f" GET method {created}")
        if not created :
            print(f" Get part {request.user}")
            print(f" Get parcours {parcours}")
            quiz_profile= QuizProfile.objects.create(user=request.user, parcours= parcours)
            print(f"  not created {created}")
            global created
            created = True
            print(f" GET created {created}")
        else:
            print(f"GET else  created {created}")
            print("number of quizprofile linked to this user",len(list(QuizProfile.objects.filter(user = request.user))))
            quiz_profile = list(QuizProfile.objects.filter(user = request.user))[-1]
        
        categorie = choice(categories_parcours)
        question = quiz_profile.get_new_question(categorie.id)

        if question is not None:
            quiz_profile.create_attempt(question)
        else:
           global created
           created= False
        #print(f" GET method second{created}")
        context = {
            'question': question,
            'parcours' : parcours,
        }

        return render(request, 'quiz/play.html', context=context)


@login_required()
def submission_result(request, attempted_question_pk):
    attempted_question = get_object_or_404(AttemptedQuestion, pk=attempted_question_pk)
    context = {
        'attempted_question': attempted_question,
    }

    return render(request, 'quiz/submission_result.html', context=context)


def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('/user-home')
    return render(request, 'quiz/login.html', {"form": form, "title": title})


def register(request):
    title = "Create account"
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = RegistrationForm()

    context = {'form': form, 'title': title}
    return render(request, 'quiz/registration.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('/')


def error_404(request):
    data = {}
    return render(request, 'quiz/error_404.html', data)


def error_500(request):
    data = {}
    return render(request, 'quiz/error_500.html', data)
from django.shortcuts import render

# Create your views here.

def resume_test(request, quiz_profile_id,):
    attempts = AttemptedQuestion.objects.filter(quiz_profile=quiz_profile_id)
    quizprofile = QuizProfile.objects.get(id= quiz_profile_id)
    results = quizprofile.calculation()
    tresult = []
    percentage = []
    for result in results:
        tmp = {
            'result':f'{result[0]},   {round(result[2]/result[1]*100)} %',
            'percent':str(result[2]/result[1]*100),
            }
        tresult.append(tmp)
        #percentage.append()
    context ={
        'attempts':attempts,
        'results' : tresult,
        #'percents' : percentage
    }
    return render(request, 'quiz/resume.html',context)

def affiche_categories(request, id_parcours):
    parcours =Parcours.objects.get(id = id_parcours)
    categories = parcours.categorie.all()
    questions=[]
    for categorie in categories :
        tmp = list(Question.objects.filter(categorie= categorie.id))
        questions.append((categorie,tmp))
    context= {
            'categories': categories,
            'questions' :questions
        }
    return render(request,'quiz/affiche.html',context)


def add_questions_with_excel(request):
    if request.method== 'POST':
        form = AddWithExcel(request.POST)

        if form.is_valid():
            path = form.cleaned_data['path_file']
            questions = pd.read_excel(path, index_col=0)
            questions = questions.head()

            for i in range(1, len(questions)+1):
                ques_excel = questions.loc[i]
                categorie = Categorie.objects.get(nom= ques_excel["Categories"])
                question = Question(html=ques_excel["Questions"], categorie= categorie)
                question.save()
                good_answer = int(ques_excel['Bonne_reponse'][-1])

                for j in range(4):
                    if j == good_answer-1:
                        choice = Choice(html=ques_excel[f"Opt{j+1}"],question=question,is_correct= True)
                        choice.save()
                    else:
                        choice = Choice(html=ques_excel[f"Opt{j+1}"],question=question)
                        choice.save()
            return redirect('home') 
        else :
            return Http404("Formulaire non valide")
    else:
        form = AddWithExcel()
        context = {'form':form}
        return render(request,'quiz/parametre.html',context)


# API Views 
class QuestionView(APIView):

    def get(self, request, format =None):
        questions = Question.objects.all()
        serializer = serializers.QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    #def put(self, request, format = None):
        