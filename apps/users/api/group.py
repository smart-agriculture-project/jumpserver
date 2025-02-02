# -*- coding: utf-8 -*-
#
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from orgs.mixins.api import OrgBulkModelViewSet
from ..models import UserGroup, User
from ..serializers import UserGroupSerializer

__all__ = ['UserGroupViewSet']


class UserGroupViewSet(OrgBulkModelViewSet):
    model = UserGroup
    filterset_fields = ("name",)
    search_fields = filterset_fields
    serializer_class = UserGroupSerializer
    ordering = ('name',)
    rbac_perms = (
        ("add_all_users", "users.change_usergroup"),
    )

    @action(methods=['post'], detail=True, url_path='add-all-users')
    def add_all_users(self, request, *args, **kwargs):
        instance = self.get_object()
        users = User.get_org_users().exclude(groups__id=instance.id)
        instance.users.add(*users)
        return Response(status=status.HTTP_200_OK)
