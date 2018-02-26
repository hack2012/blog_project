#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/2/23
# Created by 独自等待
# Blog: https://www.waitalone.cn/
import logging
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.db import connection
from django.conf import settings
from django.db.models import Count
from models import *
from forms import *

logger = logging.getLogger('blog.views')


# Create your views here.
def global_setting(request):
    # 站点基本信息
    SITE_URL = settings.SITE_URL
    SITE_NAME = settings.SITE_NAME
    SITE_DESC = settings.SITE_DESC
    WEBBO_SINA = settings.WEBBO_SINA
    WEBBO_TENCENT = settings.WEBBO_TENCENT
    PRO_RSS = settings.PRO_RSS
    PRO_EMAIL = settings.PRO_EMAIL
    # 分类信息获取(导航数据)
    category_list = Category.objects.all()
    # 文章归档数据
    archive_list = Article.objects.distinct_date()
    # 广告数据
    ads_list = Ad.objects.all()
    # 标签云数据
    tag_list = Tag.objects.all()
    # 友情链接数据
    link_list = Links.objects.all()
    # 文章排行榜
    article_count_list = Article.objects.all().order_by('-click_count')[:6]
    # 评论排行
    comment_count_list = Comment.objects.values('article').annotate(comment_count=Count('article')) \
        .order_by('-comment_count')
    article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_count_list]
    return locals()


def index(request):
    try:
        # 最新文章数据
        article_list = Article.objects.all()
        article_list = getPage(request, article_list)
        # 文章归档
        # 1、先要去获取到文章中有的 年份-月份 2018/02
        # 使用values和distinct去掉重复数据（不可行）
        # Article.objects.values('date_publish').distinct() #不适用
        # 直接执行原生sql
        # 第一种方式(不可行)
        # archiva_list = Article.objects.raw(
        #     'SELECT id, DATE_FORMAT(date_publish,"%%Y-%%m") AS col_date FROM blog_article ORDER BY date_publish'
        # ) # raw 返回结果必须要包含主键
        # for archive in archive_list:
        #     print archive
        # 第二种方式(不推荐)
        # cursor = connection.cursor()
        # cursor.execute(
        #     'SELECT DISTINCT DATE_FORMAT(date_publish,"%Y-%m") AS col_date FROM blog_article ORDER BY date_publish'
        # )
        # row = cursor.fetchall()
        # print row
    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())


def archive(request):
    try:
        # 先获取客户端提前的信息
        year = request.GET.get('year', None)
        month = request.GET.get('month', None)
        article_list = Article.objects.filter(date_publish__icontains=year + '-' + month)
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'archive.html', locals())


# 分页代码
def getPage(request, article_list):
    paginator = Paginator(article_list, 6)  # 分页数据
    try:
        page = int(request.GET.get('page', 1))
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list


# 文章详情
def article(request):
    try:
        # 获取文章id
        id = request.GET.get('id', None)
        try:
            # 获取文章信息
            article = Article.objects.get(pk=id)
            # 文章浏览量(点击量)
            num = article.click_count
            num += 1
            article.click_count = num
            article.save()
        except Article.DoesNotExist:
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})

        # 评论表单
        comment_form = CommentForm(
            {
                'author': request.user.username,
                'email': request.user.email,
                'url': request.user.url,
                'article': id
            } if request.user.is_authenticated() else {'article': id}
        )
        # 获取评论信息
        comments = Comment.objects.filter(article=article).order_by('id')
        comment_list = []
        for comment in comments:
            for item in comment_list:
                if not hasattr(item, 'children_comment'):
                    setattr(item, 'children_comment', [])
                if comment.pid == item:
                    item.children_comment.append(comment)
                    break
            if comment.pid is None:
                comment_list.append(comment)
    except Exception as e:
        print(e)
        logger.error(e)
    return render(request, 'article.html', locals())


# 提交评论
def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # 获取表单信息
            comment = Comment.objects.create(
                username=comment_form.cleaned_data["author"],
                email=comment_form.cleaned_data["email"],
                url=comment_form.cleaned_data["url"],
                content=comment_form.cleaned_data["comment"],
                article_id=comment_form.cleaned_data["article"],
                user=request.user if request.user.is_authenticated() else None
            )
            comment.save()
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])


# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])


# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(
                    username=reg_form.cleaned_data["username"],
                    email=reg_form.cleaned_data["email"],
                    url=reg_form.cleaned_data["url"],
                    password=make_password(reg_form.cleaned_data["password"]),
                )
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                login(request, user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        print e
        logger.error(e)
    return render(request, 'reg.html', locals())


# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        print e
        logger.error(e)
    return render(request, 'login.html', locals())


def category(request):
    try:
        # 先获取客户端提交的信息
        cid = request.GET.get('cid', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '分类不存在'})
        article_list = Article.objects.filter(category=category)
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())


def tags(request):
    try:
        # 先获取客户端提交的tag
        tag = request.GET.get('tag', None)
        article_list = Article.objects.filter(tag__name__icontains=tag)
        article_list = getPage(request, article_list)
    except Exception as e:
        print(e)
        logger.error(e)
    return render(request, 'tags.html', locals())
