from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
from .models import userInfo,shiftAllotment,serverSheet,screenShot,balanceHistory
from .forms import userForm,shiftAllotmentForm,screenShotForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
import json
from datetime import datetime,timedelta
import schedule

  

# defining function 

 


# to update and insert the main sheet/model that is serverSheet
def serverSheetUpdate(work,serverName,date,shiftTime,userName,startingCount='',endingCount='',isghosted="yes",isbonus="",commentText='',classModel=serverSheet):
    # getting team name 
    teamNameQuery=userInfo.objects.filter(userName=userName).values('teamName').first()
    teamName=teamNameQuery['teamName']

    # making the slug 
    slug=f"{serverName}_{date}_{shiftTime}_{userName}"
    
    # making the approval 
    approval='yes'

    # to insert half data after allotment 
    if work=="insert":
        serverSheet=classModel(serverName=serverName,date=date,shiftTime=shiftTime,userName=userName,teamName=teamName,slug=slug)
        serverSheet.save()
    
    # to update data in already alloted users 
    elif work == "update":
        serverSheet=classModel.objects.filter(date=date,serverName=serverName,shiftTime=shiftTime,userName=userName).update(startingCount=startingCount,endingCount=endingCount,isbonus=isbonus,isghosted=isghosted,teamName=teamName,commentText=commentText,approval=approval,slug=slug,timestamp=datetime.now())


# to replace the shift from one to another 
def serverSheetReplace(serverName,date,shiftTime,userName,replacedUserName,classModel=serverSheet):
    # getting the team name of the replaced user 
    teamNameQuery=userInfo.objects.filter(userName=replacedUserName).values('teamName').first()
    teamName=teamNameQuery['teamName']


    # making the slug 
    slug=f"{serverName}_{date}_{shiftTime}_{userName}"
    
    # to replace a shift 
    serverSheet=classModel.objects.filter(date=date,serverName=serverName,shiftTime=shiftTime,userName=userName).update(userName=replacedUserName,teamName=teamName,slug=slug)


# to remove all the bonus 
def splitLst(listofshifttime):
    for i in listofshifttime:
        i1=i.split('$')[0]
        ind=listofshifttime.index(i)
        listofshifttime[ind]=i1
    return listofshifttime

# shiftFromLast3Days=serverSheet.objects.filter(balanceCheck="no",isghosted="yes",timestamp__gte=datetime.now()-timedelta(days=3))
# print(shiftFromLast3Days)

# to update the weekBalance of balanceHistory 
def updateWeekBalance(userName):
    query=balanceHistory.objects.filter(userName=userName).values('weekNormal','weekBonus',"weekGhosted")
    # Normal=(balanceHistory.objects.filter(userName=userName).values_list('weekNormal',flat=True))
    # Bonus=(list(balanceHistory.objects.filter(userName=userName).values_list('weekBonus',flat=True)))
    # Ghosted=(list(balanceHistory.objects.filter(userName=userName).values_list('weekGhosted',flat=True)))
    print("------------------------------------",query)
    # query=int(query[0]["weekNormal"])
    # print("------------------------------------",(int(query[0]["weekNormal"])))
    try:
        Normal=int(query[0]["weekNormal"]) or 0
        Bonus=int(query[0]["weekBonus"])or 0
        Ghosted=int(query[0]["weekGhosted"]) or 0
    except Exception as e:
        print(e)
    # print("------------------------------------",type(Normal))
    weekBalance=(Normal+Bonus)-Ghosted
    balanceHistory.objects.filter(userName=userName).update(weekBalance=weekBalance)

# updateWeekBalance('dhruv')


