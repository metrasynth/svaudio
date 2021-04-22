import graphene

import svaudio.repo.schema


class Query(svaudio.repo.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
