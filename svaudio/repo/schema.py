from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from . import models as m


class FileNode(DjangoObjectType):
    class Meta:
        model = m.File
        interfaces = (relay.Node,)
        filter_fields = [
            "hash",
            "file_type",
            "size",
            "cached_at",
            "last_accessed_at",
        ]


class Query(ObjectType):
    file = relay.Node.Field(FileNode)
    all_files = DjangoFilterConnectionField(FileNode)
