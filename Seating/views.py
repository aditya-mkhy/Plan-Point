from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import logout , login
from Seating.models import MyUser, Contact, Rooms, RoomsRows, Batch, Stundets, Classes, AttendUser, Subjects, DateOfClass, Attendance
from Seating.sp_algorithm import SpMethod4, SpMethod3
from Seating.validator import Validator
from django.views.decorators.csrf import csrf_exempt


from random import choice
import uuid
from django.contrib import messages
from Seating.sendEmail import  Email
from Seating.mysetting import dafultname
import time
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http.request import HttpRequest
import os
from django.http import JsonResponse
import random
import datetime
import time


send_email = Email()
from cryptography.fernet import Fernet

mail=Email()

# Create your views here.

seating_plan = {
    "rooms" : [],
    "batch" : {},
    "time" : None,
    "id" : None,
    "name" : None,
    "date" : None,
    "shift" : None,
}


planning_algorith = [
    "SP_Model 4.8",
    "SP_Model 3.3",
]

seating_plan_is_active = False

signupuser_pages_token = []

seating_plan_is_active = False

signup_data = {}

key_enc = settings.ENC_KEY

# Create your views here.

def decrypt(key, data:bytes) -> str:
    f = Fernet(key)
    decrypted = f.decrypt(data)
    return decrypted.decode()

def encrypt(key, data:str) -> str:
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()


def goal(attendent: int, perct:int = 75) -> int:
    need = (perct/100) * attendent
    # if need is 7.5  then it is not possibe to atten half class so it roundoff to next digit
    int_part, frac_part = str(need).split(".")
    int_part = int(int_part)
    frac_part = int(frac_part[0])

    if frac_part > 0:
        int_part += 1

    return int_part

def goal_seek(total: int, mine: int):
    goal_attend = goal(total, 75)

    need = mine - goal_attend
    return need

def get_num_days(total:int, mine: int):
    days = 0
    while True:
        need = goal_seek(total, mine)
        if need >= 0:
            break

        total += 1
        mine += 1
        days += 1

    return days

def get_user_cont(request):
    value = request.COOKIES.get("slideroff")
    context = {"username" : request.user.full_name, "level" : "User", "profile" : request.user.propath, "sidebarst": ""}
    if request.user.is_subadmin:
        context["Admin"] = True
        context["level"] = "Admin"

    if value != '1':
        context["sidebarst"] = "active"

    return context


def home(request):
    if request.user.is_anonymous:
        return redirect('/login')

    context = get_user_cont(request)

    return render(request , "home.html", context=context)

def contacts(request):
    context = {}


    if request.user.is_anonymous:
        value = request.COOKIES.get("slideroff")
        if value == '1':
            context["sidebarst"] = ""
        else:
            context["sidebarst"] = "active"
    else:
        context = get_user_cont(request)


    if request.method=="POST" :
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        desc=request.POST.get("desc")

        contact=Contact(name=name,email=email,phone=phone,desc=desc,date=datetime.datetime.today())
        contact.save()
        messages.success(request, 'Your Message has been sent!')

    if request.user.is_authenticated:
        data=MyUser.objects.filter(email = request.user.email  ).values()[0]
        context["user_name"]=data["full_name"]
        context["user_email"]=data["email"]
        context["phone_number"]=data["phone_no"]

    return render(request , "contacts.html" , context=context)


#____LOGIN________PAGE_______________________________
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('/')

    context={"video_file" : "video2.mp4"}
    if request.method=="POST" :
        ## Check if user has entrered correct credentials
        userName=request.POST.get("userName")
        password=request.POST.get("password")
        video_file=request.POST.get("prev_video")
        print("user==>",userName,"pass==>",password)
        context['video_file']=video_file
        user = authenticate(username=userName, password=password)
        if user is not None:
            # A backend authenticated the credentials
            #Checking If user is verified
            profile_obj = MyUser.objects.filter(email=userName).first()
            if not profile_obj.is_verified:
                context["prefix"]="Hey! "+str(profile_obj.full_name)+', '
                context["message"]='your email is not verified. Please verify your email first.'
                return render(request , "login.html" , context)

            login( request , user)
            return redirect('/')
        else:
            # No backend authenticated the credentials
            profile_obj = MyUser.objects.filter(email=userName).first()
            if not profile_obj:
                context["message"]="The username you entered doesn't belong to an account. Please check your username and try again."
            else:
                context["prefix"]="Sorry! "+str(profile_obj.full_name).split(' ')[0]+', '
                context["message"]="your password was incorrect. Please double-check your password."
            return render(request , "login.html" , context)

    return render(request , "login.html" , context)

def logout_user(request):
    logout(request)
    return redirect('/login')

def verified(request ,auth_token):
    print("auth_token==>",auth_token)
    try:
        profile_obj = MyUser.objects.filter(auth_token = auth_token).first()
        print(f"profile_obj===> {profile_obj}")
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/login')

            profile_obj.is_verified = True
            profile_obj.save()
            try:
                print('username=',profile_obj.email, 'password=]',profile_obj.password)
                user = authenticate(username=profile_obj.email, password=profile_obj.password)

                if user is not None:

                    login( request , user)
                    return redirect('/')
                else:
                    print("Error in Autohtentication8")

            except Exception as e:
                    print("Eoor==>",e)


            print(request, 'Your account has been verified.')
            return render(request , "verified.html" ,{'name': profile_obj.full_name})
        else:
            print("er56")
            return redirect('/error_page')

    except Exception as e:
        print(e)
        return redirect('/')


def error_page(request):
    return  render(request , 'error.html')