# to update balance of every user after 24hours if ghosting is done
def updateGhostingBalance():
    # datex = datetime.now().strftime("%Y-%m-%d")

    shiftFromLast3Days=serverSheet.objects.filter(balanceCheck="no",isghosted="yes",timestamp__gte=datetime.now()-timedelta(days=1,hours=12)).values_list('slug',flat=True)
    print("-------------+==============",shiftFromLast3Days)

    if len(shiftFromLast3Days)!=0:
        for i in shiftFromLast3Days:    
            # print("---------------++---------------------",i)
            serverSheet.objects.filter(slug=i).update(balanceCheck="yes")
            """
            morecode to write from here
            """
            slugSplit=i.split('_')
            serverName=slugSplit[0]
            serverDate=slugSplit[1]
            shiftTime=slugSplit[2]
            userName=slugSplit[3]

                # getting server data from JSON file 
            with open("login/moneyPerShift.json",'r') as st:
                moneyDict=json.load(st)

            if len(balanceHistory.objects.filter(userName=userName))==0:
                ghosted=moneyDict[serverName]["ghosted"]
                newbalance=balanceHistory(userName=userName,weekNormal=0,weekBonus=0,weekGhosted=ghosted,checkerUsername="yes")
                newbalance.save()
            else:
                weekGhosted=list(balanceHistory.objects.filter(userName=userName).values_list('weekGhosted',flat=True))
                ghosted=moneyDict[serverName]["ghosted"]+int(weekGhosted[0])
                replaceBalance=balanceHistory.objects.filter(userName=userName).update(weekGhosted=ghosted,checkerUsername="notDefinedByDhruv")

            updateWeekBalance(userName)

    else:
        pass

# schedule.every().hour.do(updateGhostingBalance)
print("-=-=-=-=-=","schedules")
# schedule.every(10).seconds.do(updateGhostingBalance)
updateGhostingBalance()



def updateBalance(serverDate,shiftTime,serverName,userName):
    # getting server data from JSON file 
    with open("login/moneyPerShift.json",'r') as st:
        moneyDict=json.load(st)

    if (serverSheet.objects.filter(date=serverDate,shiftTime=shiftTime,userName=userName,serverName=serverName).values_list("balanceCheck",flat=True))[0] == "no":
        serverSheet.objects.filter(date=serverDate,shiftTime=shiftTime,userName=userName,serverName=serverName).update(balanceCheck='yes')
        if len(balanceHistory.objects.filter(userName=userName))==0:
            normal=len(serverSheet.objects.filter(date=serverDate,shiftTime=shiftTime,serverName=serverName,userName=userName,isbonus="no",isghosted="no"))*moneyDict[serverName]["normal"]
            bonus=len(serverSheet.objects.filter(date=serverDate,shiftTime=shiftTime,serverName=serverName,userName=userName,isbonus="yes",isghosted="no"))*moneyDict[serverName]["bonus"]
            ghosted=0
            newbalance=balanceHistory(userName=userName,lastPaymentDate="1st week",weekNormal=normal,weekBonus=bonus,weekGhosted=ghosted,checkerUsername="yes",commentText="1st week checked")
            newbalance.save()
        else:
            weekNormal=list(balanceHistory.objects.filter(userName=userName).values_list('weekNormal',flat=True))
            weekBonus=list(balanceHistory.objects.filter(userName=userName).values_list('weekBonus',flat=True))
            normal=len(serverSheet.objects.filter(date=serverDate,shiftTime=shiftTime,serverName=serverName,userName=userName,isbonus="no",isghosted="no"))*moneyDict[serverName]["normal"]+int(weekNormal[0])
            bonus=len(serverSheet.objects.filter(date=serverDate,shiftTime=shiftTime,serverName=serverName,userName=userName,isbonus="yes",isghosted="no"))*moneyDict[serverName]["bonus"]+int(weekBonus[0])
            
            
            replaceBalance=balanceHistory.objects.filter(userName=userName).update(weekNormal=normal,weekBonus=bonus,checkerUsername="notDefinedByDhruv")

    updateWeekBalance(userName)


# print("------------------------------------------------",loggedInUsername)
# updateBalance("2022-08-01","04:00-08:00","money shark","dhruv")

# Create your views here.

def home(request):
    return render(request,'login/home.html')

def signup(request):
    submit=False
    if request.method=="POST":
        form = userForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            username=form.cleaned_data['userName']
            pass1=form.cleaned_data['pass1']
            pass2=form.cleaned_data['pass2']

            # check for errorneous input
            if len(username)<10:
                messages.warning(request, " Your user name must be bigger then 10 characters")
                return redirect('signup')

            if not username.isalnum():
                messages.warning(request, " User name should only contain letters and numbers")
                return redirect('signup')

            if  pass1!=pass2:
                messages.warning(request, " Passwords do not match")
                return redirect('signup')
            
            form.save()
            messages.success(request,"You are succesfully signed up")

            #creating user

            myuser=User.objects.create_user((form.cleaned_data['userName']),(form.cleaned_data['email']),(form.cleaned_data['pass1']))
            myuser.save()
            return HttpResponseRedirect('/signup?submit=True')
    
    else:
        form=userForm
        if submit in request.GET:
            submit=True
            messages.success(request,"Log in with your account to move further")

    return render(request,'login/signup.html',{'form':form,'submit':submit})

