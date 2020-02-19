# from django.db import models
# from django.contrib.auth.models import AbstractUser
#
# from db.basemodel import BaseModel
#
#
# class User(AbstractUser, BaseModel):
#     # def generate_active_token(self):
#     #     """ 生成用户签名字符串 """exit
#
#     #     serializer = Serializer(settings.SECRET_KEY, 3600)
#     #     info = {'confirm': self.id}
#     #     token = serializer.dumps(info)
#     #     return token.decode()
#
#     class Meta:
#         db_table = 'df_user'
#         verbose_name = '用户'
#         verbose_name_plural = verbose_name
