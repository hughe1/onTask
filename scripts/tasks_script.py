"""job_bilby Script for creating bulk tasks, for testing purposes

 Generates a fixed number of tasks, assigned to random users

This file belongs to the back end source code for team 'job-bilby' for the
University of Melbourne subject SWEN90014 Masters Software Engineering Project.
The project is a mobile-first web application for sharing tasks.
The back-end is based on the REST Framework for Django.

Client: Paul Ashkar (Capgemini)                 paul.ashkar@capgemini.com
Supervisor: Rachel Burrows                      rachel.burrows@unimelb.edu.au
Team:
Annie Zhou:                                     azhou@student.unimelb.edu.au
David Barrel:                                   dbarrell@student.unimelb.edu.au
Grace Johnson:                                  gjohnson1@student.unimelb.edu.au
Hugh Edwards:                                   hughe@student.unimelb.edu.au
Matt Perrot:                                    mperrott@student.unimelb.edu.au 
View our 'Project Overview' document on Confluence for more information about the project.
Date project started: 6/8/2017
Date project completed: 15/10/2017
"""
from django.contrib.auth.models import User
from jobs.models import Task
import random

 
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