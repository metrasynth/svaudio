import graphene

import svaudio.apps.repo.schema


class Query(svaudio.apps.repo.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
