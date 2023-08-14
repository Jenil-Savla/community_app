from django.contrib import admin
from .models import User, Village, Family, OccupationAddress, Event, Content, SocietyMember, Founder, CommitteeMember, Blog

# Register your models here.
admin.site.register(User)
admin.site.register(Village)
admin.site.register(Family)
admin.site.register(OccupationAddress)
admin.site.register(Event)
admin.site.register(Content)
admin.site.register(SocietyMember)
admin.site.register(Founder)
admin.site.register(CommitteeMember)
admin.site.register(Blog)