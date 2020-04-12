#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: serializers.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/14 11:14
@software:  Door
"""

from rest_framework import serializers
from apps.host.models import Host, HostGroup
from apps.host.models import SvcValidateModel

import logging

logger = logging.getLogger("door")


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(HostSerializer, self).to_representation(instance)
        groups = instance.group
        ret['host_group'] = {'id': groups.id, 'name': groups.name} if groups else {}

        return ret

    def create(self, validated_data):
        instance = Host.objects.create(**validated_data)
        return instance

    # def update(self, instance, validated_data):
    #     group_id = self.context.get("group", None)
    #     group = Host.objects.get(pk=group_id)
    #     logger.info(f"group id: {group_id}")
    #     for (key, val) in validated_data.items():
    #         setattr(instance, key, val)
    #
    #     setattr(instance, "group", group)
    #     instance.save()l
    #
    #     return instance


class HostGroupSerializer(serializers.ModelSerializer):
    # group_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = HostGroup
        fields = '__all__'
        depth = 1

    # def get_group_name(self, obj):
    #     return obj.super_group.name

    # 增加返回字段
    def to_representation(self, instance):
        ret = super(HostGroupSerializer, self).to_representation(instance)
        super_group = instance.super_group
        ret['groups'] = {'id': super_group.id, 'name': super_group.name} if super_group else {}

        return ret

    def create(self, validated_data):
        instance = HostGroup.objects.create(**validated_data)

        return instance

    def update(self, instance, validated_data):
        group_id = self.context.get("group", None)
        group = HostGroup.objects.get(pk=group_id)
        logger.info(f"group id: {group_id}")
        for (key, val) in validated_data.items():
            setattr(instance, key, val)

        setattr(instance, "super_group", group)
        instance.save()

        return instance

class SvcValidateModelsSerializer(serializers.ModelSerializer):
    """
    svc check model serializer
    """
    instance_name = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SvcValidateModel 
        fields = ('business', 'server_name', 'hostname', 'instance_name', 'status')

    def get_instance_name(self, obj):
        
        instance_name_list = [obj.instance_name, ]
        return instance_name_list

    def get_status(self, obj):
        return obj.get_state_display()


