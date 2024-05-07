from django.db import models
from django import forms

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyUserManager(BaseUserManager):
    def create_user(self, email,full_name,phone_no, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            phone_no=phone_no,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,full_name,phone_no, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            full_name=full_name,
            phone_no=phone_no,

        )
        user.is_admin = True
        user.is_verified=True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=255,
        unique=True,
    )

    phone_no = models.CharField(max_length = 10 ,verbose_name="Phone Number",unique=True)

    full_name = models.CharField(max_length = 50, verbose_name = "Name", blank=False)
    gnder = models.IntegerField(verbose_name="Gender", blank=True, default="4")
    dob = models.CharField(max_length=100, verbose_name="DOB", blank=True, null=True)


    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_subadmin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    auth_token = models.CharField(max_length=200,blank=True)
    auth_token_time = models.CharField(max_length=50 ,default="None")
    propath = models.CharField(max_length = 100, verbose_name = "Profile", blank=True, null=True, default="not")


    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["full_name",'phone_no']


    def __str__(self):
        return self.email

    def get_email(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_phone_no(self):
        return self.phone_no


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



class Contact(models.Model):
    name= models.CharField(max_length=132)

    email=models.CharField(max_length=130)
    phone=models.CharField(max_length=12)
    desc=models.TextField()
    date=models.DateField()

    def __str__(self):
        return self.name


class Rooms(models.Model):
    room_num = models.IntegerField(verbose_name="Room Number", primary_key=True, null=False)
    seats = models.IntegerField(verbose_name="Total Seats", null=False)
    gate = models.CharField(verbose_name="Gate Side", max_length=7, default="left")
    dis = models.TextField(verbose_name="Room Discription", blank=True)

    def __str__(self):
        return f"Room: {str(self.room_num)}"


class RoomsRows(models.Model):
    room_num = models.ForeignKey(Rooms, on_delete=models.CASCADE, verbose_name="Room Number")
    row_num = models.IntegerField(verbose_name="Row Number", blank=False)
    desks = models.IntegerField(verbose_name="Desk in Row", blank=False)
    capicity = models.IntegerField(verbose_name="Capacity", blank=False)

    def __str__(self):
        return f"{str(self.room_num)}==> {str(self.row_num)}"


class Batch(models.Model):
    bachid = models.CharField(verbose_name="Batch", primary_key=True, null=False, max_length=10)
    course = models.CharField(verbose_name="Course", null=False, max_length=20)
    classname = models.CharField(verbose_name="Class Name", null=True, max_length=50)

    def __str__(self) -> str:
        return f"{self.bachid} : {self.course}"

class Stundets(models.Model):
    rollnum = models.CharField(verbose_name="Roll Number", primary_key=True, max_length=20)
    name = models.CharField(verbose_name="Name", null=False, max_length=100)
    email = models.EmailField(verbose_name="E-mail", null=True, max_length=200)

    bachid = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name="Batch")


    def __str__(self) -> str:
        return f"{self.rollnum} : {self.name}"

class Classes(models.Model):
    classname = models.CharField(verbose_name="Class", primary_key=True, max_length=30)
    class_admin = models.ForeignKey(MyUser, on_delete=models.SET_NULL, verbose_name="Class Admin" , null = True)

    def __str__(self) -> str:
        return f"{self.classname}"

class Subjects(models.Model):
    subjct = models.CharField(verbose_name="Subject", primary_key=False, max_length=30)
    classname = models.ForeignKey(Classes, on_delete=models.CASCADE, verbose_name="Class")

    def __str__(self) -> str:
        return f"{self.subjct} : {self.classname}"

class AttendUser(models.Model):
    rollnum = models.CharField(verbose_name="Roll Number", primary_key=True, max_length=20)
    classname = models.ForeignKey(Classes, on_delete=models.CASCADE, verbose_name="Class")
    email = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name="Email")
    notify = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.rollnum} : {self.email}"

class DateOfClass(models.Model):
    classname = models.ForeignKey(Classes, on_delete=models.CASCADE, verbose_name="Class")
    date_of = models.DateField( verbose_name="Date")
    subjct = models.CharField(verbose_name="Subject", max_length=30)
    value = models.BooleanField(default=False, verbose_name="Value")

    def __str__(self) -> str:
        return f"{self.classname} : {self.date_of} : {self.subjct}"


class Attendance(models.Model):
    email = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name="Email")
    date = models.DateField(verbose_name="Date", null=False)
    subject = models.CharField(verbose_name="Subject", max_length=30, null=False)
    value = models.IntegerField(verbose_name="Value", default=3)

    def __str__(self) -> str:
        return f"{self.email}: {self.date}: {self.subject}"
