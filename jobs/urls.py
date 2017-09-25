from django.conf.urls import url
from django.conf.urls import include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import authtoken
from jobs import views

urlpatterns = [

    url(r'^profiles/$', views.ProfileList.as_view(), name='profile-list'),
    url(r'^profile/$', views.current_profile, name='profile-current'),
    url(r'^profiles/create/$', views.create_profile, name='profile-create'),
    url(r'^profiles/(?P<pk>[0-9]+)/$', views.ProfileDetail.as_view(), name='profile-detail'),
    url(r'^tasks/$', views.TaskList.as_view(), name='task-list'),
    url(r'^tasks/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view(), name='task-detail'),
    url(r'^tasks/create/$', views.create_task, name='task-create'),
    url(r'^tasks/(?P<task_id>[0-9]+)/apply/$', views.apply_task, name='task-apply'),
    url(r'^tasks/start/$', views.start_task, name='task-start'),
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
    #url(r'^profiletasks/$', views.ProfileTaskList.as_view(), name='profiletask-list'),
    url(r'^profiletasks/(?P<pk>[0-9]+)/$', views.ProfileTaskDetail.as_view(), name='profiletask-detail'),


]


urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
