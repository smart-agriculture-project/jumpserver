# ~*~ coding: utf-8 ~*~
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from common.utils import pretty_string
from common.serializers.fields import LabeledChoiceField
from terminal.backends.command.models import AbstractSessionCommand
from terminal.models import Command

__all__ = ['SessionCommandSerializer', 'InsecureCommandAlertSerializer']


class SimpleSessionCommandSerializer(serializers.ModelSerializer):

    """ 简单Session命令序列类, 用来提取公共字段 """
    user = serializers.CharField(label=_("User"))  # 限制 64 字符，见 validate_user
    asset = serializers.CharField(max_length=128, label=_("Asset"))
    input = serializers.CharField(max_length=2048, label=_("Command"))
    session = serializers.CharField(max_length=36, label=_("Session ID"))
    risk_level = LabeledChoiceField(
        choices=AbstractSessionCommand.RiskLevelChoices.choices,
        required=False, label=_("Risk level"),
    )
    org_id = serializers.CharField(
        max_length=36, required=False, default='', allow_null=True, allow_blank=True
    )

    class Meta:
        # 继承 ModelSerializer 解决 swagger risk_level type 为 object 的问题
        model = Command
        fields = ['user', 'asset', 'input', 'session', 'risk_level', 'org_id']

    def validate_user(self, value):
        if len(value) > 64:
            value = value[:32] + value[-32:]
        return value


class InsecureCommandAlertSerializer(SimpleSessionCommandSerializer):
    pass


class SessionCommandSerializerMixin(serializers.Serializer):
    """使用这个类作为基础Command Log Serializer类, 用来序列化"""
    id = serializers.UUIDField(read_only=True)
    # 限制 64 字符，不能直接迁移成 128 字符，命令表数据量会比较大
    account = serializers.CharField(label=_("Account "))
    output = serializers.CharField(max_length=2048, allow_blank=True, label=_("Output"))
    timestamp = serializers.IntegerField(label=_('Timestamp'))
    timestamp_display = serializers.DateTimeField(read_only=True, label=_('Datetime'))
    remote_addr = serializers.CharField(read_only=True, label=_('Remote Address'))

    def validate_account(self, value):
        if len(value) > 64:
            value = pretty_string(value, 64)
        return value


class SessionCommandSerializer(SessionCommandSerializerMixin, SimpleSessionCommandSerializer):
    """ 字段排序序列类 """

    class Meta(SimpleSessionCommandSerializer.Meta):
        fields = SimpleSessionCommandSerializer.Meta.fields + [
            'id', 'account', 'output', 'timestamp', 'timestamp_display', 'remote_addr'
        ]

