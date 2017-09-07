from django.conf.urls import url
from django.conf.urls import include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import authtoken
from jobs import views

urlpatterns = [

    url(r'^profiles/$', views.ProfileList.as_view(), name='profile-list'),
    url(r'^profiles/create/$', views.create_profile, name='profile-create'),
    url(r'^profiles/(?P<pk>[0-9]+)/$', views.ProfileDetail.as_view(), name='profile-detail'),
    url(r'^tasks/$', views.TaskList.as_view(), name='task-list'),
    url(r'^tasks/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view(), name='task-detail'),
    url(r'^tasks/create/$', views.create_task, name='task-create'),
    url(r'^tasks/apply/$', views.apply_task, name='task-apply'),
    url(r'^tasks/shortlist/$', views.shortlist_task, name='task-shortlist'),
    url(r'^tasks/discard/$', views.discard_task, name='task-discard'),
    url(r'^profiletasks/$', views.ProfileTaskList.as_view(), name='profiletask-list'),
    url(r'^profiletasks/(?P<pk>[0-9]+)/$', views.ProfileTaskDetail.as_view(), name='profiletask-detail'),


]


urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]