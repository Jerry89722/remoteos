from django.db import models
from db.basemodel import BaseModel


class BaseMedia(BaseModel):
    title = models.CharField(max_length=128, verbose_name='名称')
    item_number = models.IntegerField(unique=True, null=True, verbose_name='编号')
    url = models.CharField(max_length=512, verbose_name='地址')
    author = models.CharField(max_length=128, verbose_name='创作者')

    def __str__(self):
        return self.title

    class Meta:
        # 说明这是一个抽象模型类
        abstract = True


class TvChannels(BaseMedia):
    class Meta:
        db_table = 'ros_channels'
        verbose_name = 'channel'
        verbose_name_plural = verbose_name


class Favourite(BaseMedia):
    class Meta:
        db_table = 'ros_favourite'
        verbose_name = 'favourite'
        verbose_name_plural = verbose_name

