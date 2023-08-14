from rest_framework import serializers
from .models import User, Village, Family, OccupationAddress, Event, Content, SocietyMember, Founder, CommitteeMember, Blog

import re
email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

class RegisterSerializer(serializers.ModelSerializer):
	password=serializers.CharField(max_length=32,min_length=8,write_only = True)
	
	class Meta:
		model = User
		fields = ['first_name','last_name','relation','country','city','email','password','phone','dob','education','occupation','gender','blood_group','maritial_status','village','profile_pic','shakha','in_laws_village','in_laws_shakha']
		#exclude = ['is_active','is_staff','is_superuser','groups','user_permissions','last_login','date_joined']

	def validate(self,attrs):
		email = attrs.get('email',' ')

		if not email_pattern.match(email):
			raise serializers.ValidationError('Please enter a valid email!')
		return attrs
		
	def create(self,validated_data):
            #validated_data['is_active'] = False
            return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=32,min_length=8,write_only = True)
    
    class Meta:
        model = User
        fields = ['email','password']
	
class MemberSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = '__all__'

class VillageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Village
		fields = '__all__'

class FamilySerializer(serializers.ModelSerializer):
	village = VillageSerializer()
	class Meta:
		model = Family
		fields = '__all__'

class OccupationAddressSerializer(serializers.ModelSerializer):
	class Meta:
		model =  OccupationAddress
		fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model =  Event
		fields = '__all__'

class ContentSerializer(serializers.ModelSerializer):
	class Meta:
		model =  Content
		fields = '__all__'

class SocietyMemberSerializer(serializers.ModelSerializer):
	class Meta:
		model =  SocietyMember
		fields = '__all__'

class FounderSerializer(serializers.ModelSerializer):
	class Meta:
		model =  Founder
		fields = '__all__'

class UpdatedMemberSerializer(serializers.ModelSerializer):
	home_address = serializers.SerializerMethodField(read_only=True)
	village_address = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = User
		fields = ["email",
            "is_superuser",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
            "phone",
            "relation",
            "country",
            "city",
            "dob",
            "education",
            "occupation",
            "village",
			"shakha",
            "gender",
            "blood_group",
            "maritial_status",
            "in_laws_village",
			"in_laws_shakha",
            "profile_pic",
	    	"related_family",
	    	"home_address",
		    "village_address"
			]
		
	def get_home_address(self,obj):
		family = Family.objects.get(id=obj.related_family.id)
		serializer = FamilySerializer(family)
		return serializer.data['home_address']
	
	def get_village_address(self,obj):
		family = Family.objects.get(id=obj.related_family.id)
		serializer = FamilySerializer(family)
		return serializer.data['village_address']

class CommitteeMemberSerializer(serializers.ModelSerializer):
	class Meta:
		model = CommitteeMember
		fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
	class Meta:
		model = Blog
		fields = '__all__'

class ForgotPasswordSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['email']