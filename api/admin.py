from django.contrib import admin
from .models import User, Village, Family, OccupationAddress

# Register your models here.
admin.site.register(User)
admin.site.register(Village)
admin.site.register(Family)
admin.site.register(OccupationAddress)