def passwordreset(request):
    email = request.GET.get('email','')
    context={"prev_video" : "video2.mp4"}
    if email != "":
        context["userid"]= email

    if request.method=="POST" :
        ## Check if user has entrered correct credentials--prev_video
        userid=request.POST.get("userid")
        prev_video=request.POST.get("prev_video")
        print("userid==>",userid)
        print("prev_video==>",prev_video)

        context["prev_video"]=prev_video

        if "@" in userid and '.' in userid:
            type="email"
        else:
            try:
                int(userid)
                type="number"
            except:
                type=None

        context["userid"]=userid
        send=False
        if type ==None:
            context["prefix"]="Please, "
            context["message"]="enter a valid Email or Phone number "

        elif type=="email":
            user=MyUser.objects.filter(email=userid).first()
            if user:
                context["prefix"]="Hi "+str(user.full_name).split(' ')[0]+', '
                context["message"]=f"We sent an email to {getHiddenEmail(userid)}  with a link to reset your account password."
                context["userid"]=""
                send=True
            else:
                context["prefix"]="Sorry! "
                context["message"]="We couldn't find an account with that email address."


        elif type=="number":
            if len(userid) == 10:

                user=MyUser.objects.filter(phone_no=userid).first()
                if user:
                    context["prefix"]="Hi "+str(user.full_name).split(' ')[0]+', '
                    context["message"]= f"We sent an email to {getHiddenEmail(user.email)}  with a link to reset your account password."
                    context["userid"]=""
                    send=True
                else:
                    context["prefix"]="Sorry! "
                    context["message"]="We couldn't find an account with that phone number."

            else:
                context["prefix"]="Please, "
                context["message"]="enter a valid Phone number. Entered Phone number is not valid"

        if send:
            auth_token =str(uuid.uuid4())+"-"+str(uuid.uuid4())+str(uuid.uuid4())

            subject = 'Reset password'
            loginlink=dafultname.myIP+"changepassword/login/"+auth_token
            resetlink=dafultname.myIP+"changepassword/reset/"+auth_token

            page=send_email.forgotPasswordPage(name=user.full_name ,loginlink=loginlink, resetlink=resetlink)

            status=send_email.send(to_addrs=user.email ,subject=subject ,HTMLmsg=page)



            if status:
                print("Email Sent")
                user.auth_token=auth_token
                user.auth_token_time=str(int(time.time()))
                user.save()
            else:
                print("Email not sent")
                return render(request , "error.html"  )

    return render(request , "forgot.html" , context=context )



#URL==>http://localhost/changepassword/reset/c1732210-af1b-435f-9637-1dd1461ed1ef
def changepassword(request ,action,auth_token):
    print("action====>",action)
    print("auth_token===>",auth_token)
    context={}

    if action =="reset" or action=="login":
        profile_obj = MyUser.objects.filter(auth_token = auth_token).first()
        if profile_obj:
            context["prefix"]="Hey! "+str(profile_obj.full_name).split(' ')[0]+', '

            tt=int(time.time())-int(profile_obj.auth_token_time)
            print("Time Taken====> ",tt)
            #link valid for 10 mintutes
            if tt > 600:
                context["message"]=context["prefix"]+" This token was only valid for 10 minutes."
                return render(request , "invalidToken.html" , context=context)

            if action=="reset":

                context["message"]="Please create a password that is at least 8 characters in length "
                if request.method=="POST" :
                    password1=request.POST.get("password1")
                    print("password1==>",password1)
                    password2=request.POST.get("password2")
                    print("password2==>",password2)

                    if password1 != password2:
                        context["message"]="Please make sure that both passwords match."
                        context["password1"]=password1
                        return render(request , "setpassword.html" , context=context)

                    try:
                        validate_password(password=password1, user=profile_obj)

                    except ValidationError as err:
                        print("Error==> ", err.messages)
                        msg = []
                        if len(err.messages) > 1:
                            msg = [" And ".join(err.messages)]
                        else:
                            msg = err.messages

                        context["message"] = msg
                        context["password1"] = password1
                        return render(request , "setpassword.html" , context=context)



                    #Reset Pasword
                    profile_obj.set_password(password2)
                    profile_obj.auth_token="Used"
                    profile_obj.save()

                    user = authenticate(username=profile_obj.email, password=password2)
                    login( request , user)

                    msg="Hi "+str(profile_obj.full_name)+', you have successfully reset the password for your account and signed in.'
                    messages.success(request, msg)
                    return redirect('/')



                return render(request , "setpassword.html" , context=context)

            elif action == "login":
                profile_obj.auth_token="Used"
                profile_obj.save()
                msg="Hi "+str(profile_obj.full_name)+', you have successfully login in via link.'
                login(request, profile_obj, backend=settings.AUTHENTICATION_BACKENDS[0])
                messages.success(request, msg)
                return redirect('/')

            else:
                context["message"]="Unknown Error"
                return render(request , "invalidToken.html" , context=context)

        else:
            context["message"]="Invalid Token"
            return render(request , "invalidToken.html" , context=context)
    else:
        context["message"]="Invalid Action"
        return render(request , "invalidToken.html" , context=context)


#function extra
def getHiddenEmail(email):
    email=email.split("@")
    return email[0][:4]+"*"*(26-(len(email[1])+8))+email[0][-2:]+"@"+email[1]



