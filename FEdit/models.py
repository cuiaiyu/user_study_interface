from django.db import models
from django.contrib.auth.models import User

MY_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'Both Fail'),
        ('D', 'D'),
    )
Q_TYPE_CHOICES = (
    ("single real/fake", "single real/fake"),
    ("real/fake", "real/fake"),
    ("conditional real/fake", "conditional real/fake"),
)
Q_CATA_CHOICES = (
    ("viton", "viton"),
    ("posetrans", "posetrans"),
    ("", ""),
)

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    question_ref_image = models.CharField(default='', max_length=200) 
    question_type = models.CharField(max_length=200, choices=Q_TYPE_CHOICES)
    question_cata = models.CharField(max_length=200, choices=Q_CATA_CHOICES, default="")
    correct_answer = models.CharField(max_length=1, choices=MY_CHOICES, default='D')

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    query_image = models.CharField(default='both_failed.png', max_length=200) 
    choice_text = models.CharField(max_length=200, default='D')
    notes = models.CharField(default='', max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text

class Answer(models.Model):
    user = models.CharField(max_length=200)
    question = models.CharField(max_length=200)
    choice = models.CharField(max_length=1)
    task = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    
    def __str__(self):
        return self.choice