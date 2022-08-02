from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from requests import request
# Create your models here.


class userInfo(models.Model):
    sno=models.AutoField
    userName=models.CharField(max_length=70)
    email=models.CharField(max_length=50)
    phone=models.BigIntegerField(default=0)
    teamName=models.CharField(max_length=20)
    dateOfBirth=models.CharField(max_length=30)
    profilePic=models.ImageField(upload_to="profilePic")
    idProof=models.ImageField(upload_to="idProof")
    pass1=models.CharField(max_length=40)
    pass2=models.CharField(max_length=40)

    def __str__(self):
        return self.userName

class shiftAllotment(models.Model):
    sno=models.AutoField(primary_key=True)
    userName=models.CharField(max_length=50)
    date=models.CharField(max_length=50)
    serverName=models.CharField(max_length=15)
    shiftTime=models.CharField(max_length=50)
    timestamp=models.DateTimeField(default=now)

    def __str__(self):
        return self.userName+" "+self.serverName+" "+self.shiftTime

class serverSheet(models.Model):
    sno=models.AutoField(primary_key=True) 
    serverName=models.CharField(max_length=15)
    date=models.CharField(max_length=50)
    shiftTime=models.CharField(max_length=50)
    userName=models.CharField(max_length=50)
    startingCount=models.IntegerField(blank=True,editable=True,null=True)
    endingCount=models.IntegerField(blank=True,editable=True,null=True)
    teamName=models.CharField(max_length=50,blank=True,editable=True,null=True)
    isghosted=models.CharField(max_length=50,blank=True,editable=True,null=True,default="yes")
    isbonus=models.CharField(max_length=50,blank=True,editable=True,null=True)
    commentText=models.CharField(max_length=500,default='')
    approval=models.CharField(max_length=10,blank=True,editable=True,null=True,default='')
    balanceCheck=models.CharField(max_length=10,blank=True,editable=True,null=True,default='no')
    startingCountScreenShot=models.ImageField(upload_to="startingScreenShot",null=True,default="")
    endingCountScreenShot=models.ImageField(upload_to="endingingScreenShot",null=True,default="")
    slug=models.CharField(max_length=120,default="",blank=True,editable=True,null=True)
    timestamp=models.DateTimeField(default=now)

    def __str__(self):
        return self.userName+" "+self.serverName+" "+self.shiftTime+" "+self.date

# to et the screen shot 
class screenShot(models.Model):
    sno=models.AutoField(primary_key=True)
    userName=models.CharField(max_length=50)
    date=models.CharField(max_length=50)
    serverName=models.CharField(max_length=15)
    shiftTime=models.CharField(max_length=50)
    startingCountScreenShot=models.ImageField(upload_to="startingScreenShot",null=True,default="")
    endingCountScreenShot=models.ImageField(upload_to="endingingScreenShot",null=True,default="")
    timestamp=models.DateTimeField(default=now)

    def __str__(self):
        return self.userName+" "+self.serverName+" "+self.shiftTime

# payment history
class balanceHistory(models.Model):
    sno=models.AutoField(primary_key=True)
    userName=models.CharField(max_length=40)
    lastPaymentDate=models.CharField(max_length=50)
    weekNormal=models.CharField(max_length=15)
    weekBonus=models.CharField(max_length=15)
    weekGhosted=models.CharField(max_length=15)
    weekBalance=models.CharField(max_length=15)
    checkerUsername=models.CharField(max_length=50)
    commentText=models.CharField(max_length=500,default='')
    timestamp=models.DateTimeField(default=now)


    def __str__(self):
        return self.userName