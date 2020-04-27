from django.db import models
from django.contrib.auth.models import AbstractUser

from db.basemodel import BaseModel


class User(AbstractUser, BaseModel):
    phone = models.CharField(max_length=20, unique=False, verbose_name="手机号")
    is_admin = models.BooleanField(default=False, verbose_name="管理员标记")

    class Meta:
        db_table = 'ros_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
