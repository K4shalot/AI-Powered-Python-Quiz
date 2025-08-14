"""
URL configuration for python_interview project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from interview_app.views import (
    home_view, 
    quiz_question_view, 
    quiz_result_view, 
    next_question_view,
    ai_quiz_start_view, 
    ai_quiz_view,
    ai_next_question_view,
    ai_quiz_result_view,
    quiz_hint_view,
    explain_mistake_view
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    
    path('quiz/', quiz_question_view, name='quiz-start'),
    path('quiz/<int:question_id>/', quiz_question_view, name='quiz-question'),
    path('quiz/next/', next_question_view, name='quiz-next'),
    path('quiz/result/', quiz_result_view, name='quiz-result'),
    
    path('ai-quiz/', ai_quiz_start_view, name='ai-quiz-start'),
    path('ai-quiz/<int:question_id>/', ai_quiz_view, name='ai-quiz-question'),
    path('ai-quiz/next/', ai_next_question_view, name='ai-quiz-next'),
    path('ai-quiz/result/', ai_quiz_result_view, name='ai-quiz-result'),
    path('api/hint/<int:question_id>/', quiz_hint_view, name='quiz-hint'),
    path('api/explain/<int:attempt_id>/', explain_mistake_view, name='quiz-explain-mistake'),
]