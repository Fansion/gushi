# coding: utf-8

class Permission:

    """定义系统当前操作对应的权限"""
    REPOST = 0x02
    UPVOTE = 0x04
    SHARE = 0x08
    FOLLOW = 0x10
    ADMINISTER = 0x80
