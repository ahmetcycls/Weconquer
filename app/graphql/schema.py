import graphene

from app.graphql.resolvers.task_resolvers import resolve_create_task, resolve_update_task
from app.domain.task_tree.models import Task

# Task Input Type for Create and Update Operations
class TaskInput(graphene.InputObjectType):
    title = graphene.String()
    description = graphene.String()
    assigned_to = graphene.String()
    due_date = graphene.DateTime()

# Mutation to Create a New Task
class CreateTask(graphene.Mutation):
    class Arguments:
        task_data = TaskInput(required=True)

    task = graphene.Field(Task)  # Assuming you have a Task ObjectType defined

    def mutate(root, info, task_data):
        # Logic to handle task creation, considering optional fields
        task = resolve_create_task(info, **task_data)
        return CreateTask(task=task)

# Mutation to Update an Existing Task
class UpdateTask(graphene.Mutation):
    class Arguments:
        task_id = graphene.ID(required=True)
        task_data = TaskInput(required=True)

    task = graphene.Field(Task)

    def mutate(root, info, task_id, task_data):
        # Logic to handle task update, allowing partial updates
        task = resolve_update_task(info, task_id, **task_data)
        return UpdateTask(task=task)

class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
