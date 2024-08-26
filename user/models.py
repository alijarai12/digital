import os.path
from io import BytesIO
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from core.utils.managers import ActiveManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        # email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


GENDER_CHOICES = [
    ("Male", _("Male")),
    ("Female", _("Female")),
    ("Other", _("Other")),
]


class User(AbstractBaseUser):
    username = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=15, default="Male", choices=GENDER_CHOICES)
    ward = models.JSONField(default=list, blank=True, null=True)
    group = models.ForeignKey(
        Group, related_name="UserGroup", on_delete=models.CASCADE, blank=True, null=True
    )
    designation = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to="upload/profile/", null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to="upload/profile/", editable=False, null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = "email"

    objects = UserManager()
    active = ActiveManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def make_thumbnail(self):
        try:
            image = Image.open(self.image)
            image.thumbnail((200, 150), Image.ANTIALIAS)
            thumb_name, thumb_extension = os.path.splitext(self.image.name)
            thumb_extension = thumb_extension.lower()
            thumb_filename = thumb_name + "_thumb" + thumb_extension
            if thumb_extension in [".jpg", ".jpeg"]:
                FTYPE = "JPEG"
            elif thumb_extension == ".gif":
                FTYPE = "GIF"
            elif thumb_extension == ".png":
                FTYPE = "PNG"
            else:
                return False  # Unrecognized file type
            # Save thumbnail to in-memory file as StringIO
            temp_thumb = BytesIO()
            image.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)
            # set save=False, otherwise it will run in an infinite loop
            self.thumbnail.save(
                thumb_filename, ContentFile(temp_thumb.read()), save=False
            )
            temp_thumb.close()
            return True
        except:
            pass

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.title()
        if self.designation:
            self.designation = self.designation[0].capitalize() + self.designation[1:]
        try:
            self.make_thumbnail()
            super(User, self).save(*args, **kwargs)
        except:
            super(User, self).save(*args, **kwargs)

    def __str__(self):
        if self.username:
            return self.username
        else:
            return f"User {self.id}"


class WorkshopMode(models.Model):
    workshop_mode = models.BooleanField(default=False, null=True, blank=True)
