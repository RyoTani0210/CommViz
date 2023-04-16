from django.http import HttpResponse

#はじめてのビュー作成
def index(request):
    return HttpResponse("Hello, world. You're at the main index.")