import os
import django
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orm_series.settings')
django.setup()

from core.models import Author, Book, Review, Rating

def get_schema_debug():
    for model in [Author, Book, Review, Rating]:
        print(f"Model: {model.__name__}")
        for field in model._meta.get_fields():
            internal_type = field.get_internal_type()
            print(f"  Field: {field.name}, Internal Type: {internal_type}, Class: {field.__class__.__name__}")
            if field.is_relation:
                print(f"    Is Relation: True, ManyToOne: {field.many_to_one}")

get_schema_debug()
