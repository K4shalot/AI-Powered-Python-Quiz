from django.contrib import admin
from .models import Question, Option, Category, AIEvaluationAttempt

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'category', 'complexity', 'correct_answer_key')
    list_filter = ('category', 'complexity')
    search_fields = ('question',)
    list_editable = ('category', 'complexity', 'correct_answer_key')
    inlines = [OptionInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(AIEvaluationAttempt)
class AIEvaluationAttemptAdmin(admin.ModelAdmin):
    list_display = ('question', 'user_text_answer', 'is_correct_by_ai', 'created_at')
    list_filter = ('is_correct_by_ai',)
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False