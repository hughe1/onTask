from django.contrib.auth.models import User
from jobs.models import Task
import random

# This script generates a fixed number of tasks, assigned to random users
 
tasks = []
 
for i in range(10):
    task = Task(title='Task{}'.format(i), 
                description='Description{}'.format(i),
                points=i,
                location='Location{}'.format(i),
                status='IC',
                user=User.objects.get(pk=random.randint(1,7))
                )
    tasks.append(task)
 
Task.objects.bulk_create(tasks)