def rooms(request:HttpRequest):
    if request.user.is_anonymous:
        return redirect('/login')

    action = request.GET.get('action', '')

    context = get_user_cont(request)

    if action == "cmd":
        if not request.user.is_subadmin:
            return JsonResponse({"auth_Error": 1})


        roomid = int(request.GET.get("cmd"))
        status = request.GET.get("stat")
        if status == "1":
            print(f"rooms : {roomid} => is added in planning")
            seating_plan["rooms"].append(roomid)

        elif status == "0":
            print(f"rooms : {roomid} => is Remove in planning")
            try:
                seating_plan["rooms"].remove(roomid)
            except:
                print("rooms Value not in list")

        else:
            print("wrong status")

        data = {"stat" : "1"}
        return JsonResponse(data)


    roomsObj = Rooms.objects.all()
    print(f'seating_plan["rooms"]==> {seating_plan["rooms"]}')

    contxt_room_data = []
    for room in roomsObj:
        is_selected = 0
        if room.room_num in seating_plan["rooms"] and context["level"] == "Admin":
            is_selected = 1

        contxt_room_data.append([room.room_num, room.seats, is_selected])

    if action == "showroom":
        room_num = request.GET.get('roomnum', '')

        if room_num != "":
            print(f"room_num==> {room_num}")

            room_map_data = []
            room_obj = Rooms.objects.filter(room_num=room_num).first()
            if room_obj != None:
                gate_side = room_obj.gate
                room_disc = room_obj.dis

                all_rows_obj = RoomsRows.objects.filter(room_num=room_num)
                seat_count = 0
                map_data_room_number = room_num

                for row in all_rows_obj:
                    row_data = []

                    for desk in range(row.desks):
                        desk_data = []
                        for seat in range(row.capicity):
                            seat_count += 1
                            desk_data.append(seat_count)

                        row_data.append(desk_data)

                    room_map_data.append(row_data)

                if gate_side == "right":
                    room_map_data = room_map_data[::-1]

                context["room_map_data"] = room_map_data
                context["map_data_room_number"] = map_data_room_number
                context["scroll_page"] = "scroll_page"
                context["gateside"] = gate_side

    context["short_view_data"] = contxt_room_data

    context["room_selection_show"] = "room-selection-off"
    if seating_plan_is_active and context["level"] == "Admin":
        context["room_selection_show"] = "Yes"

    return render(request, "rooms.html", context=context)



def rooms_add(request:HttpRequest ):
    if request.user.is_anonymous:
        return redirect('/login')

    if not request.user.is_subadmin:
        return redirect("/rooms")

    context = get_user_cont(request)


    if request.method == "POST":
        room_num = request.POST.get("roomnum")
        gate_side = request.POST.get("gateside")
        info = request.POST.get("extrainfo")
        totalrow = request.POST.get("rowcount")

        row_data = {}
        total_seats = 0
        for row in range(int(totalrow)):
            desk_in_row = request.POST.get(f"deskinrow{row+1}")
            capi_in_row = request.POST.get(f"capofrow{row+1}")
            if desk_in_row != None and capi_in_row != None:
                row_data[row] = [desk_in_row, capi_in_row]
                total_seats += int(desk_in_row)* int(capi_in_row)


       



        roomObj = Rooms(room_num=room_num, seats=total_seats, gate=gate_side, dis=info)
        roomObj.save()

        for row in row_data:
            rowObj = RoomsRows(room_num=roomObj, row_num=row, desks=row_data[row][0], capicity=row_data[row][1])
            rowObj.save()

        return redirect(f"/rooms?action=showroom&roomnum={room_num}")


    return render(request , "addroom.html", context=context)


def add_batch(request:HttpRequest):
    if request.user.is_anonymous:
        return redirect('/login')

    if not request.user.is_subadmin:
        return redirect("/class")

    context = get_user_cont(request)


    if request.method == "POST":
        batch = request.POST.get("batchid", "").strip()
        course = request.POST.get("course", "").strip()
        total_records = request.POST.get("totalrecords", "").strip()
        semester = request.POST.get("semester", "").strip()

        records = {}
        for index in range(int(total_records)):
            index = index + 1
            roll_num = request.POST.get(f"onerollnum{index}").strip()
            name = request.POST.get(f"onestname{index}").strip()
            email = request.POST.get(f"onemail{index}").strip()

            if roll_num != None and roll_num != "":
                if name != None and name != "":
                    records[roll_num] = {"name": name, "email": email}
                else:
                    print(f"Please enter name of roolnumer==> {roll_num}")

        print(f"Batch===> {batch}")
        print(f"Course===> {course}")
        print(f"TotalRecord===> {total_records}")
        print(f"semester ==> {semester}")
        print(f"Records===> {records}")

        if batch != "" and course != "":
            batch_obj = Batch(bachid=batch, course=course, classname=semester)
            batch_obj.save()
            print("Bacth info is saved")

            for roll_num in records:
                studnt_obj = Stundets(rollnum=roll_num, name=records[roll_num]["name"], email=records[roll_num]["email"], bachid=batch_obj)
                studnt_obj.save()

            return redirect(f"/class?action=batch&batchid={batch}")


    return render(request, "addbatch.html", context=context)



def batch_class(request:HttpRequest):
    if request.user.is_anonymous:
        return redirect('/login')

    action = request.GET.get('action', '')

    context = get_user_cont(request)

    selected_batch = None

    if action == "cmd":
        if not request.user.is_subadmin:
            return JsonResponse({"auth_Error": 1})

        batchid = request.GET.get("cmd")
        status = request.GET.get("stat")
        if status == "1":
            print(f"Batch : {batchid} => is added in planning")
            batch_obj = Batch.objects.filter(bachid=batchid)[0]

            if batch_obj  != None:
                seating_plan["batch"][batch_obj.bachid] = f"{batch_obj.course} {batch_obj.classname}"
                data = {"stat" : "1"}

            else:
                return JsonResponse({"auth_Error": 1})

        elif status == "0":
            print(f"Batch : {batchid} => is Remove in planning")
            try:
                seating_plan["batch"].pop(batchid)
                data = {"stat" : "1"}
            except:
                data = {"stat" : "0"}

        else:
            data = {"stat" : "0"}


        return JsonResponse(data)


    if action == "batch":
        batchid = request.GET.get("batchid")
        student_data = Stundets.objects.filter(bachid=batchid).values_list("rollnum", "name", "email")
        student_data = list(student_data)

        if student_data != []:
            context["student_data"] = student_data
            selected_batch = batchid

    batch_obj = Batch.objects.all()
    batch_data = []

    for batch in batch_obj:
        strength = len(Stundets.objects.filter(bachid=batch).all())

        is_selected = 0
        if batch.bachid in seating_plan["batch"] and context["level"] == "Admin" and seating_plan_is_active:
            is_selected = 1

        batch_data.append([batch.course, batch.classname, batch.bachid, strength, is_selected])

        if selected_batch != None:
            if selected_batch == batch.bachid:
                context["student_batch_data"] = [batch.course ,batch.classname, batch.bachid, strength]

    context["batch_data"] = batch_data

    context["batch_selection"] = "batch-selection-off"
    if seating_plan_is_active:
        context["batch_selection"] = "batch-selection-on"


    # context["room_selection_show"] = "room-selection-off"
    # if seating_plan_is_active and context["level"] == "Admin":
    #     context["room_selection_show"] = "Yes"

    return render(request, "classes.html", context= context)




