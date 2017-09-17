from django.contrib import admin
from jobs.models import *

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'pk')
    
class ProfileTaskAdmin(admin.ModelAdmin):
    list_display = ('__str__','pk',)
    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk')

admin.site.register(Task, TaskAdmin)
admin.site.register(Skill)
admin.site.register(ProfileSkill)
admin.site.register(ProfileTask, ProfileTaskAdmin)
admin.site.register(Comment)
admin.site.register(Profile, ProfileAdmin)
