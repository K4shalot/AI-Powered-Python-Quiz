from django.db import models

class Question(models.Model):
    question = models.TextField()
    correct_answer_key = models.CharField(max_length=1)
    user_answer = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return self.question[:60]


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    key = models.CharField(max_length=1)
    text = models.TextField()

    def __str__(self):
        return f"{self.key}. {self.text[:50]}"
    
class AIEvaluationAttempt(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='ai_attempts')
    user_text_answer = models.TextField()
    ai_response = models.CharField(max_length=50, blank=True)
    is_correct_by_ai = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt for '{self.question.question[:30]}...' -> Correct: {self.is_correct_by_ai}"