def do_plan(request:HttpRequest):
    global seating_plan_is_active, seating_plan

    if request.user.is_anonymous:
        return redirect('/login')

    if not request.user.is_subadmin:
        return redirect('/')

    context = get_user_cont(request)

    action = request.GET.get('action', '')
    print("actioon====>", action)

    if action == "cmd":
        cmd = request.GET.get("cmd")

        if cmd == "newplan":

            if seating_plan["name"] == None and seating_plan["rooms"] == [] and seating_plan["batch"] == {} and seating_plan["date"] == None:
                print("id is none")
                idd = random.randint(10000, 90000)
                seating_plan["id"] = idd
                seating_plan["time"] = time.time()
                seating_plan["batch"] = {}
                seating_plan["date"] = None
                seating_plan["rooms"] = []
                seating_plan["shift"] = None
                seating_plan["name"] = None
                time.sleep(5)

                data = {"stat" : "1", "plan_id" : str(idd)}

            else:
                print("id not is none")
                data = {"stat" : "0"}

            return JsonResponse(data)

        elif cmd == "delplan":
            print("Delete Plan is accessed...")
            seating_plan["id"] = None
            seating_plan["time"] = None
            seating_plan["batch"] = {}
            seating_plan["date"] = None
            seating_plan["rooms"] = []
            seating_plan["shift"] = None
            seating_plan["name"] = None

            seating_plan_is_active = False



    if request.method == "POST":
        action = request.POST.get("postaction")

        if action == "newplan":

            planid = request.POST.get("planid", "").strip()
            planame = request.POST.get("planame", "").strip()
            plandate = request.POST.get("plandate", "").strip()
            shift = request.POST.get("shift", "").strip()

            print(f"planid==> {planid}")
            print(f"planame==> {planame}")
            print(f"plandate==> {plandate}")
            print(f"shift==> {shift}")

            if planid != str(seating_plan["id"]):
                print("idd not equal to int")
                return render(request, "seating.html", context=context)

            #validating data
            if planame == "" or plandate == "" or shift == "":
                print("Plan is not valid")
                return render(request, "seating.html", context=context)

            # checking prev plan
            if seating_plan["batch"] != {} or seating_plan["rooms"] != [] or seating_plan["date"] != None:
                print("prev plan is invalid")
                print(f"seating_plan==> {seating_plan}")
                return render(request, "seating.html", context=context)

            # every things loks good so preceed to nest step


            try:
                plandate = datetime.date.fromisoformat(plandate).strftime("%d/%m/%Y")
            except:
                return render(request, "seating.html", context=context)

            seating_plan["date"] = plandate
            seating_plan["name"] = planame
            seating_plan["shift"] = shift

            seating_plan_is_active = True



    if seating_plan["id"] != None and seating_plan["date"] != None and seating_plan_is_active:

        context["idd"] = seating_plan["id"]
        context["planame"] = seating_plan["name"]
        context["plandate"] = seating_plan["date"]
        context["planshift"] = seating_plan["shift"]

        context["rooms"] = seating_plan["rooms"]
        context["batch"] = seating_plan["batch"]
        context["algorithm"] = planning_algorith


        return render(request, "selectrc.html", context=context)


    return render(request, "seating.html", context=context)




def make_plan(request: HttpRequest):
    global seating_plan_is_active, seating_plan

    if request.user.is_anonymous:
        return redirect('/login')

    if not request.user.is_subadmin:
        return redirect('/')

    context = get_user_cont(request)
    action = request.GET.get('action', '')
    model = request.GET.get('model', '')

    print(f"model ===========>  {model}")

    if model not in planning_algorith:
        model = "SP_Model 4.8"


    rooms = []
    print("Accessing room")


    for room_num in seating_plan["rooms"]:

        room_obj = Rooms.objects.filter(room_num=room_num).first()
        if room_obj != None:
            one_room = {
                "room_no" : room_obj.room_num,
                "total_desk" : room_obj.seats,
                "rows" : {},
                "info" : room_obj.dis,
                "gate_side" : room_obj.gate,
                "room_disc" : room_obj.dis,
                }

            gate_side = room_obj.gate
            room_disc = room_obj.dis

            all_rows_obj = RoomsRows.objects.filter(room_num=room_num)
            seat_count = 0
            map_data_room_number = room_num

            for row in all_rows_obj:
                one_room["rows"][f"row_{row.row_num}"] = {
                    "capacity" : row.capicity,
                    "desks" : row.desks,
                }

            rooms.append(one_room.copy())


    print("rooms==", rooms)

    classes = []

    for batch_id in seating_plan["batch"]:
        batch_obj = Batch.objects.filter(bachid=batch_id).first()

        one_batch = {
            "batch_id" : batch_obj.bachid,
            "course" : batch_obj.course,
            "classname" : batch_obj.classname,
            "students" : [],
        }

        students_obj = Stundets.objects.filter(bachid=batch_obj)

        for student in students_obj:
            one_batch["students"].append(student.rollnum)

        classes.append(one_batch.copy())

    # sending data for planning

    if model == "SP_Model 4.8":
        planingAlgo = SpMethod4(rooms=rooms, classes=classes)

    elif model == "SP_Model 3.3":
        planingAlgo = SpMethod3(rooms=rooms, classes=classes)

    planned_data = planingAlgo.planning()

    # for room in planned_data:
    #     method4.print_room_data(room, planned_data[room])

    context["seating_argmnt_data"] = planned_data

    return render(request, "plannedroom.html", context=context)


