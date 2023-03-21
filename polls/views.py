from django.http import HttpResponse

sampleHTML = open("polls/sample.html",encoding="utf-8").read()
# print(sampleHTML)
def index(request):
    return HttpResponse(sampleHTML)
