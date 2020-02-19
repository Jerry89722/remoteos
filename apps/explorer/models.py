from django.db import models

# Create your models here.
from db.basemodel import BaseModel


class TvChannels(BaseModel):
    channel_name = models.CharField(max_length=20, verbose_name='频道名称')
    channel_id = models.IntegerField(verbose_name='频道号')
    channel_url = models.CharField(max_length=512, verbose_name='频道地址')

    class Meta:
        db_table = 'ros_channels'
        verbose_name = 'channel'
        verbose_name_plural = 'channels'
