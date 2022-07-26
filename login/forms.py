from django import forms
from django.forms import ModelForm
from numpy import short
from .models import serverSheet, userInfo,shiftAllotment,screenShot


#creating a form
class userForm(ModelForm):
    class Meta:
        model=userInfo
        fields=('userName','email','phone','teamName','dateOfBirth','profilePic','idProof','pass1','pass2')
        # fields='__all__'
        # exclude=['sno']
        
        widgets={
            'userName':forms.TextInput(attrs={'class':"form-control",'placeholder':"Enter Your User Name"}),
            'email':forms.TextInput(attrs={'class':"form-control",'placeholder':'Enter your email'}),
            'phone':forms.TextInput(attrs={'class':"form-control",'placeholder':'Enter your phone number'}),
            'teamName':forms.TextInput(attrs={'class':"form-control",'placeholder':'Enter your Team Name'}),
            'dateOfBirth':forms.TextInput(attrs={'class':"form-control",'placeholder':'Enter your Date of birth'}),
            'pass1':forms.TextInput(attrs={'class':"form-control",'placeholder':'Enter your password'}),
            'pass2':forms.TextInput(attrs={'class':"form-control",'placeholder':'Enter your password again'}),
        }


class shiftAllotmentForm(forms.Form):
    date=forms.CharField(label='Type your date in dd-mm-yyyy format', max_length=100,)
    serverName=forms.CharField(label='Type your server name', max_length=100)
    shiftTime=forms.CharField(label='Type your shift time in hh:mm - hh:mm', max_length=100)

# to get the starting count and ending count screen shot
class screenShotForm(ModelForm):
    class Meta:
        model=screenShot
        # fields=('__all__')
        exclude=['date','userName','serverName','shiftTime','timestamp']




