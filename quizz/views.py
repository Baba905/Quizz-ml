from multiprocessing import context
from random import choice
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .models import QuizProfile, Question, AttemptedQuestion, Parcours
from .forms import UserLoginForm, RegistrationForm
from rest_framework.views import APIView
from rest_framework.response import Response
from quizz import serializers


def home(request):
    context = {}
    return render(request, 'quiz/home.html', context=context)


@login_required()
def user_home(request):
    parcours = Parcours.objects.all()
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

created = False
@login_required()
def play(request,id_parcours):
    
    #quiz_profile, created = QuizProfile.objects.get_or_create(user=request.user)
    parcours= Parcours.objects.get(id=id_parcours)
    categories_parcours = list(parcours.categorie.all())
    global created
    print(f" first {created}")
    if request.method == 'POST':
        print(f" POST method {created}")
        #print(len(list(QuizProfile.objects.filter(user = request.user))))
        quiz_profile = list(QuizProfile.objects.filter(user = request.user))
        #print(quiz_profile.id)

        question_pk = request.POST.get('question_pk')
        #print(question_pk)
        attempted_question = quiz_profile.attempts.select_related('question').get(question_id=question_pk)

        choice_pk = request.POST.get('choice_pk')

        try:
            selected_choice = attempted_question.question.choices.get(pk=choice_pk)
        except ObjectDoesNotExist:
            raise Http404

        quiz_profile.evaluate_attempt(attempted_question, selected_choice)

        return redirect(f'/play/{id_parcours}')
    else:
        print(f" GET method {created}")
        if not created :
            print(f" Get part {request.user}")

            quiz_profile= QuizProfile.objects.create(user=request.user, parcours= parcours)
            created = True
        else:
            quiz_profile = list(QuizProfile.objects.filter(user = request.user))[-1]
        
        categorie = choice(categories_parcours)
        question = quiz_profile.get_new_question(categorie.id)

        if question is not None:
            quiz_profile.create_attempt(question)
        else:
            created= False
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

# API Views 
class QuestionView(APIView):

    def get(self, request, format =None):
        questions = Question.objects.all()
        serializer = serializers.QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    #def put(self, request, format = None):
        