import graphene
from .resolvers.task_resolvers import create_task

class TaskInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    description = graphene.String()
    parent_id = graphene.ID()  # Optional parent ID for creating subtasks

class CreateTask(graphene.Mutation):
    class Arguments:
        task_data = TaskInput(required=True)

    success = graphene.Boolean()
    task_id = graphene.ID()

    def mutate(self, info, task_data):
        task_id = create_task(**task_data)
        return CreateTask(success=True, task_id=task_id)

class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()

schema = graphene.Schema(mutation=Mutation)
