from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from playground.services import get_schema, execute_code

def index(request: HttpRequest) -> HttpResponse:
    """
    Renders the playground page and handles code execution requests.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page or JSON response.
    """
    result = None
    queries = []
    execution_time = None
    code = request.POST.get('code', '')

    if request.method == 'POST' and code:
        result, queries, execution_time = execute_code(code)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'result': result,
                'queries': queries,
                'execution_time': execution_time
            })
            
    if not code:
        code = "from playground.models import Book, Author\n\n# Example: Get all books\nBook.objects.all()"

    return render(request, 'playground/index.html', {
        'code': code,
        'result': result,
        'queries': queries,
        'execution_time': execution_time,
        'schema': get_schema()
    })

