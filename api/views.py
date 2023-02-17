from rest_framework.generics import GenericAPIView
from rest_framework import status,permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.db.models import Q
import random

from .models import User, Village, Family, OccupationAddress
from .serializers import RegisterSerializer,LoginSerializer,MemberSerializer,VillageSerializer,FamilySerializer,OccupationAddressSerializer
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
				village = Village.objects.get(name__icontains = data['village'])
				family = Family.objects.create(head = user, village = village)
				occupation = OccupationAddress.objects.create(family=family)
				user = serializer.save(related_family = family)
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
		
class MemberListAPI(GenericAPIView):
	
	serializer_class = MemberSerializer
	queryset = User.objects.all()
	permission_classes = [permissions.IsAuthenticated,]

	def get(self,request):
		try:
			users = self.get_queryset()
			serializer = self.serializer_class(users, many=True)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request):
		try:
			filter_data = request.data
			if filter_data['name'] == 'all':
				if filter_data['city'] != 'all' and filter_data['village'] != 'all' and filter_data['gender'] != 'all':
					users = User.objects.filter(city__icontains = filter_data['city'], village__in = filter_data['village'], gender__in =  filter_data['gender'])
				elif filter_data['city'] == 'all' and filter_data['village'] != 'all' and filter_data['gender'] != 'all':
					users = User.objects.filter(village__in = filter_data['village'], gender__in =  filter_data['gender'])
				elif filter_data['city'] != 'all' and filter_data['village'] == 'all' and filter_data['gender'] != 'all':
					users = User.objects.filter(city__icontains = filter_data['city'], gender__in =  filter_data['gender'])
				elif filter_data['city'] != 'all' and filter_data['village'] != 'all' and filter_data['gender'] == 'all':
					users = User.objects.filter(city__icontains = filter_data['city'], village__in = filter_data['village'])
				elif filter_data['city'] == 'all' and filter_data['village'] == 'all' and filter_data['gender'] != 'all':
					users = User.objects.filter(gender__in =  filter_data['gender'])
				elif filter_data['city'] == 'all' and filter_data['village'] != 'all' and filter_data['gender'] == 'all':
					users = User.objects.filter(village__in = filter_data['village'])
				elif filter_data['city'] != 'all' and filter_data['village'] == 'all' and filter_data['gender'] == 'all':
					users = User.objects.filter(city__icontains = filter_data['city'])
				else:
					users = self.get_queryset()
			else:
				name = filter_data['name'].split(" ")
				fname = name[0]
				lname = name[len(name)-1]
				if len(name) == 1:
					if filter_data['city'] != 'all' and filter_data['village'] != 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), city__icontains = filter_data['city'], village__icontains = filter_data['village'], gender =  filter_data['gender'])
					elif filter_data['city'] == 'all' and filter_data['village'] != 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), village__icontains = filter_data['village'], gender =  filter_data['gender'])
					elif filter_data['city'] != 'all' and filter_data['village'] == 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), city__icontains = filter_data['city'], gender =  filter_data['gender'])
					elif filter_data['city'] != 'all' and filter_data['village'] != 'all' and filter_data['gender'] == 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), city__icontains = filter_data['city'], village__icontains = filter_data['village'])
					elif filter_data['city'] == 'all' and filter_data['village'] == 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), gender =  filter_data['gender'])
					elif filter_data['city'] == 'all' and filter_data['village'] != 'all' and filter_data['gender'] == 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), village__icontains = filter_data['village'])
					elif filter_data['city'] != 'all' and filter_data['village'] == 'all' and filter_data['gender'] == 'all':
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname), city__icontains = filter_data['city'])
					else:
						users = User.objects.filter(Q(first_name__icontains = fname) | Q(last_name__icontains = fname))
				else:
					if filter_data['city'] != 'all' and filter_data['village'] != 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, city__icontains = filter_data['city'], village__icontains = filter_data['village'], gender =  filter_data['gender']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, city__icontains = filter_data['city'], village__icontains = filter_data['village'], gender =  filter_data['gender'])
					elif filter_data['city'] == 'all' and filter_data['village'] != 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, village__icontains = filter_data['village'], gender =  filter_data['gender']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, village__icontains = filter_data['village'], gender =  filter_data['gender'])
					elif filter_data['city'] != 'all' and filter_data['village'] == 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, city__icontains = filter_data['city'], gender =  filter_data['gender']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, city__icontains = filter_data['city'], gender =  filter_data['gender'])
					elif filter_data['city'] != 'all' and filter_data['village'] != 'all' and filter_data['gender'] == 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, city__icontains = filter_data['city'], village__icontains = filter_data['village']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, city__icontains = filter_data['city'], village__icontains = filter_data['village'])
					elif filter_data['city'] == 'all' and filter_data['village'] == 'all' and filter_data['gender'] != 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, gender =  filter_data['gender']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, gender =  filter_data['gender'])
					elif filter_data['city'] == 'all' and filter_data['village'] != 'all' and filter_data['gender'] == 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, village__icontains = filter_data['village']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, village__icontains = filter_data['village'])
					elif filter_data['city'] != 'all' and filter_data['village'] == 'all' and filter_data['gender'] == 'all':
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname, city__icontains = filter_data['city']) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname, city__icontains = filter_data['city'])
					else:
						users = User.objects.filter(first_name__icontains = fname, last_name__icontains = lname) | User.objects.filter(first_name__icontains = lname, last_name__icontains = fname)
				
			serializer = self.serializer_class(users, many=True)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)

		except:
			return Response({"status" : False ,"data" : {}, "message" : "Invalid filter"}, status=status.HTTP_400_BAD_REQUEST)
		
