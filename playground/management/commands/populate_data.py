import random
from datetime import timedelta
from typing import List

from django.core.management.base import BaseCommand
from django.utils import timezone
from playground.models import Author, Book, Rating, Review


class Command(BaseCommand):
    help = 'Populates the database with sample book/author data'

    FIRST_NAMES = ['George', 'J.K.', 'Stephen', 'Agatha', 'Tolkien', 'Jane']
    LAST_NAMES = ['Orwell', 'Rowling', 'King', 'Christie', 'Tolkien', 'Austen']
    ADJECTIVES = ['Mysterious', 'Dark', 'Happy', 'Ancient', 'Future']
    NOUNS = ['Journey', 'Secret', 'Life', 'World', 'Galaxy']

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        self._delete_old_data()

        self.stdout.write('Creating Authors...')
        authors = self._create_authors()

        self.stdout.write('Creating Books...')
        books = self._create_books(authors)

        self.stdout.write('Creating Reviews and Ratings...')
        self._create_reviews_and_ratings(books)

        self.stdout.write(self.style.SUCCESS('Data populated successfully'))

    def _delete_old_data(self):
        """Deletes all existing data from the playground models."""
        models = [Author, Book, Rating, Review]
        for m in models:
            m.objects.all().delete()

    def _create_authors(self) -> List[Author]:
        """Creates and returns a list of 10 sample authors."""
        authors = []
        for i in range(10):
            author = Author.objects.create(
                first_name=random.choice(self.FIRST_NAMES),
                last_name=random.choice(self.LAST_NAMES) + f" {i}",
                birth_date=timezone.now().date() - timedelta(days=random.randint(10000, 30000)),
                email=f"author{i}@example.com"
            )
            authors.append(author)
        return authors

    def _create_books(self, authors: List[Author]) -> List[Book]:
        """Creates and returns a list of 30 sample books."""
        books = []
        for i in range(30):
            title = f"The {random.choice(self.ADJECTIVES)} {random.choice(self.NOUNS)} {i}"
            book = Book.objects.create(
                title=title,
                description=f"A wonderful book about {title}.",
                published_date=timezone.now().date() - timedelta(days=random.randint(100, 5000)),
                isbn=f"978-{random.randint(1000000000, 9999999999)}",
                price=random.randint(10, 50),
                is_bestseller=random.choice([True, False]),
                author=random.choice(authors)
            )
            books.append(book)
        return books

    def _create_reviews_and_ratings(self, books: List[Book]):
        """Creates random reviews and ratings for the given books."""
        for book in books:
            # Create 0-5 reviews per book
            for _ in range(random.randint(0, 5)):
                Review.objects.create(
                    book=book,
                    reviewer_name=f"Reader {random.randint(1, 100)}",
                    content="I couldn't put it down!",
                    date=timezone.now()
                )
            
            # Create 0-10 ratings per book
            for _ in range(random.randint(0, 10)):
                Rating.objects.create(
                    book=book,
                    score=random.randint(1, 5),
                    date=timezone.now()
                )
