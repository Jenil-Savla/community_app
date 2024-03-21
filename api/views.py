from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework import status,permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.db.models import Q
import random

from .models import CommitteeMember, Content, User, Village, Family, OccupationAddress, Event, SocietyMember, Founder, Blog
from .serializers import CommitteeMemberSerializer, ContentSerializer, ForgotPasswordSerializer, RegisterSerializer,LoginSerializer,MemberSerializer,VillageSerializer,FamilySerializer,OccupationAddressSerializer, EventSerializer, SocietyMemberSerializer, FounderSerializer, UpdatedMemberSerializer, BlogSerializer
from . import util

class IsAdminUserOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(IsAdminUserOrReadOnly, self).has_permission(request, view)
        # Python3: is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin

# Create your views here.
@api_view(['GET'])
def homepage(request):
	try:
		data = dict()
		counter = set()
		for family in Family.objects.all():
			counter.add(family.head.city.lower())
		data['cities'] = len(counter)
		data['families'] = Family.objects.count()
		data['members'] = User.objects.count()
		return Response({"status" : True ,"data" : data, "message" : 'Success'},status=status.HTTP_200_OK)
	except:
		return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPI(GenericAPIView):
	
	serializer_class = RegisterSerializer
	
	def post(self,request,*args,**kwargs):
		try:
			data = request.data
			data = dict(data)
			data['password'] = data['username'] #[:8]
			data['email_id'] = data['email']
			if not 'in_laws_name' in data.keys():
				data['in_laws_name'] = 'NA'
			serializer = self.serializer_class(data=data)
			if serializer.is_valid(raise_exception = True):
				user = serializer.save()
				print(user.password)
				token = Token.objects.create(user=user)
				'''current_site = get_current_site(request).domain
				relative_link = reverse('email-verify')
				link = 'http://'+current_site+relative_link+'?token='+ token.key
				data = {'email_body': f'Use this link to get verified {link}.', 'subject':'Email Verification', 'to' : user.email}'''
				#util.send_email(data)
				village = Village.objects.filter(name__icontains = data['village'])
				if village.exists():
					village = village.first()
				print("here")
				family = Family.objects.create(head = user, village = village)
				occupation = OccupationAddress.objects.create(family=family)
				user.related_family = family
				user.save()
				return Response({"status" : True ,"data" : serializer.data, "message" : 'Request Sent'},status=status.HTTP_200_OK)
			return Response({"status" : False ,"data" : serializer.errors, "message" : "Failure"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(GenericAPIView):
	
	serializer_class = LoginSerializer
	
	def post(self,request,*args,**kwargs ):
		username = request.data.get('username',None)
		password = request.data.get('password',None)

		print(username,password)
		user = authenticate(username = username, password = password)
		print(user)
		if user :
			login(request,user)
			serializer = self.serializer_class(user)
			token,k = Token.objects.get_or_create(user=user)
			return Response({"status" : True ,"data" : {'token' : token.key,'username' : user.username, 'family':user.related_family.id}, "message" : 'Login Success'},status = status.HTTP_200_OK)
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
	
	serializer_class = UpdatedMemberSerializer
	queryset = User.objects.all()
	permission_classes = [permissions.IsAuthenticated,]

	def get(self,request):
		if 1: #try:
			users = self.get_queryset()[:50]
			serializer = self.serializer_class(users, many=True)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		# except:
		# 	return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request):
		try:
			filter_data = request.data
			maritial_status = request.GET.get('maritial_status',None)
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
			if maritial_status:
				users = users.filter(maritial_status__icontains = maritial_status)
			serializer = self.serializer_class(users, many=True)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)

		except Exception as e:
			print(e)
			return Response({"status" : False ,"data" : {}, "message" : "Invalid filter"}, status=status.HTTP_400_BAD_REQUEST)
		
class VillageAPI(GenericAPIView):
	serializer_class = VillageSerializer
	queryset = Village.objects.all()

	def get(self,request):
		try:
			villages = self.get_queryset()
			villages.update(no_of_families = 0)
			families = Family.objects.all().values('village')
			for family in families:
				village = Village.objects.get(id = family['village'])
				village.no_of_families += 1
				village.save()
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
		except Exception as e:
			print(e)
			return Response({"status" : False ,"data" : {}, "message" : f"Internal Server Error + {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
class MemberAPI(GenericAPIView):
	
	serializer_class = MemberSerializer
	queryset = User.objects.all()
	permission_classes = [permissions.IsAuthenticated,]

	def get(self,request,pk):
		try:
			member = User.objects.get(email = pk)
			serializer = self.serializer_class(member)
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def post(self,request,pk):
		try:
			data = dict(request.data)
			if(type(data['email']) == list):
				for i in data.keys():
					data[i] = data[i][0]
			family = Family.objects.get(id = pk)
			if (request.user != family.head):
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can add member"}, status=status.HTTP_400_BAD_REQUEST)
			data['password'] = data['email'][:4]+str(random.randint(1000,9999))
			data['village'] = family.village.name
			data['email_id'] = data['email']
			data['related_family'] = family.id
			serializer = MemberSerializer(data=data)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	def put(self,request,pk):
		try:
			data = dict(request.data)
			if(type(data['email']) == list):
				for i in data.keys():
					data[i] = data[i][0]
			family = Family.objects.get(id = pk)
			if request.user != family.head:
				return Response({"status" : False ,"data" : {}, "message" : "Only head of family can edit member"}, status=status.HTTP_400_BAD_REQUEST)
			#data['password'] = data['email'][:4]+str(random.randint(1000,9999))
			data['village'] = family.village.name
			data['related_family'] = family.id
			user = User.objects.get(email = data['email'])
			serializer = MemberSerializer(instance = user, data=data, partial = True)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
				return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
			return Response({"status" : False ,"data" : serializer.errors, "message" : "Failure"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			print(e)
			return Response({"status" : False ,"data" : {}, "message" : f"Internal Server Error + {e.message}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
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
		
class EventAPI(GenericAPIView):

	serializer_class = EventSerializer
	permission_classes = [permissions.IsAuthenticated,]

	def get(self,request,pk):
		try:
			event = Event.objects.get(id = pk)
			serializer = self.serializer_class(event)
			data = dict(serializer.data)
			if request.user.is_staff:
				data['can_edit'] = True
			else:
				data['can_edit'] = False
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request,pk):
		try:
			event = Event.objects.filter(date__year=pk)
			serializer = self.serializer_class(event,many = True)
			data = dict()
			data['events'] = serializer.data
			if request.user.is_staff:
				data['can_add'] = True
			else:
				data['can_add'] = False
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def put(self,request,pk):
		try:
			event = Event.objects.get(id = pk)
			if request.user.is_staff == False:
				return Response({"status" : False ,"data" : {}, "message" : "Sorry, only admin can edit this page"}, status=status.HTTP_200_OK)
			serializer = self.serializer_class(instance = event, data = request.data, partial = True)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def delete(self,request,pk):
		try:
			event = Event.objects.get(id = pk)
			if request.user.is_staff == False:
				return Response({"status" : False ,"data" : {}, "message" : "Sorry, only admin can edit this page"}, status=status.HTTP_200_OK)
			event.delete()
			return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class EventListAPI(GenericAPIView):
	serializer_class = EventSerializer
	permission_classes = [permissions.IsAuthenticated,]
	queryset = Event.objects.all().order_by('-date')

	def get(self,request):
		try:
			event = self.get_queryset()
			serializer = self.serializer_class(event,many = True)
			data = dict()
			data['events'] = serializer.data
			if request.user.is_staff:
				data['can_add'] = True
			else:
				data['can_add'] = False
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request):
		try:
			if request.user.is_staff == False:
				return Response({"status" : False ,"data" : {}, "message" : "Sorry, only admin can edit this page"}, status=status.HTTP_200_OK)
			serializer = self.serializer_class(data = request.data)	
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			data = serializer.data
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class ChangePasswordView(GenericAPIView):
	permission_classes = [permissions.IsAuthenticated,]

	def post(self,request):
		try:
			old_password = request.data["old_password"]
			new_password = request.data["new_password"]
			if not request.user.check_password(old_password):
				return Response({"status" : False ,"data" : {"old_password": "wrong_password" }, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			request.user.set_password(new_password)
			request.user.save()
			return Response({"status" : True ,"data" : {"new_password": "success" }, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class ContentListAPI(GenericAPIView):
	serializer_class = ContentSerializer
	queryset = Content.objects.all()

	def get(self,request):
		try:
			content = self.get_queryset()
			serializer = self.serializer_class(content,many = True)
			data = dict()
			for i in serializer.data:
				data[i['title']] = i['details']
			founders = Founder.objects.all().order_by('city')
			founder_serializer = FounderSerializer(founders,many = True)
			data['founders'] = founder_serializer.data
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request):
		try:
			city = request.data["city"]
			society_member = SocietyMember.objects.filter(city__icontains = city)
			serializer = SocietyMemberSerializer(society_member,many = True)
			data = serializer.data
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except:
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class CommitteeMemberListAPI(GenericAPIView):
	serializer_class = CommitteeMemberSerializer
	queryset = CommitteeMember.objects.all()
	
	def get(self,request):
		try:
			committee_member = self.get_queryset()
			serializer = self.serializer_class(committee_member,many = True)
			data = serializer.data
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request):
		try:
			serializer = CommitteeMemberSerializer(data = request.data)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
				data = serializer.data
				return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
			return Response({"status" : False ,"data" : serializer.errors, "message" : "Failure"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class BlogListAPI(GenericAPIView):
	serializer_class = BlogSerializer
	queryset = Blog.objects.filter(is_active = True)
	permission_classes = [permissions.IsAuthenticated,]
	
	def get(self,request):
		try:
			blog = self.get_queryset().order_by('-updated_at')
			serializer = self.serializer_class(blog,many = True)
			data = serializer.data
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def post(self,request):
		try:
			data = request.data.dict()
			ad = request.data.get('is_advertisement', None)
			if ad:
				if type(ad) == str:
					if ad == "true":
						data['is_advertisement'] = True
					else:
						data['is_advertisement'] = False

			job = request.data.get('is_job', None)
			if job:
				if type(job) == str:
					if job == "true":
						data['is_job'] = True
					else:
						data['is_job'] = False
			user = request.user
			data['created_by'] = user
			serializer = BlogSerializer(data = data)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
				data = serializer.data
				return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
			return Response({"status" : False ,"data" : serializer.errors, "message" : "Failure"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		

class BlogAPI(GenericAPIView):
	serializer_class = BlogSerializer
	queryset = Blog.objects.all()
	permission_classes = [permissions.IsAuthenticated,]

	def get(self,request,pk):
		try:
			blog = Blog.objects.get(id = pk)
			serializer = self.serializer_class(blog)
			data = serializer.data
			return Response({"status" : True ,"data" : data, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def put(self,request,pk):
		try:
			blog = Blog.objects.get(id = pk)
			if request.user != blog.created_by:
				return Response({"status" : False ,"data" : {}, "message" : "Only creator can edit this blog"}, status=status.HTTP_400_BAD_REQUEST)
			serializer = self.serializer_class(instance = blog, data = request.data, partial = True)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
			return Response({"status" : True ,"data" : serializer.data, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	# def delete(self,request,pk):
	# 	try:
	# 		blog = Blog.objects.get(id = pk)
	# 		if request.user != blog.created_by:
	# 			return Response({"status" : False ,"data" : {}, "message" : "Only creator can delete this blog"}, status=status.HTTP_400_BAD_REQUEST)
	# 		blog.delete()
	# 		return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
	# 	except Exception as e:
	# 		return Response({"status" : False ,"data" : {}, "message" : f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class ForgotPasswordAPI(GenericAPIView):
	serializer_class = ForgotPasswordSerializer
	
	def post(self,request):
		try:
			email = request.data['email']
			user = User.objects.get(email = email)
			if not user.email_id:
				user.email_id = user.email
				user.save()
			password = email[:4]+str(random.randint(1000,9999))
			data ={'email_body': f"Your password has been reset.\nUsername: {user.username}\nPassword: {password}", 'email_subject': "Password Reset",'to_email':user.email_id}
			util.send_email(data)
			user.set_password(password)
			user.save()
			return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		

class UpdateEmailAPI(GenericAPIView):
	permission_classes = [permissions.IsAuthenticated,]
	
	def post(self,request):
		try:
			email = request.data['email']
			user = User.objects.get(email = email)
			print(user.related_family, request.user.related_family, request.user.related_family != user.related_family)
			if request.user.is_staff == False and request.user.related_family != user.related_family:
				return Response({"status" : False ,"data" : {}, "message" : "You are not authorized to update this email"}, status=status.HTTP_400_BAD_REQUEST)
			data ={'email_body': f"Your email has been updated by {request.user.email}.\nOld Username: {user.email}", 'email_subject': "Email Updated",'to_email':user.email}
			util.send_email(data)
			user.email = request.data['new_email']
			user.save()
			return Response({"status" : True ,"data" : {}, "message" : "Success"}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"status" : False ,"data" : {}, "message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataAPI(GenericAPIView):

	def get(self,request):
		users = User.objects.all()
		for user in users:
			user.email_id = user.email
			user.username = user.email
			user.save()
		return Response({"status" : True, "message" : 'Success'},status=status.HTTP_200_OK)