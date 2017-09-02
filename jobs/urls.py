from django.conf.urls import url
from django.conf.urls import include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import authtoken
from jobs import views

urlpatterns = [

    url(r'^profiles/$', views.ProfileList.as_view()),
    url(r'^profiles/create/$', views.create_profile),
    url(r'^profiles/(?P<pk>[0-9]+)/$', views.ProfileDetail.as_view()),
    url(r'^tasks/$', views.TaskList.as_view()),
    url(r'^tasks/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view()),
    url(r'^tasks/create/$', views.create_task),
    url(r'^tasks/apply/$', views.apply_task),
    url(r'^tasks/shortlist/$', views.shortlist_task),
    url(r'^tasks/discard/$', views.discard_task),
    url(r'^profiletasks/$', views.ProfileTaskList.as_view()),
    url(r'^profiletasks/(?P<pk>[0-9]+)/$', views.ProfileTaskDetail.as_view()),

]


urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]