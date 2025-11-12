from .serializers import SkillSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Skill
import os
from rest_framework.response import Response
import requests
import jwt
from django.db.models import Count
class CreateSkillView(generics.CreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer



    def create(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        #print(access_token)
        cookies = {"access_token" : access_token}
        validacao = requests.post(url=f'{os.getenv("AUTH_URL")}api/token/verify/', cookies=cookies)
        validacao = validacao.json()
        #print(f"validando:{validacao}")

        if validacao != {}:
            return Response(validacao, status=status.HTTP_401_UNAUTHORIZED)
        info_token = jwt.decode(access_token,options={"verify_signature": False})
        data = request.data.copy()
        data["id_user"] = info_token["user_id"]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class GetUserSkillsView(generics.ListAPIView):
    serializer_class = SkillSerializer

    def get_queryset(self):
        access_token = self.request.COOKIES.get("access_token")
        
        cookies = {"access_token" : access_token}
        
        validacao = requests.post(url=f'{os.getenv("AUTH_URL")}api/token/verify/', cookies=cookies)
        if validacao.status_code != 200:
            return Response({"mensagem": "Erro ao Validar token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        validacao = validacao.json()
        if validacao != {}:
            return Response(validacao, status=status.HTTP_401_UNAUTHORIZED)
        info_token = jwt.decode(access_token,options={"verify_signature": False})

        return Skill.objects.filter(id_user=info_token.get("user_id"))

    


class PatchUserView(generics.UpdateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    lookup_field = 'pk'
  


    def patch(self, request, *args, **kwargs):
        
        access_token = request.COOKIES.get("access_token")
        cookies = {"access_token" : access_token}

        validacao = requests.post(url=f'{os.getenv("AUTH_URL")}api/token/verify/' , cookies=cookies)
        validacao = validacao.json()
        if validacao != {}:
            return Response(validacao, status=status.HTTP_401_UNAUTHORIZED)
        return super().patch(request, *args, **kwargs)
    
class GetAllUserSkillsView(APIView):
#    serializer_class = SkillSerializer
#    queryset = Skill.objects.values('id_user')

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
