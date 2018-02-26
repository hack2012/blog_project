#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/2/24
# Created by 独自等待
# Blog: https://www.waitalone.cn/
from django import template

register = template.Library()


# 定义一个将日期中的月份转换为大写的过滤器，如8转换为八
@register.filter
def month_to_upper(key):
    print key.month
    return ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'][key.month - 1]

# 注册过滤器
# register.filter('month_to_upper',month_to_upper)
