from django.contrib import admin
from playground.models import Author, Book, Review, Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['book', 'score', 'date']