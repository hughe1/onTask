"""job_bilby Jobs app admin configuration

Registers application details to be viewable in the Django default Admin suite.

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

from django.contrib import admin
from jobs.models import *

class TaskAdmin(admin.ModelAdmin):
	""" defines admin display characteristics for Tasks """
    list_display = ('title', 'pk')
    
class ProfileTaskAdmin(admin.ModelAdmin):
	""" defines admin display characteristics for ProfileTasks """
    list_display = ('__str__','pk',)
    
class ProfileAdmin(admin.ModelAdmin):
	""" defines admin display characteristics for Profiles """
    list_display = ('user', 'pk')

# Register models with the admin suite.
admin.site.register(Task, TaskAdmin)
admin.site.register(Skill)
admin.site.register(ProfileSkill)
admin.site.register(ProfileTask, ProfileTaskAdmin)
admin.site.register(Profile, ProfileAdmin)