def genSessionId(len_ = 50, idList= []):
    data = "zxcvbnmasdfghjklqwertyuiop1234567890ZXCVBNMASDFGHJKLQWERTYUIOP"
    id_ = ""
    for i in range(len_):
        id_ += choice(data)

    if id_ in idList:
        genSessionId(len_, idList)
    else:
        return id_

def getOtp(len_=8):
    otp = ""
    for i in range(len_):
        otp += choice("0493826571")
    return otp

def signupuser(request : HttpRequest):

    action = request.GET.get('action', '')
    token = request.GET.get("token", None)
    if token == None:
        if request.method == "POST":
            print("toke is  got from post request")
            token = request.POST.get("token")

    context = {}

    print(f"actionn===> {action}")
    print(f"token==> {token}")

    print(f"tokenList==> {signupuser_pages_token}")


    if token not in signupuser_pages_token:
        fro_m = request.GET.get('from', None)
        if fro_m == "fetch":
            return JsonResponse({"error" : "Page Authentication error. Please try again.", "status" : "error", "error_code" : 0})


        tokenid = genSessionId(idList=signupuser_pages_token)
        signupuser_pages_token.append(tokenid)
        context["token"] = tokenid
        print("token noot in")

        context["message"] = "This action requires email verification. An OTP is send to your email to verify your email id."
        context["prefix"] = "Hey!, "


        return render(request, "signupuser.html", context=context)

    signupuser_pages_token.remove(token)
    print("removing  token")


    if action == "addemail":
        print("add action email")

        email = request.GET.get("val")

        print(f"Emil==> {email}")
        tokenid = genSessionId(idList=signupuser_pages_token)
        signupuser_pages_token.append(tokenid)

        new_authkey = genSessionId(idList=list(signup_data))
        otp = getOtp(6)

        print(f"OTP==> {otp}")


        signup_data[new_authkey] = {
            "email" : email,
            "email_veried" : 0,
            "otp" : otp,
            "otp_time" : time.time(),
            "token" : tokenid,
            "trytime" : 0,
        }

        page = send_email.send_otp("User", otp)
        st = send_email.send(email, "Verify Email", page)
        if st:
            print("Email is send")

            data = {"token" : tokenid, "status" : "validemail", "auth" : new_authkey}
        else:
            data = {"error" : "Error in sending OTP to this email id. Please try later.", "status" : "error"}

        return JsonResponse(data)

    elif action == "verifyotp":
        print("add action email")


        otp = request.GET.get("val")
        authkey = request.GET.get("auth")


        if authkey in  signup_data:

            print(f"Email=====> {signup_data[authkey]['email']}")
            if token != signup_data[authkey]['token']:
                return JsonResponse({"error" : "Page Authentication error. Please try again.", "status" : "error", "error_code" : 0})

            tokenid = genSessionId(idList=signupuser_pages_token)

            print(f"trytime===> {signup_data[authkey]['trytime']}")



            if signup_data[authkey]["trytime"] > 2:
                return JsonResponse({"error" : "Blocked this id due to too many attempts. Please use another email id.", "status" : "error",  "error_code" : 0})



            if otp != signup_data[authkey]["otp"]:
                signupuser_pages_token.append(tokenid)
                signup_data[authkey]['token'] = tokenid

                signup_data[authkey]["trytime"] = signup_data[authkey]["trytime"] + 1
                if (3 - signup_data[authkey]['trytime']) == 0:
                    chance = "no chance"
                elif (3 - signup_data[authkey]['trytime']) == 1:
                    chance = f"{(3 - signup_data[authkey]['trytime'])} chance"
                else:
                    chance = f"{(3 - signup_data[authkey]['trytime'])} chances"

                return JsonResponse({"status" : "error", "token" : tokenid,  "error" : f"The OTP you've entered is incorrect. Please try again. You have {chance} is left.",  "error_code" : 1})


            if (time.time() - signup_data[authkey]["otp_time"]) > 120:

                signupuser_pages_token.append(tokenid)
                signup_data[authkey]['token'] = tokenid

                signup_data[authkey]["trytime"] = signup_data[authkey]["trytime"] + 1

                otp = getOtp(6)
                signup_data[authkey]["otp"] = otp
                signup_data[authkey]["otp_time"] = time.time()

                if (3 - signup_data[authkey]['trytime']) == 0:
                    chance = "no chance"
                elif (3 - signup_data[authkey]['trytime']) == 1:
                    chance = f"{(3 - signup_data[authkey]['trytime'])} chance"
                else:
                    chance = f"{(3 - signup_data[authkey]['trytime'])} chances"

                page = send_email.send_otp("User", otp)

                st = send_email.send(signup_data[authkey]["email"], "Verify Email (sent again)", page)
                if not st:
                    return JsonResponse({"error" : "Error in sending email to this email. Please try again or later.", "status" : "error", "error_code" : 0})

                return JsonResponse({"status" : "error", "token" : tokenid,  "error" : f"The OTP entered is expired. A new OTP is sent again to your email. Please check and enter it. Your have only  {chance} is left.", "error_code" : 2})


            data = {
                "status" : "validotp",
                "token" : tokenid,
            }

            # # remove any prev data with same id
            email = signup_data[authkey]["email"]
            # for keys in signup_data:
            #     if keys != authkey:
            #         if signup_data[keys]["email"] == email:
            #             signup_data.pop(keys)
            #             print("=============> ID is removed")  getting an error: data changed duing etration

            userObj = MyUser.objects.filter(email = email).first()
            print(f"UserObject===> {userObj}")
            if userObj != None:
                return JsonResponse({"status" : "error", "error" : f'This email address is already registered. If this belogs to you, click on  <a href="/passwordReset?email={email}">Forgot Password</a> to change password or <a style="color : green;" href="/contacts">Contact</a> to the admin if any issue.', "error_code" : 0})


            signup_data[authkey]["otp"] = "verified"
            signup_data[authkey]["email_veried"] = 1
            signup_data[authkey]["token"] = tokenid

            signupuser_pages_token.append(tokenid)

            print("opt verified...")
            return JsonResponse(data)


    if request.method == "POST":
        print("post mehhtods is here")
        action = request.POST.get("postaction")

        if action == "addphone":

            phone = request.POST.get("pnumber")
            email = request.POST.get("email")
            authkey = request.POST.get("authkey")
            token = request.POST.get("token")

            if authkey not in  signup_data:
                return JsonResponse({"error" : "invalid auth"})

            print(f"Phone Email=====> {signup_data[authkey]['email']}")
            if token != signup_data[authkey]['token']:
                return JsonResponse({"error" : "invalid token"})

            if email != signup_data[authkey]['email']:
                return JsonResponse({"error" : "invalid email"})

            if not signup_data[authkey]['email_veried']:
                return JsonResponse({"error" : "invalid not verified"})

            print(f"email==> {email} ")
            print(f"phone==> {phone} ")
            print(f"authkey==> {authkey} ")

            tokenid = genSessionId(idList=signupuser_pages_token)

            signup_data[authkey]["token"] = tokenid
            signup_data[authkey]["phone"] = phone

            signupuser_pages_token.append(tokenid)

            context["token"] = tokenid
            context["authkey"] = authkey

            return render(request, "userdetail.html", context=context)


        elif action == "userdetails":

            fname = request.POST.get("fname")
            lname = request.POST.get("lname", "")
            authkey = request.POST.get("authkey")
            token = request.POST.get("token")
            gender = request.POST.get("gender")
            dob = request.POST.get("dob")

            if authkey not in  signup_data:
                return JsonResponse({"error" : "invalid auth"})

            if token != signup_data[authkey]['token']:
                return JsonResponse({"error" : "invalid token"})

            print(f"fname ==>{fname}")
            print(f"lname ==>{lname}")
            print(f"gender ==>{gender}")
            print(f"dob ==>{dob}")
            print(f"email ==>{signup_data[authkey]['email']}")

            tokenid = genSessionId(idList=signupuser_pages_token)

            signup_data[authkey]["token"] = tokenid
            signupuser_pages_token.append(tokenid)

            signup_data[authkey]["fname"] = fname
            signup_data[authkey]["lname"] = lname
            signup_data[authkey]["gender"] = gender
            signup_data[authkey]["dob"] = dob

            context["token"] = tokenid
            context["authkey"] = authkey
            context["fname"] = fname
            context["message"] = "Please create a password that is at least 8 characters in length"
            context["prefix"] = f"Hey {fname}! , "

            return render(request, "password.html", context=context)


        elif action == "passwd":

            passwd = request.POST.get("passwd")
            confirmpasswd = request.POST.get("confirmpasswd")
            authkey = request.POST.get("authkey")
            token = request.POST.get("token")

            if authkey not in  signup_data:
                return JsonResponse({"error" : "invalid auth"})

            if token != signup_data[authkey]['token']:
                return JsonResponse({"error" : "invalid token"})


            passwd_val = Validator(passwd = passwd, email=signup_data[authkey]['email'], name=f"{signup_data[authkey]['fname']} {signup_data[authkey]['lname']}", phone=signup_data[authkey]['phone'])

            error = passwd_val.validate()

            if error:
                tokenid = genSessionId(idList=signupuser_pages_token)
                signupuser_pages_token.append(tokenid)
                signup_data[authkey]['token'] = tokenid


                context["message"] = error

                context["token"] = tokenid
                context["authkey"] = authkey
                context["passwd"] = confirmpasswd

                context["fname"] = f"Hey {signup_data[authkey]['fname']}!"

                return render(request, "password.html", context=context)



            email = signup_data[authkey]['email']
            phone = signup_data[authkey]['phone']
            fname = signup_data[authkey]['fname']
            lname = signup_data[authkey]['lname']
            gender = signup_data[authkey]['gender']
            dob = signup_data[authkey]['dob']

            print("User Detials")
            print(f"email ==> {email}")
            print(f"phone ==> {phone}")
            print(f"fname ==> {fname}")
            print(f"lname ==> {lname}")
            print(f"gender ==> {gender}")
            print(f"dob ==> {dob}")
            print(f"passwd ==> {passwd}")
            print(f"confirmpasswd ==> {confirmpasswd}")

            #encrypt data

            dob = encrypt(key_enc, dob)

            e_st = False

            userObj = MyUser.objects.filter(email = email).first()
            if userObj != None:
                e_st = True

            userObj = MyUser.objects.filter(phone_no = phone).first()
            if userObj != None:
                e_st = True

            if  e_st:
                return JsonResponse({"Error" : "email or phone is already associated to  antoher account"})

            genderid = 4
            profile = "man.png"
            if gender == "Male":
                genderid = 1
            elif gender == "Female":
                genderid = 2
                profile = "girl.png"


            singup = MyUser(email=email, phone_no=phone, full_name=f"{fname} {lname}", gnder=genderid, dob=dob, propath=profile ,is_verified=True)
            singup.set_password(confirmpasswd)
            singup.save()

            login( request , singup)

            return  redirect('/')



    return render(request, "signupuser.html", context=context)


