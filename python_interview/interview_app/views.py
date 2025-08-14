from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Question, AIEvaluationAttempt, Option
import random
import google.generativeai as genai
from django.http import JsonResponse 


def home_view(request):
    request.session.flush()
    questions = Question.objects.all()
    return render(request, 'index.html', {'questions': questions})

def quiz_question_view(request, question_id=None):
    if 'question_order' not in request.session:
        question_ids = list(Question.objects.values_list('id', flat=True))
        random.shuffle(question_ids)
        request.session['question_order'] = question_ids
        request.session['current_index'] = 0
        request.session['answers'] = {}

    question_order = request.session['question_order']
    current_index = request.session['current_index']

    if question_id is None:
        if not question_order:
            return redirect('quiz-result')
        question_id = question_order[0]
    
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        selected_answer = request.POST.get('answer')
        
        answers = request.session.get('answers', {})
        answers[str(question_id)] = selected_answer
        request.session['answers'] = answers
        
        is_correct = question.correct_answer_key == selected_answer
        correct_answer_text = ""
        for option in question.options.all():
            if option.key == question.correct_answer_key:
                correct_answer_text = option.text
                break
        
        context = {
            'question': question,
            'selected_answer': selected_answer,
            'is_correct': is_correct,
            'correct_answer_key': question.correct_answer_key,
            'correct_answer_text': correct_answer_text,
            'show_result': True, 
        }
        return render(request, 'question.html', context)
    
    context = {
        'question': question,
        'show_result': False,
    }
    return render(request, 'question.html', context)


def next_question_view(request):
    current_index = request.session.get('current_index', 0)
    question_order = request.session.get('question_order', [])
    
    next_index = current_index + 1
    request.session['current_index'] = next_index

    if next_index < len(question_order):
        next_question_id = question_order[next_index]
        return redirect('quiz-question', question_id=next_question_id)
    else:
        return redirect('quiz-result')


def quiz_result_view(request):
    user_answers = request.session.get('answers', {})
    correct_questions = []
    incorrect_questions = []
    question_order = request.session.get('question_order', [])
    all_questions = Question.objects.in_bulk(question_order)

    for q_id_str, user_answer in user_answers.items():
        q_id = int(q_id_str)
        question = all_questions.get(q_id)
        if not question:
            continue

        question.user_answer = user_answer
        
        correct_option = question.options.filter(key=question.correct_answer_key).first()
        question.correct_answer_text = correct_option.text if correct_option else ""

        if question.correct_answer_key == user_answer:
            correct_questions.append(question)
        else:
            incorrect_questions.append(question)
    
    context = {
        'correct_questions': correct_questions,
        'incorrect_questions': incorrect_questions,
        'total': len(user_answers),
        'correct_count': len(correct_questions),
    }

    return render(request, 'result.html', context)


def ai_quiz_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    context = {'question': question}

    if request.method == "POST":
        user_answer = request.POST.get('user_answer', '').strip()

        if not user_answer:
            context['error'] = "Please provide an answer."
            return render(request, 'ai_question.html', context)

        question_text = question.question
        try:
            correct_option = question.options.get(key=question.correct_answer_key)
            correct_answer_text = correct_option.text
        except Option.DoesNotExist:
            context['error'] = "Could not find the correct answer for this question."
            return render(request, 'ai_question.html', context)

        prompt = f"""
        Evaluate the user's answer to the question.

        Question: "{question_text}"
        Correct answer: "{correct_answer_text}"
        User's answer: "{user_answer}"

        Is the user's answer correct or very close in meaning to the correct answer?
        Answer with only one word: 'True' if yes, and 'False' if no.
        """

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            ai_raw_response = response.text.strip()

            is_correct = ai_raw_response.lower() == 'true'
            
            # --- ВИПРАВЛЕННЯ ТУТ ---
            # Зберігаємо створений об'єкт, щоб отримати його ID
            new_attempt = AIEvaluationAttempt.objects.create(
                question=question,
                user_text_answer=user_answer,
                ai_response=ai_raw_response,
                is_correct_by_ai=is_correct
            )
            # --- КІНЕЦЬ ВИПРАВЛЕННЯ ---

            context['show_result'] = True
            context['user_answer'] = user_answer
            context['is_correct'] = is_correct
            context['correct_answer_text'] = correct_answer_text
            context['ai_response'] = ai_raw_response
            
            # --- ВИПРАВЛЕННЯ ТУТ ---
            # Передаємо ID в шаблон, щоб кнопка "Explain my mistake" знала, що пояснювати
            context['attempt_id'] = new_attempt.id
            # --- КІНЕЦЬ ВИПРАВЛЕННЯ ---

        except Exception as e:
            context['error'] = f"An error occurred while contacting the AI service: {e}"

    return render(request, 'ai_question.html', context)