def handlelogin(request):
    if request.method =="POST":
        userName = request.POST.get('userName','')
        password = request.POST.get("pass","")
        user= authenticate(username=userName,password=password)

        if user is not None:
            login(request,user)
            messages.success(request,"You have succesfully Logged in")
            return redirect('home')
        else:
            messages.warning(request,"PLease try again with right credentials")
            return redirect('/login')


    return render(request,'login/login.html')

def handlelogout(request):
    logout(request)
    messages.success(request,"You have succesfully Logged out")
    return redirect('home')

def allotment(request):

    # getting server data from JSON file 
    with open("login/shiftTime.json",'r') as st:
        serverDictFromJson=json.load(st)
        # server list 
        serverLst=list(serverDictFromJson.keys())


    if request.method=="POST":
        date=request.POST.get('date')
        serverName=request.POST.get('serverName')
        shiftTime=request.POST.get('shiftTime')
        userName=request.user
        print(date,serverName,shiftTime,userName)

        # checks------- for the variable to be stored 

        # to check if all the variables are not null 
        if (date=="" or serverName=="" or shiftTime=="" or userName==""):
            messages.warning(request,f"Please fill all the information")
            return redirect('allotment')
        
        # to check the server is right 
        if serverName in serverLst:
            pass
        else:
            messages.warning(request,"Please select the right server")
            return redirect('allotment')

        # to check it the shift time is legit 
        shiftTimeLst=serverDictFromJson[f'{serverName}']
        shiftTimeLst=splitLst(shiftTimeLst)
        if shiftTime in shiftTimeLst:
            pass
        else:
            messages.warning(request,f"Please fill all the right time in the right format.It did't match our database")
            return redirect('allotment')

        try:
            # all shift will be stored in shift allotment table 
            shiftAllotmentdb=shiftAllotment(userName=userName,date=date,serverName=serverName,shiftTime=shiftTime)
            shiftAllotmentdb.save()

            # only the top 3 shift will be stored in serverSheet
            # serverSheetUpdate('insert',serverName,date,shiftTime,userName)

        except Exception as e:
            messages.warning(request,f"An error occured = {e}")


        # only the top 3 shift will be stored in serverSheet
        # serverSheetUpdate('insert',serverName,date,shiftTime,userName)
        # getting server data from JSON file 
        with open("login/shiftTime.json",'r') as st:
            serverDictFromJson=json.load(st)
            updatedShiftTime=splitLst(serverDictFromJson[f'{serverName}'])

        # if shiftAllotment.objects.filter(date=date,serverName=serverName,shiftTime=shiftTime)
        print(len(serverSheet.objects.filter(date=date,serverName=serverName,shiftTime=shiftTime)))
        if (len(serverSheet.objects.filter(date=date,serverName=serverName,shiftTime=shiftTime))) <= 2:
            serverSheetUpdate('insert',serverName,date,shiftTime,userName)
            messages.success(request,"Your form is succesfully submitted")
        else:
            messages.warning(request,f"Sorry,but the shifts are full for {date} time -{shiftTime} in {serverName}")
            print("====================================================")
        
    

        return render(request,'login/allotment.html',{"serverLst":serverLst})
    else:
        return render(request,'login/allotment.html',{"serverLst":serverLst})

    return render(request,'login/allotment.html')
    

def shiftSheet(request):
    # getting server data from JSON file 
    with open("login/shiftTime.json",'r') as st:
        serverDictFromJson=json.load(st)
        # server list 
        serverLst=list(serverDictFromJson.keys())

    if request.method=="POST":

        shiftDate=request.POST.get('date')
        serverName=request.POST.get('serverName')

        print(shiftDate,serverName)
        # checks------- for the variable to be stored 
        # to check if all the variables are not null 
        if (shiftDate=="" or serverName==""):
            messages.warning(request,f"Please fill all the information")
            return redirect('shiftSheet')
        # to check the server is right 
        if serverName in serverLst:
            pass
        else:
            messages.warning(request,"Please select the right server")
            return redirect('shiftSheet')


        #getting and setting the right query

        #filtering the query for date and server name
        for i in range(len(serverDictFromJson[f'{serverName}'])):
            updatedShiftTime=splitLst(serverDictFromJson[f'{serverName}'])
            if i == 0:    
                querySet1=serverSheet.objects.filter(date=shiftDate,serverName=serverName,shiftTime=updatedShiftTime[i])
                querySet2=querySet1
            else:
                querySet1=serverSheet.objects.filter(date=shiftDate,serverName=serverName,shiftTime=updatedShiftTime[i])
                querySet2=querySet2|querySet1 
             
        # to store data in serverSheet

        return render(request,'login/shiftSheet.html',{"serverLst":serverLst,"alldata":querySet2})
    else:
        return render(request,'login/shiftSheet.html',{"serverLst":serverLst})

    return render(request,'login/shiftSheet.html')    