def profile_img_upload(request : HttpRequest):

    print("Acessing upload file page")

    if request.method == "POST":
        email = request.user.email

        file_data = request.POST.get("photo")

        file = request.FILES['photo']
        print(f"File name==> {file.name}")

        file_name = f"{email}_profile{os.path.splitext(file.name)[1]}"

        full_path = f"/home/darkstartech/projects/static/profile/{file_name}"



        print(f"file_name=> {file_name}")

        try:
            if os.path.exists(request.user.propath):
                if file_name != request.user.propath:
                    os.remove(request.user.propath)
                    print("File is delete")
                else:
                    print("File is overwrite")
            else:
                print("File  notfound")
        except Exception as e:
            print(f"Error at removing file: {e}")


        with open(full_path, 'wb') as dest:
            for chunk in file.chunks():
                dest.write(chunk)


        request.user.propath = file_name;
        request.user.save(update_fields=['propath'])


        print(f"Email ==> {email} ===> {file_data}")
    else:
        print(f"not poast Method===> {request.method}")


    return HttpResponse(status=204)



def test_page(request : HttpRequest):
    # context = {
    #     "message" : "Please create a password that is at least 8 characters in length",
    #     "prefix" : "Hey Aditya! , ",
    #     "fname" : "Aditya"
    # }

    # if request.method == "POST":

    #     passwd = request.POST.get("passwd")
    #     confirmpasswd = request.POST.get("confirmpasswd")


    #     passwd_val = Validator(passwd = passwd, email=request.user.email, name=request.user.full_name, phone=request.user.phone_no)

    #     error = passwd_val.validate()

    #     if error:
    #         context["message"] = error
    #         context["passwd"] = passwd

    #         return render(request, "password.html", context=context)

    #     else:
    #         return HttpResponse("<h1>Welcome</h1>")


    return render(request, "basicdetails.html")



