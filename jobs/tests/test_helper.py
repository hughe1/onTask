from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from jobs.models import Profile, User, Task, ProfileTask, Skill

# Return a token to authorise API calls
def api_login(user):
    token, created = Token.objects.get_or_create(user=user)
    return token.key

# Create a user indexed by the argument user_number
def create_user(user_num):
    user = User.objects.create(
        username="test{}_user".format(user_num),
        email="test{}@user.com".format(user_num),
        password="testing1234",
        first_name="test{}".format(user_num),
        last_name="user{}".format(user_num)
    )
    return user  

# Update profile information
def update_profile(user, user_num):
    profile = Profile.objects.get(user=user)
    profile.location = "Location {}".format(user_num)
    profile.description = "Description {}".format(user_num)
    return profile

# Create a user and profile and return the profile
def create_profile(user_num):
    user = create_user(user_num)
    profile = update_profile(user, user_num)
    return profile
    
# Create and return a task
def create_task(owner_prof, task_num):
    task = Task.objects.create(
        title="Task {}".format(task_num),
        description="Desc {}".format(task_num),
        offer=0,
        location="Loc {}".format(task_num),
        owner=owner_prof
    )
    return task

# Create a skill    
def create_skill(title):
    if len(title) > 2:
        code = title[:2]
    else:
        code = title

    skill = Skill.objects.create(
        title=title,
        code=code
    )
    return skill
        
# Delete a user
@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def delete_user_profile(request):
    username = request.data["username"]
    if not (request.user.username == 'job_user'):
        # os.environ['DB_USERNAME']
        return Response({"error":"Only admin can delete users"})
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
    except:
        return Response({"Error": "Not found"})
    profile.delete()
    user.delete()
    return Response({"Success": "User and profile deleted successfully"})

# Delete a profile task
@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def delete_profile_task(request):
    profile = request.user.profile
    try:
        task = Task.objects.get(pk=request.data["task_id"])
        profile_task = ProfileTask.objects.get(profile=profile, task=task)
    except:
        return Response({"Error": "Not found"})
    profile_task.delete()
    return Response({"Sucess": "ProfileTask deleted successfully"})
    
# Delete a profile task
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def unapply(request):
    try:
        task = Task.objects.get(pk=request.data["task_id"])
        profile_task = ProfileTask.objects.get(task=task, profile=request.user.profile)
    except:
        return Response({"Error": "Not found"})
    profile_task.status = ProfileTask.SHORTLISTED
    profile_task.save()
    return Response({"Sucess": "ProfileTask unapplied successfully"})