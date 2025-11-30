from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    """
    Represents an author of books.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'author'


class Book(models.Model):
    """
    Represents a book written by an author.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_bestseller = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'


class Review(models.Model):
    """
    Represents a text review for a book.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.book.title} by {self.reviewer_name}"

    class Meta:
        db_table = 'review'


class Rating(models.Model):
    """
    Represents a numeric rating (1-5) for a book.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.score}/5 for {self.book.title}"

    class Meta:
        db_table = 'rating'