@csrf_exempt
def devmng(request : HttpRequest):
    action = request.GET.get('action', '')
    print(f"Data==> {request.GET}")

    if request.method == "POST":
        print(f"Header : {request.headers}")
        print(f"Data: {request.POST}")
        print(f"Data2: {request.POST.lists()}")

    return JsonResponse({"stat" : 1, "cmd" : ""})


def get_id(txt):
    idd = ''
    for word in txt.split(" "):
        idd += word[:3]
    return idd.lower()


def generateSubjectIds(subjects):
    print(f"Subjec==> {subjects}")
    subid = []
    for sub in subjects:
        subid.append(get_id(sub))
    return subid

def add_list(lst1, lst2, lst3):
    tmp_list = []
    indx = 0
    for a in lst1:
        tmp_list.append([a, lst2[indx], lst3[indx]])
        indx += 1

    return tmp_list

def add_2_list(lst1, lst2):
    tmp_list = []
    indx = 0
    for a in lst1:
        tmp_list.append([a, lst2[indx]])
        indx += 1
    return tmp_list


def add_attendence_date(request : HttpRequest):
    if request.user.is_anonymous:
        return redirect('/login')

    context = get_user_cont(request)
    context["emailaddrs"] = request.user.email

    class_of = Classes.objects.filter(class_admin=request.user).first()
    print(f"class==> {class_of}")
    if class_of == None:
        return HttpResponse("Error 509")

    subjects = Subjects.objects.filter(classname=class_of).values_list("subjct")
    subjects = [sub[0] for sub in subjects]
    subjct_ids = generateSubjectIds(subjects)

    today_or_date = datetime.date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        date_of = request.POST.get("dateofclass")
        print("Date==> ", date_of)
        data = {}
        indx = 0
        for ids in subjct_ids:
            val = request.POST.get(ids)
            if val == "on":
                val = 1
            else:
                val = 0

            data[subjects[indx]] = val
            indx += 1

        print(f"Data==> {data}")

        for subj in data:
            subj_obj = DateOfClass.objects.filter(classname=class_of, date_of=date_of, subjct=subj).first()
            if subj_obj != None:
                subj_obj.value = data[subj]
                subj_obj.save(update_fields=["value"])
            else:
                subj_obj = DateOfClass(classname=class_of, date_of=date_of, subjct=subj, value=data[subj])
                subj_obj.save()

        today_or_date = date_of

    else:
        get_date = request.GET.get("date")
        if get_date  != None:
            today_or_date = get_date


    values_ondate_obj = DateOfClass.objects.filter(classname=class_of, date_of=today_or_date).values_list("subjct", "value")
    if values_ondate_obj:
        values_dict = {}
        for oneitem in values_ondate_obj:
            subj = oneitem[0]
            if oneitem[1]:
                val = "checked"
            else:
                val = ""
            values_dict[subj] = val

        values_list = []
        for subj in subjects:
            values_list.append(values_dict[subj])
    else:
        print("record not found")
        values_list = []
        for i in subjects:
            values_list.append("")

    context["subjects"] = add_list(subjects, subjct_ids, values_list)
    context["date"] = today_or_date
    context["class"] = class_of
    return render(request, "attendancedate.html", context=context)