def replacement(request):
    # getting server data from JSON file 
    with open("login/shiftTime.json",'r') as st:
        serverDictFromJson=json.load(st)
        # server list 
        serverLst=list(serverDictFromJson.keys())

    usernames=userInfo.objects.all().order_by('teamName').values('userName')
    userNameLst=[]
    # print(usernames)
    for i in usernames:
        userNameLst.append(i['userName'])
    
    if request.method=="POST":
        shiftDate=request.POST.get('date')
        serverName=request.POST.get('serverName')
        shiftTime=request.POST.get('shiftTime')
        receiverUserName=request.POST.get('receiverUserName')

        # getting the username of the logged in user 
        userName=request.user

        print(shiftDate,serverName,shiftTime,receiverUserName)

        # checks------- for the variable to be stored 

        # to check if all the variables are not null 
        if (shiftDate=="" or serverName=="" or shiftTime=="" or receiverUserName==""):
            messages.warning(request,f"Please fill all the information")
            return redirect('shiftSheet')

        # to check the server is right 
        if serverName in serverLst:
            pass
        else:
            messages.warning(request,"Please select the right server")
            return redirect('replacement')

        # to check the user is right or not 
        if receiverUserName in userNameLst:
            pass
        else:
            messages.warning(request,"Please type the right user name")
            return redirect('replacement')

        # to check it the shift time is legit 
        shiftTimeLst=serverDictFromJson[f'{serverName}']
        shiftTimeLst=splitLst(shiftTimeLst)
        if shiftTime in shiftTimeLst:
            pass
        else:
            messages.warning(request,f"Please fill  the right time in the right format.It did't match our database")
            return redirect('allotment')

        # to check if the person have a shift or not 
        shiftcheck=serverSheet.objects.filter(date=shiftDate,serverName=serverName,shiftTime=shiftTime,userName=userName)
        if not shiftcheck:
            messages.warning(request,f"You don't have any shift on {shiftDate} - {shiftTime} in {serverName}")
            return redirect('replacement')
        else:
            print('shift==============')


        # to replace the shift we need to run the replacement function
        try: 
            serverSheetReplace(serverName,shiftDate,shiftTime,userName,receiverUserName)
            messages.success(request,f"Succesfully replaced {userName} to {receiverUserName}.Check the sheets to confirm ")
        except Exception as e:
            messages.warning(request,f"An error occured {e}")
        
        return redirect('replacement')
        

    return render(request,'login/replacement.html',{"serverLst":serverLst,"usernames":userNameLst})

