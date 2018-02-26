#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/2/13
# Created by 独自等待
# Blog: https://www.waitalone.cn/
# 上传文件重命名
# https://segmentfault.com/q/1010000007316349/a-1020000007316494
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from system.storage import ImageStorage


# Create your models here.
# 用户模型
# 第一种：采用继承方式扩展用户信息（本系统采用）
# 扩展：采用关联方式扩展用户信息
class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatar/%Y/%m', storage=ImageStorage(),
        default='avatar/default.png',
        max_length=200, verbose_name=u'用户头像'
    )
    qq = models.CharField(max_length=20, blank=True, null=True, verbose_name=u'QQ号码')
    mobile = models.CharField(max_length=11, blank=True, null=True, verbose_name=u'手机号码')
    url = models.URLField(max_length=100, blank=True, null=True, verbose_name=u'个人网页地址')

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __unicode__(self):
        return self.username


# tag (标签)
class Tag(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'标签名称')

    class Meta:
        verbose_name = u'标签'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


# 分类
class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'分类名称')
    index = models.IntegerField(default=999, verbose_name=u'分类排序')

    class Meta:
        verbose_name = u'分类'
        verbose_name_plural = verbose_name
        ordering = ['index', 'id']

    def __unicode__(self):
        return self.name


# 自定义一个文章Model的管理器
# 1、新加一个数据处理的方法
# 2、改变原有的queryset
class ArticleManager(models.Manager):
    def distinct_date(self):
        distinct_date_list = []
        date_list = self.values('date_publish')
        for date in date_list:
            date = date['date_publish'].strftime('%Y/%m')
            if date not in distinct_date_list:
                distinct_date_list.append(date)
        return distinct_date_list


# 文章模型
class Article(models.Model):
    title = models.CharField(max_length=50, verbose_name=u'文章标题')
    desc = models.CharField(max_length=50, verbose_name=u'文章描述')
    content = models.TextField(verbose_name=u'文章内容')
    click_count = models.IntegerField(default=0, verbose_name=u'点击次数')
    is_recommend = models.BooleanField(default=False, verbose_name=u'是否推荐')
    date_publish = models.DateTimeField(auto_now_add=True, verbose_name=u'发布时间')
    user = models.ForeignKey(User, verbose_name=u'用户')
    category = models.ForeignKey(Category, blank=True, null=True, verbose_name=u'分类')
    tag = models.ManyToManyField(Tag, verbose_name=u'标签')

    objects = ArticleManager()

    class Meta:
        verbose_name = u'文章'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __unicode__(self):
        return self.title


# 评论模型
class Comment(models.Model):
    content = models.TextField(verbose_name=u'评论内容')
    username = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'用户名')
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name=u'邮箱地址')
    url = models.URLField(max_length=100, blank=True, null=True, verbose_name=u'个人网页地址')
    date_publish = models.DateTimeField(auto_now_add=True, verbose_name=u'发布时间')
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'用户')
    article = models.ForeignKey(Article, blank=True, null=True, verbose_name=u'文章')
    pid = models.ForeignKey('self', blank=True, null=True, verbose_name=u'父级评论')

    class Meta:
        verbose_name = u'评论'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.id)


# 友情链接
class Links(models.Model):
    title = models.CharField(max_length=50, verbose_name=u'标题')
    description = models.CharField(max_length=200, verbose_name=u'友情链接描述')
    callback_url = models.URLField(verbose_name=u'地址')
    date_publish = models.DateTimeField(auto_now_add=True, verbose_name=u'发布时间')
    index = models.IntegerField(default=999, verbose_name=u'排列顺序(从小到大)')

    class Meta:
        verbose_name = u'友情链接'
        verbose_name_plural = verbose_name
        ordering = ['index', 'id']

    def __unicode__(self):
        return self.title


# 广告
class Ad(models.Model):
    title = models.CharField(max_length=50, verbose_name=u'广告标题')
    description = models.CharField(max_length=200, verbose_name=u'广告描述')
    image_url = models.ImageField(upload_to='ad/%Y/%m', storage=ImageStorage(), verbose_name=u'图片路径')
    callback_url = models.URLField(null=True, blank=True, verbose_name=u'回调URL')
    date_publish = models.DateTimeField(auto_now_add=True, verbose_name=u'发布时间')
    index = models.IntegerField(default=999, verbose_name=u'排列顺序(从小到大)')

    class Meta:
        verbose_name = u'广告'
        verbose_name_plural = verbose_name
        ordering = ['index', 'id']

    def __unicode__(self):
        return self.title