def attendance(request : HttpRequest):
    if request.user.is_anonymous:
        return redirect('/login')

    context = get_user_cont(request)
    context["emailaddrs"] = request.user.email

    action = request.GET.get('action', '')

    user_class = AttendUser.objects.filter(email = request.user).first()

    if request.method == "POST":
        post_action = request.POST.get("postaction")

        if post_action == "adduser":
            class_st = request.POST.get("classofst")
            rollnum = request.POST.get("rollnum")
            notify = request.POST.get("notify")

            if notify == "on":
                notify = 1
            else:
                notify = 0

            errormsg = None

            if rollnum == None:
                errormsg = "Please enter a roll number"

            if not Classes.objects.filter(classname=class_st).exists():
                errormsg = "Please choose a valid class"

            if AttendUser.objects.filter(rollnum=rollnum).exists():
                errormsg = "This roll number belongs to another user. If this is yours, contact the site admin."

            if errormsg:
                context["rollnum"] = rollnum
                context["classofst"] = class_st
                context["message"] = errormsg
                classes = Classes.objects.all().values_list("classname")
                context["classes"] = [cl[0] for cl in classes]
                return render(request, "basicdetails.html", context=context)

            clas =  Classes.objects.filter(classname=class_st).first()

            rollnum = rollnum.lower()

            atten_user_obj = AttendUser(rollnum=rollnum, classname=clas, email=request.user, notify=notify)
            atten_user_obj.save()

            user_class = AttendUser.objects.filter(email = request.user).first()
            # print("record is saved....")


    if not user_class:
        classes = Classes.objects.all().values_list("classname")
        context["classes"] = [cl[0] for cl in classes]
        return render(request, "basicdetails.html", context=context)

    subjects = Subjects.objects.filter(classname=user_class.classname).values_list("subjct")
    subjects = [sub[0] for sub in subjects]
    subjct_ids = generateSubjectIds(subjects)

    dates = DateOfClass.objects.order_by("-date_of").values_list("date_of").distinct()


    if action == "attenadd":
        subjid = request.GET.get("subid")
        date = request.GET.get("date")
        val = request.GET.get("value")



        if not subjid in subjct_ids:
            return JsonResponse({"status": "error", "error": "Unknown subject id"})

        if_found = 0
        for date_in in dates:
            if date_in[0].strftime("%Y-%m-%d") == date:
                if_found = 1
                break

        if not if_found:
            return JsonResponse({"status": "error", "error": f"This  date <{date}> is not allowed "})

        lecture_on = DateOfClass.objects.filter(classname=user_class.classname, date_of=date).values_list("subjct", "value")
        lecture_on_data = {sub[0]: sub[1] for sub in lecture_on}

        full_subject = subjects[subjct_ids.index(subjid)]

        if not lecture_on_data[full_subject]:
            return JsonResponse({"status": "error", "error": f"Can't add Attendance of an empty lacture."})

        atten_obj = Attendance.objects.filter(email=request.user, date=date, subject=full_subject).first()
        if atten_obj:
            atten_obj.value = val
            atten_obj.save(update_fields=["value"])
        else:
            atten_obj = Attendance(email=request.user, date=date, subject=full_subject, value=val)
            atten_obj.save()


        #updating table record for subject...
        atten_obj = Attendance.objects.filter(email=request.user, subject=full_subject, value=1).values_list("date")

        lecture_on = DateOfClass.objects.filter(classname=user_class.classname, subjct=full_subject, value=1).values_list("date_of")
        lecture_on = [lect[0] for lect in lecture_on]

        mine = 0
        total = len(lecture_on)
        for atten_date in atten_obj:
            if atten_date[0] in lecture_on:
                mine += 1

        try:
            prcnt = str((mine/total)*100)
            prcnt = prcnt[:prcnt.find(".")+2]
            try:
                if prcnt[prcnt.find(".") +1] == "0":
                    prcnt = f"{prcnt[:prcnt.find('.')]}"
            except:
                pass
        except:
            prcnt = "0"

        need = get_num_days(total, mine)

        return JsonResponse({"status": "ok", "sub": subjid, "total": total, "mine" : mine, "prcnt": prcnt, "need" : need})




    context["subjects"] = add_2_list(subjects, subjct_ids)
    context["subject_ids"] = subjct_ids

    if Classes.objects.filter(class_admin=request.user).exists():
        context["classadmin"] = "/plusdates"

    atten_data = []

    user_atten_data = {subjct : 0 for subjct in subjects}



    for date in dates:
        s_date = date[0].strftime("%Y-%m-%d")
        f_date = date[0].strftime("%b %d, %Y")
        day_name = date[0].strftime("%A")

        lecture_on = DateOfClass.objects.filter(classname=user_class.classname, date_of=s_date).values_list("subjct", "value")
        lecture_on_data = {sub[0]: sub[1] for sub in lecture_on}
        # print(f"Lacture_on_date==> ", lecture_on_data)

        atten_obj = Attendance.objects.filter(email=request.user, date=s_date).values_list("subject", "value")
        val_data = []

        if atten_obj:
            print(f"AttendanceFound==> {atten_obj}")
            atten_val_dict = {sub[0]: sub[1] for sub in atten_obj}
            for subjct in subjects:
                value = lecture_on_data[subjct]

                if not value:
                    val_data.append(2)
                else:
                    try:
                        val = atten_val_dict[subjct]
                        if val == 1:
                            user_atten_data[subjct] = user_atten_data[subjct] + 1


                    except:
                        val = 3
                    val_data.append(val)
        else:
            # print("Atendance_not_found..")
            for subjct in subjects:
                value = lecture_on_data[subjct]

                if value:
                    val_data.append(3)
                else:
                    val_data.append(2)

        atten_data.append([f_date, s_date, day_name, val_data])


    context["attendata"] = atten_data

    # calcutaing %age of lecctures....
    lecture_data = {subjct : 0 for subjct in subjects}
    lectures = DateOfClass.objects.filter(classname=user_class.classname).values_list("subjct", "value")
    for lect in lectures:
        if lect[1]:
            lecture_data[lect[0]] = lecture_data[lect[0]] + 1
    # print(f"lecture_data==> {lecture_data}")

    # getting user lectures....
    # user_atten_data = {subjct : 0 for subjct in subjects}
    # user_atten = Attendance.objects.filter(email=request.user, value=1).values_list("subject", "value", "date")


    # for atten in user_atten:

    #     user_atten_data[atten[0]] = user_atten_data[atten[0]] + 1

    # print("user_atten==>", user_atten_data)

    prcnt_data = []
    for lect in lecture_data:
        try:
            prcnt = str((user_atten_data[lect]/lecture_data[lect])*100)
            prcnt = prcnt[:prcnt.find(".")+2]
            try:
                if prcnt[prcnt.find(".") +1] == "0":
                    prcnt = f"{prcnt[:prcnt.find('.')]}"
            except:
                pass
        except:
            prcnt = "0"

        need = get_num_days(lecture_data[lect], user_atten_data[lect])

        prcnt_data.append([get_id(lect), lect, lecture_data[lect], user_atten_data[lect], f"{prcnt}%",  need])

    context["precntdata"] = prcnt_data

    return render(request, "attendance.html", context=context)


