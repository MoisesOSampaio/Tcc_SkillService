from .views import CreateSkillView, GetUserSkillsView, PatchSkillView, GetAllUserSkillsView, DeleteSkillView
from django.urls import path

urlpatterns = [
    path('skill/create/', CreateSkillView.as_view(), name='skill-create'),
    path('skill/', GetUserSkillsView.as_view(), name='get-user-skills'),
    path('skill/patch/<int:pk>', PatchSkillView.as_view(), name='path-user-skill'),
    path('skill/users/', GetAllUserSkillsView.as_view(), name='get-all-users-skills'),
    path('skill/delete/<int:pk>',DeleteSkillView.as_view(), name='delete-skill' )
]