def ai_quiz_start_view(request):
    question_ids = list(Question.objects.values_list('id', flat=True))
    random.shuffle(question_ids)
    
    request.session['ai_question_order'] = question_ids
    request.session['ai_current_index'] = 0

    if not question_ids:
        return redirect('home')

    first_question_id = question_ids[0]
    return redirect('ai-quiz-question', question_id=first_question_id)


def ai_next_question_view(request):
    current_index = request.session.get('ai_current_index', 0)
    question_order = request.session.get('ai_question_order', [])
    
    next_index = current_index + 1
    request.session['ai_current_index'] = next_index

    if next_index < len(question_order):
        next_question_id = question_order[next_index]
        return redirect('ai-quiz-question', question_id=next_question_id)
    else:
        return redirect('ai-quiz-result')


def ai_quiz_result_view(request):
    question_ids = request.session.get('ai_question_order', [])
    
    attempts = AIEvaluationAttempt.objects.filter(
        question_id__in=question_ids
    ).select_related('question')

    correct_attempts = []
    incorrect_attempts = []

    for attempt in attempts:
        if attempt.is_correct_by_ai:
            correct_attempts.append(attempt)
        else:
            incorrect_attempts.append(attempt)
    
    context = {
        'correct_attempts': correct_attempts,
        'incorrect_attempts': incorrect_attempts,
        'total': len(attempts),
        'correct_count': len(correct_attempts),
    }

    request.session.pop('ai_question_order', None)
    request.session.pop('ai_current_index', None)
    
    return render(request, 'ai_result.html', context)


def quiz_hint_view(request, question_id):
    if request.method == "GET":
        question = get_object_or_404(Question, id=question_id)

        prompt = f"""
        Give a short, one-sentence hint for the following interview question.
        Do not give the direct answer. The hint should gently guide the user to the correct concept.

        Question: "{question.question}"

        Example Hint: "Think about how Python handles memory for immutable vs. mutable types."
        
        Your response must be ONLY the hint text and in ukraine language.
        """

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            hint_text = response.text.strip()
            return JsonResponse({'success': True, 'hint': hint_text})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def explain_mistake_view(request, attempt_id):
    if request.method == "GET":
        attempt = get_object_or_404(AIEvaluationAttempt, id=attempt_id)
        
        try:
            correct_option = attempt.question.options.get(key=attempt.question.correct_answer_key)
            correct_answer_text = correct_option.text
        except Option.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Correct answer text not found.'}, status=500)
            
        prompt = f"""
        You are an experienced and friendly programming mentor.
        A student is taking a quiz and made a mistake. Explain their error in simple, encouraging terms.

        The original question was:
        "{attempt.question.question}"

        The student's incorrect answer was:
        "{attempt.user_text_answer}"

        The ideal correct answer is:
        "{correct_answer_text}"

        Your task:
        1. Briefly explain why the student's answer is incorrect or incomplete.
        2. Clearly explain why the ideal answer is correct, focusing on the core concept.
        3. Keep the tone positive and educational. Do not be condescending.

        Respond with only the explanation text in ukraine language.
        """

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            explanation_text = response.text.strip()

            return JsonResponse({'success': True, 'explanation': explanation_text})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)