class VillageAPI(GenericAPIView):
	serializer_class = VillageSerializer
	queryset = Village.objects.all()

	def get(self,request):
		try:
			villages = self.get_queryset()
			serializer = self.serializer_class(villages, many=True)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class FamilyAPI(GenericAPIView):
	serializer_class = FamilySerializer
	queryset = Family.objects.all()
	permission_classes = [permissions.IsAuthenticated,]

	def get(self,request,pk):
		try:
			family = Family.objects.get(id = pk)
			family_serializer = self.serializer_class(family)
			data = dict(family_serializer.data)
			if request.user == family.head:
				data['can_edit'] = True
			else:
				data['can_edit'] = False
			occupation_address = OccupationAddress.objects.filter(family = family)
			occupation_address_serializer = OccupationAddressSerializer(occupation_address, many =True)
			data['occupations'] = list(occupation_address_serializer.data)
			members = User.objects.filter(related_family = family)
			user_serializer = MemberSerializer(members, many = True)
			data['members'] = list(user_serializer.data)
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def post(self,request,pk):
		try:
			data = dict(request.data)
			family = Family.objects.get(id = pk)
			if request.user != family.head:
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can edit this data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			data['family'] = family.id
			serializer = OccupationAddressSerializer(data=data)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self,request,pk):
		try:
			data = request.data
			family = Family.objects.get(id = pk)
			if request.user != family.head:
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can edit this data"}, status=status.HTTP_400_BAD_REQUEST)
			occupation = data.pop('occupations')
			for occ in occupation:
				occupation = OccupationAddress.objects.get(id = occ['id'])
				occupation_serializer = OccupationAddressSerializer(instance = occupation, data = occ, partial = True)
				if occupation_serializer.is_valid(raise_exception=True):
					occupation_serializer.save()
			family_serializer = self.serializer_class(instance = family, data = data, partial = True)
			if family_serializer.is_valid(raise_exception=True):
				family_serializer.save()
			return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
class MemberAPI(GenericAPIView):
	
	serializer_class = MemberSerializer
	queryset = User.objects.all()
	permission_classes = [permissions.IsAuthenticated,]

	def post(self,request,pk):
		try:
			data = dict(request.data)
			family = Family.objects.get(id = pk)
			if request.user != family.head:
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can add member"}, status=status.HTTP_400_BAD_REQUEST)
			data['password'] = data['email'][:4]+str(random.randint(1000,9999))
			data['village'] = family.village.name
			data['related_family'] = family.id
			serializer = MemberSerializer(data=data)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	def put(self,request,pk):
		try:
			data = dict(request.data)
			family = Family.objects.get(id = pk)
			if request.user != family.head:
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can edit member"}, status=status.HTTP_400_BAD_REQUEST)
			data['password'] = data['email'][:4]+str(random.randint(1000,9999))
			data['village'] = family.village.name
			data['related_family'] = family.id
			user = User.objects.get(email = data['email'])
			serializer = MemberSerializer(instance = user, data=data, partial = True)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def delete(self,request,pk):
		try:
			email = request.data['email']
			family = Family.objects.get(id = pk)
			if request.user != family.head:
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can delete member"}, status=status.HTTP_400_BAD_REQUEST)
			user = User.objects.get(email = email)
			user.delete()
			return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)