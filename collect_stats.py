import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gui.settings")
import django
django.setup()
from FEdit.models import Question, Choice, Answer
import collections
import random
import numpy as np
import imageio
from tqdm import tqdm



def get_stats(answer_list):
    # basic
    n_answers = len(answer_list)
    n_questions = len(set([a.question for a in answer_list]))
    users = collections.defaultdict(list)
    for a in answer_list:
        users[a.user].append((a.question))
    n_users = len(users)
    print("[total] Get %d answers for %d questions from %d users. " % (n_answers, n_questions, n_users))
    print("[user] %.2f questions per user." % (sum([len(users[u]) for u in users]) * 1.0 / (n_users + 1e-12)))

    choices = collections.defaultdict(list)
    for answer in answer_list:
        choices[answer.choice] += [(answer.user, answer.question)]

    out = collections.defaultdict(str)
    for choice in choices:
        n_c = len(choices[choice])
        prefix, exp_name = choice.split(";")
        n_total = sum([len(choices[item]) for item in choices if item.startswith(prefix)])
        out[prefix] += '--[choice][%s]  %.2f%%, (%d/%d)\n' % (exp_name.ljust(8),  n_c * 100.0 / (n_total+1e-12), n_c, n_total,)

    for exp in out:
        print("EXP\n>> %s" % exp)
        print(out[exp])

# get answers
all_answer_list = Answer.objects.order_by('id')
all_question_list = Question.objects.order_by('id')
all_choice_list = Choice.objects.order_by('id')
import pickle
with open('stats.pkl', 'wb') as f:
    pickle.dump({'answer': all_answer_list,
                 'question': all_question_list,
                 'choice': all_choice_list,
                },f)
    

# viton
print("\n ---------viton---------")
answer_list = [a for a in all_answer_list if a.task == 'viton']
get_stats(answer_list)

# pose
print("\n ---------pose---------")
answer_list = [a for a in all_answer_list if a.task == 'posetrans']
get_stats(answer_list)