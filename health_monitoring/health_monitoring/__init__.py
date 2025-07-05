import pymysql
pymysql.install_as_MySQLdb()

from django.shortcuts import render

def index(request):
    return render(request, 'healthapp/index.html')