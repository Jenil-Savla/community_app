from rest_framework.generics import GenericAPIView
from rest_framework import status,permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import random

from .models import User
from .serializers import RegisterSerializer,LoginSerializer
from . import util

# Create your views here.
class RegisterAPI(GenericAPIView):
	
	serializer_class = RegisterSerializer
	
	def post(self,request,*args,**kwargs):
		try:
			data = request.data
			data = dict(data)
			data['password'] = '12345678'
			serializer = self.serializer_class(data=data)
			if serializer.is_valid(raise_exception = True):
				user = serializer.save()
				token = Token.objects.create(user=user)
				'''current_site = get_current_site(request).domain
				relative_link = reverse('email-verify')
				link = 'http://'+current_site+relative_link+'?token='+ token.key
				data = {'email_body': f'Use this link to get verified {link}.', 'subject':'Email Verification', 'to' : user.email}'''
				#util.send_email(data)
				return Response({"status" : True ,"data" : serializer.data, "message" : 'Request Sent'},status=status.HTTP_200_OK)
			return Response({"status" : False ,"data" : serializer.errors, "message" : "Failure"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(GenericAPIView):
	
	serializer_class = LoginSerializer
	
	def post(self,request,*args,**kwargs ):
		email = request.data.get('email',None)
		password = request.data.get('password',None)
		user = authenticate(email = email, password = password)
		if user :
			serializer = self.serializer_class(user)
			token = Token.objects.get(user=user)
			return Response({"status" : True ,"data" : {'token' : token.key,'email' : user.email}, "message" : 'Login Success'},status = status.HTTP_200_OK)
		return Response({"status" : False ,"data" : {}, "message" : 'Invalid Credentials'},status = status.HTTP_401_UNAUTHORIZED)
	
class UserRequest(GenericAPIView):
	
	serializer_class = RegisterSerializer
	queryset = User.objects.filter(is_active = False)
	permission_classes = [permissions.IsAdminUser,]

	def get(self,request):
		try:
			users = self.get_queryset()
			serializer = self.serializer_class(users, many=True)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	def post(self,request):
		try:
			email = request.data['email']
			user = User.objects.get(email=email)
			user_data = self.serializer_class(user).data
			password = email[:4]+str(random.randint(1000,9999))
			data ={'email_body': f"Congratulations! your account is activated.\nUsername: {user_data['email']}\nPassword: {password}", 'email_subject': "Account activated!",'to_email':user_data['email']}
			util.send_email(data)
			user.set_password(password)
			user.is_active = True
			user.save()
			return Response({"status" : True ,"data" : {}, "message" : "User Activated"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)