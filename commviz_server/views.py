from django.http import HttpResponse
# from django.shortcuts import render

#はじめてのビュー作成
def index(request):
    with open("/home/ryotani/Documents/work/datamining-chat/CommViz/d3graph_sample.html") as f:
        htmldata = f.readlines()

    # render(request, "/home/ryotani/Documents/work/datamining-chat/CommViz/d3graph_sample.html")
    return HttpResponse(htmldata)