import ast
import sys
import time
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

import sqlparse
from django.apps import apps
from django.db import connection


def get_schema() -> List[Dict[str, Any]]:
    """
    Retrieves the database schema for the 'playground' app.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a model
        and its fields.
    """
    schema = []
    try:
        app_config = apps.get_app_config('playground')
        for model in app_config.get_models():
            fields_data = []
            for field in model._meta.get_fields():
                related_model = None
                related_name = None
                is_reverse = False
                
                # Determine field type and related model
                if field.is_relation:
                    if field.related_model:
                        related_model = field.related_model.__name__
                    
                    # Try to get related_name
                    if hasattr(field, 'related_name'):
                        related_name = field.related_name
                    elif hasattr(field, 'remote_field') and field.remote_field:
                         related_name = field.remote_field.related_name
                    
                    if field.many_to_many:
                        field_type = 'ManyToMany'
                        if not field.concrete:
                            is_reverse = True
                    elif field.one_to_many:
                        field_type = 'Reverse ManyToOne'
                        is_reverse = True
                        # For reverse relations, the "name" is the accessor
                        if hasattr(field, 'get_accessor_name'):
                             related_name = field.get_accessor_name()
                    elif field.one_to_one:
                        field_type = 'OneToOne'
                        if not field.concrete:
                            is_reverse = True
                    elif field.many_to_one:
                        field_type = 'Foreign Key'
                    else:
                        field_type = 'Relation'
                else:
                    # Use class name to catch EmailField, etc.
                    internal_type = field.get_internal_type()
                    class_name = field.__class__.__name__
                    
                    # Mapping to user-friendly names
                    type_mapping = {
                        'CharField': 'Character',
                        'EmailField': 'Email',
                        'IntegerField': 'Integer',
                        'DateField': 'Date',
                        'DateTimeField': 'DateTime',
                        'BooleanField': 'Boolean',
                        'DecimalField': 'Decimal',
                        'TextField': 'Text',
                        'BigAutoField': 'ID',
                        'BigAutoField': 'ID',
                    }
                    
                    # Prefer class name for mapping (e.g. EmailField)
                    base_type = type_mapping.get(class_name, type_mapping.get(internal_type, internal_type))
                    
                    field_type = base_type
                    
                    if internal_type == 'CharField':
                        field_type += f" ({field.max_length})"
                    elif internal_type == 'DecimalField':
                        field_type += f" ({field.max_digits}, {field.decimal_places})"
                
                # Add null/blank info
                if field.null:
                    field_type += " (null)"
                
                fields_data.append({
                    'name': field.name,
                    'data_type': field_type,
                    'related_model': related_model,
                    'related_name': related_name,
                    'is_relation': field.is_relation,
                    'is_reverse': is_reverse
                })
            
            # Sort fields: Regular first, then Forward Relations, then Reverse Relations
            fields_data.sort(key=lambda x: (x['is_relation'], x['is_reverse'], x['name']))

            schema.append({
                'name': model.__name__,
                'fields': fields_data
            })
    except LookupError:
        pass
    return schema


def execute_code(code: str) -> Tuple[Optional[str], List[Dict[str, Any]], Optional[float]]:
    """
    Executes the provided Python code and captures the output and SQL queries.

    Args:
        code (str): The Python code to execute.

    Returns:
        Tuple[Optional[str], List[Dict[str, Any]], Optional[float]]: A tuple containing:
            - result (str): The captured stdout output.
            - queries (List[Dict]): A list of executed SQL queries with timing.
            - execution_time (float): The time taken to execute the code.
    """
    result = None
    queries = []
    execution_time = None

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    start_time = time.time()
    try:
        # Create a fresh execution context
        context = {}
        
        # Parse the code
        tree = ast.parse(code)
        
        # Check if the last node is an expression
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            # Separate the last expression
            last_expr = tree.body.pop()
            
            # compile and execute the preceding code
            if tree.body:
                exec(compile(tree, filename="<string>", mode="exec"), context)
            
            # Evaluate the last expression
            expr_val = eval(compile(ast.Expression(last_expr.value), filename="<string>", mode="eval"), context)
            if expr_val is not None:
                print(expr_val)
        else:
            # Execute normally if no trailing expression
            exec(code, context)
            
    except Exception as e:
        print(f"Error: {e}")
    
    end_time = time.time()
    execution_time = round(end_time - start_time, 4)

    # Restore stdout
    sys.stdout = old_stdout
    result = mystdout.getvalue()

    # Capture queries
    queries = [{
        'sql': sqlparse.format(q['sql'], reindent=True, keyword_case='upper'),
        'time': q['time']
    } for q in connection.queries]

    return result, queries, execution_time
