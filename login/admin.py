from django.contrib import admin
from .models import serverSheet, userInfo,shiftAllotment,screenShot,balanceHistory

# Register your models here.

admin.site.register((userInfo,shiftAllotment,serverSheet,screenShot,balanceHistory))