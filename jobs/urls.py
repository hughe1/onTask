"""job_bilby URL patterns for the Jobs application

This file belongs to the back end source code for team 'job-bilby' for the
University of Melbourne subject SWEN90014 Masters Software Engineering Project.
The project is a mobile-first web application for sharing tasks.
The back-end is based on the REST Framework for Django.

Client: Paul Ashkar (Capgemini)                 paul.ashkar@capgemini.com
Supervisor: Rachel Burrows                      rachel.burrows@unimelb.edu.au
Team:
Annie Zhou:                                     azhou@student.unimelb.edu.au
David Barrell:                                  dbarrell@student.unimelb.edu.au
Grace Johnson:                                  gjohnson1@student.unimelb.edu.au
Hugh Edwards:                                   hughe@student.unimelb.edu.au
Matt Perrot:                                    mperrott@student.unimelb.edu.au 
View our 'Project Overview' document on Confluence for more information about the project.
Date project started: 6/8/2017
Date project completed: 15/10/2017
"""
from django.conf.urls import url
from django.conf.urls import include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import authtoken
from jobs import views
from jobs.tests import test_helper

urlpatterns = [

    url(r'^profiles/$', views.ProfileList.as_view(), name='profile-list'),
    url(r'^profile/$', views.current_profile, name='profile-current'),
    url(r'^profile/update_skills/$', views.update_skills, name='update-skills'),
    url(r'^profiles/create/$', views.create_profile, name='profile-create'),
    url(r'^profiles/(?P<pk>[0-9]+)/$', views.ProfileDetail.as_view(), name='profile-detail'),
    url(r'^user/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='user-update'),
    url(r'^tasks/$', views.TaskList.as_view(), name='task-list'),
    url(r'^tasks/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view(), name='task-detail'),
    url(r'^tasks/create/$', views.create_task, name='task-create'),
    url(r'^tasks/(?P<task_id>[0-9]+)/apply/$', views.apply_task, name='task-apply'),
    url(r'^tasks/shortlist/$', views.shortlist_task, name='task-shortlist'),
    url(r'^tasks/helper/$', views.HelperTaskList.as_view(), name='task-helper'),
    url(r'^tasks/poster/$', views.PosterTaskList.as_view(), name='task-poster'),
    url(r'^tasks/discard/$', views.discard_task, name='task-discard'),
    url(r'^tasks/(?P<task_id>[0-9]+)/delete/$', views.delete_task, name='task-delete'),
    url(r'^tasks/(?P<task_id>[0-9]+)/applicants/$', views.view_applicants, name='task-view-applicants'),
    url(r'^tasks/(?P<task_id>[0-9]+)/accept/$', views.accept_applicant, name='task-accept-applicant'),
    url(r'^tasks/(?P<task_id>[0-9]+)/rate/$', views.rate_helper, name='rate-helper'),
    url(r'^tasks/reject/$', views.reject_application, name='task-reject_application'),
    url(r'^tasks/shortlist_application/$', views.shortlist_application, name='task-shortlist_application'),
    url(r'^tasks/complete/$', views.complete_task, name='task-complete'),
    url(r'^profiletasks/(?P<pk>[0-9]+)/$', views.ProfileTaskDetail.as_view(), name='profiletask-detail'),
    url(r'^profiles/(?P<profile_id>[0-9]+)/under_application_limit/$', views.under_application_limit, name='under-application-limit'),
    url(r'^skills/$', views.SkillList.as_view(), name='skill-list'),
    url(r'^password_reset/$', views.password_reset, name='password-reset'),
    
    # Just for testing purposes
    url(r'^profile/delete/$', test_helper.delete_user_profile, name='profile-delete'),
    url(r'^profile_task/delete/$', test_helper.delete_profile_task, name='profile_task-delete'),
    url(r'^tasks/unapply/$', test_helper.unapply, name='unapply'),
]

# Format URLs to be consistent with the REST Framework standard
urlpatterns = format_suffix_patterns(urlpatterns)

# Adds API Authentication URL
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
