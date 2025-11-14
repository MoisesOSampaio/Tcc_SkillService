from .serializers import SkillSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Skill
import os
from rest_framework.response import Response
import requests
import jwt
from django.db.models import Count


class Views:

    def verify_authentication(self, request,callback=None):       
        access_token : str = request.headers['Authorization'] 
        try:
            access_token = access_token.split(' ')[1]
        except IndexError:
            access_token = ''
        
        #print(access_token)
        body = {"token" : access_token}
        #print(body)
        validacao = requests.post(url=f'{os.getenv('AUTH_URL')}api/token/verify/', data=body)
        validacao = validacao.json()
        #print(f"validando:{validacao}")

        if validacao != {}:
            return Response(validacao, status=status.HTTP_401_UNAUTHORIZED)
        if callback is None:
            info_token = jwt.decode(access_token,options={"verify_signature": False})
            return info_token
        return callback(request)

class CreateSkillView(generics.CreateAPIView, Views):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def create(self, request, *args, **kwargs):
        token = self.verify_authentication(request)
        if isinstance(token,Response):
            return token
        data = request.data.copy()
        data["id_user"] = token["user_id"]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class GetUserSkillsView(generics.ListAPIView, Views):
    serializer_class = SkillSerializer

    def get_queryset(self):
        info_token = self.verify_authentication(self.request)
        return Skill.objects.filter(id_user=info_token.get("user_id"))


class PatchSkillView(generics.UpdateAPIView, Views):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    lookup_field = 'pk'
  
    def patch(self, request, *args, **kwargs):
        return self.verify_authentication(request,self.partial_update)

class DeleteSkillView(generics.DestroyAPIView, Views):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    def delete(self, request,*args, **kwargs):
        return self.verify_authentication(request, self.destroy)
        
    
class GetAllUserSkillsView(APIView):


    def get(self, request, *args, **kwargs):
        
        skills = Skill.objects.values('id_user', 'skill','proeficiencia','aprendendo').annotate(dcount=Count('id_user'))
        usuarios = {}
        for s in skills:
            id = str(s["id_user"])
            if id not in usuarios.keys():
                usuarios[id] = [
                    {
                    "habilidade" : s["skill"],
                    "proeficiencia": s["proeficiencia"],
                    "aprendendo": s["aprendendo"],
                    }]
                continue
            usuarios[id].append(
                {
                    "habilidade" : s["skill"],
                    "proeficiencia": s["proeficiencia"],
                    "aprendendo": s["aprendendo"],
                }
            )

        if not usuarios:
            return Response({"mensagem": "Sem Usuários com habilidades cadastradas na base"}, status=status.HTTP_204_NO_CONTENT)
        return Response(usuarios)
