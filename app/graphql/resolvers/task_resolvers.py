def resolve_create_task(info, **kwargs):
    # Use kwargs to access optional fields
    # Example Cypher query to create a task node in Neo4j
    # Adjust query according to your data model and requirements
    create_query = """
    CREATE (t:Task {title: $title, description: $description, assignedTo: $assigned_to, dueDate: $due_date})
    RETURN t
    """
    # Execute Cypher query with provided kwargs
    # Return the newly created task node
    return {"task_id": "1", "title": kwargs.get("title"), "description": kwargs.get("description")}

def resolve_update_task(info, task_id, **kwargs):
    # Construct a Cypher query for updating a task based on provided attributes
    # This example demonstrates updating the title; extend it for other fields
    update_query = "MATCH (t:Task) WHERE id(t) = $task_id SET t += {kwargs} RETURN t"
    # Execute Cypher query with task_id and kwargs
    # Return the updated task node
    return {"task_id": task_id, "title": kwargs.get("title"), "description": kwargs.get("description")}