def countsub(request):  


    # getting server data from JSON file 
    with open("login/shiftTime.json",'r') as st:
        serverDictFromJson=json.load(st)
        # server list 
        serverLst=list(serverDictFromJson.keys())

    # getting the post request 
    if request.method=="POST":
        shiftDate=request.POST.get('date')
        serverName=request.POST.get('serverName')
        shiftTime=request.POST.get('shiftTime')
        userName=request.user
        startingCount=request.POST.get('startingCount')
        endingCount=request.POST.get('endingCount')
        isghosted="no"
        commentText=request.POST.get('commentText')
    
        # getting the result if the field is bonus or not
        shiftTimeLst=serverDictFromJson[f'{serverName}']
        for i in shiftTimeLst:
            try:
                i0=i.split('$')[0]
                i1=i.split('$')[1]
            except:
                pass
            if i0==shiftTime:
                if len(i.split('$'))==2:
                    if i1=='bonus':
                        isbonus="yes"
                        break
                else:
                    isbonus="no"
            else:
                pass



        # checks------- for the variable to be stored 

        # to check if all the variables are not null 
        if (shiftDate=="" or serverName=="" or shiftTime=="" or startingCount=="" or endingCount==""):
            messages.warning(request,f"Please fill all the information")
            return redirect('countsub')

        # to check the server is right 
        if serverName in serverLst:
            pass
        else:
            messages.warning(request,"Please select the right server")
            return redirect('countsub')


        # to check it the shift time is legit 
        shiftTimeLst=serverDictFromJson[f'{serverName}']
        shiftTimeLst=splitLst(shiftTimeLst)
        if shiftTime in shiftTimeLst:
            pass
        else:
            messages.warning(request,f"Please fill  the right time in the right format.It did't match our database")
            return redirect('countsub')

        # to check if the person have a shift or not 
        shiftcheck=serverSheet.objects.filter(date=shiftDate,serverName=serverName,shiftTime=shiftTime,userName=userName)
        if not shiftcheck:
            messages.warning(request,f"You don't have any shift on {shiftDate} - {shiftTime} in {serverName}")
            return redirect('countsub')
        else:
            print('shift==============')

        # getting the screenshot from form 
        form = screenShotForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.instance.userName=request.user
            form.instance.date=shiftDate
            form.instance.serverName=serverName
            form.instance.shiftTime=shiftTime
            form.save() 

        try:
            serverSheetUpdate('update',serverName,shiftDate,shiftTime,userName,startingCount,endingCount,isghosted,isbonus, commentText)
            messages.success(request,f"Your count for {shiftDate} - {shiftTime} in {serverName} is succesfully submitted")
            ss1=screenShot.objects.filter(date=shiftDate,serverName=serverName,shiftTime=shiftTime,userName=userName).values('startingCountScreenShot')
            ss2=screenShot.objects.filter(date=shiftDate,serverName=serverName,shiftTime=shiftTime,userName=userName).values('endingCountScreenShot')
            serverSheet.objects.filter(date=shiftDate,serverName=serverName,shiftTime=shiftTime,userName=userName).update(startingCountScreenShot=ss1,endingCountScreenShot=ss2)
        
        except Exception as e:
            messages.warning(request,f"An error occured {e}")

        updateBalance(shiftDate,shiftTime,serverName,userName)
        
        return redirect('countsub')
    else:
       form=screenShotForm
    return render(request,'login/countSubmition.html',{'serverLst':serverLst,'form':form})
        

def allmembers(request):
    memberquery=userInfo.objects.all().order_by('teamName').values('userName','email','teamName','profilePic')
    return render(request,'login/allmembers.html',{"allmember":memberquery})

def approval(request):
    # getting server data from JSON file 
    with open("login/shiftTime.json",'r') as st:
        serverDictFromJson=json.load(st)
        # server list 
        serverLst=list(serverDictFromJson.keys())

    # getting the post request 
    if request.method=="POST":
        shiftDate=request.POST.get('date')
        serverName=request.POST.get('serverName')
        print(shiftDate,serverName)


        # checks------- for the variable to be stored 

        # to check if all the variables are not null 
        if (shiftDate=="" or serverName==""):
            messages.warning(request,f"Please fill all the information")
            return redirect('approval')

        # to check the server is right 
        if serverName in serverLst:
            pass
        else:
            messages.warning(request,"Please select the right server")
            return redirect('approval')

        # isApproved=serverSheet.objects.filter(date=shiftDate,serverName=serverName).values('userName','startingCount','endingCount','isbonus','commentText','startingCountScreenShot','endingCountScreenShot','slug')
        obj=serverSheet.objects.filter(date=shiftDate,serverName=serverName,approval='yes').values('userName','startingCount','endingCount','isbonus','commentText','startingCountScreenShot','endingCountScreenShot','slug')
        return render(request,'login/approval.html',{"serverLst":serverLst,'queryset':obj})

    return render(request,'login/approval.html',{"serverLst":serverLst})
        
def disapproval(request,slug):
    slugSplit=slug.split('_')
    print('==============================',slugSplit)
    serverSheet.objects.filter(serverName=slugSplit[0],date=slugSplit[1],shiftTime=slugSplit[2],userName=slugSplit[3]).update(approval='no')
    return redirect('approval')

def userpanel(request):
    return render(request,'login/userpanel.html')

def usershiftcheck(request):
    userName=request.user
    querySet=reversed(serverSheet.objects.filter(userName=userName).order_by('date'))

    return render(request,'login/usershiftcheck.html',{'alldata':querySet})


def teamwisesheet(request):
    return render(request,'login/teamwisesheet.html')

def staffpanel(request):
    return render(request,'login/staffpanel.html')

def balance(request):
    return render(request,'login/balance.html')

