from django.contrib import admin
from jobs.models import *

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'pk')
    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk')

admin.site.register(Task, TaskAdmin)
admin.site.register(Skill)
admin.site.register(ProfileSkill)
admin.site.register(ProfileTask)
admin.site.register(Comment)
admin.site.register(Profile, ProfileAdmin)
