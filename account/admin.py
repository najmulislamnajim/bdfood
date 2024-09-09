from django.contrib import admin
from .models import User,Restaurant,OneTimePassword

# Register your models here.
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(OneTimePassword)
