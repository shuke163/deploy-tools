#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: serializers.py 
@time: 2019/10/25 18:29
@contact: shu_ke163@163.com
@software:  Door
"""
from django.forms.models import model_to_dict
from collections import defaultdict
from rest_framework import serializers
from apps.deploy.models import Service, BusinessLine, DeployModels, ConfigMap

import logging

logger = logging.getLogger("door")


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# >>> class UserSerializer(DynamicFieldsModelSerializer):
# >>>     class Meta:
# >>>         model = User
# >>>         fields = ['id', 'username', 'email']
# >>>
# >>> print(UserSerializer(user))
# {'id': 2, 'username': 'jonwatts', 'email': 'jon@example.com'}
# >>>
# >>> print(UserSerializer(user, fields=('id', 'email')))
# {'id': 2, 'email': 'jon@example.com'}

class BusinessSerializer(serializers.ModelSerializer):
    """
    business serializer
    """

    class Meta:
        model = BusinessLine
        fields = '__all__'

    def create(self, validated_data):
        name = validated_data.get("name", None)

        instance = super().create(validated_data)
        # instance = BusinessLine.objects.create(**validated_data)

        return instance

    def update(self, instance, validated_data):
        name = self.context["request"].data.get("name")
        id = self.context["request"].data.get("id")

        # business = BusinessLine.objects.get(id=id)
        for (key, val) in validated_data.items():
            setattr(instance, key, val)

        instance.save()

        return instance


class ServiceDynamicFieldsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class DeployModelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeployModels
        fields = '__all__'


class ConfigMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigMap
        fields = '__all__'


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigMap
        fields = ('title', 'value',)


class ServiceSerializer(serializers.ModelSerializer):
    # business_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = '__all__'
        depth = 1

    # def get_business_name(self, obj):
    #     return obj.business.name

    # 增加序列化字段
    def to_representation(self, instance):
        ret = super(ServiceSerializer, self).to_representation(instance)
        # roles_query_set = instance.role
        #
        # result = defaultdict(list)
        # if roles_query_set is not None:
        #     roles_query_set = instance.role.all()
        #     for item in roles_query_set:
        #         result["roles"].append({"id": item.id, "name": item.name, "description": item.description})

        business = instance.business
        if business:
            ret['business'] = {'id': business.id, 'name': business.name} if business else {}
        # ret.update(result)
        return ret

    def create(self, validated_data):
        instance = Service.objects.create(**validated_data)

        return instance

    def update(self, instance, validated_data):
        business_id = self.context.get("business", None)
        business = BusinessLine.objects.get(pk=business_id)
        logger.info(f"business id: {business_id}")
        for (key, val) in validated_data.items():
            setattr(instance, key, val)

        setattr(instance, "business", business)
        instance.save()

        return instance

    def validate(self, attrs):
        if attrs.get("name", None) is None:
            raise serializers.ValidationError(
                'name fields is required.'
            )
        if attrs.get("description", None) is None:
            raise serializers.ValidationError(
                'description fields is required.'
            )
        return attrs
