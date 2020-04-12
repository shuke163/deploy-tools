#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: serializers.py 
@time: 2019/10/25 18:29
@contact: shu_ke163@163.com
@software:  Door
"""
from django.contrib.auth import authenticate
from rest_framework import serializers
from apps.account.models import Account
from rest_framework.authtoken.models import Token

import logging

logger = logging.getLogger("door")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    default_error_messages = {
        'inactive_account': 'User account is disabled.',
        'invalid_credentials': 'Unable to login with provided credentials.'
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(self.error_messages['inactive_account'])
            return attrs
        else:
            raise serializers.ValidationError(self.error_messages['invalid_credentials'])


class ResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = ("token", "created")


class SomeSerializer(serializers.Serializer):
    some_number = serializers.SerializerMethodField()

    def get_some_number(self, obj) -> float:
        return 1.0


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password']
