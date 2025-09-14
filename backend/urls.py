"""
URL configuration for ecommerce_transaction_using_BigQuery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import scalability_results, save_simulation_results, get_simulation_results, save_query_simulation_results, get_query_simulation_results,execute_bigquery

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scalability/', scalability_results, name='scalability_results'),
    path('save_simulation_results/', save_simulation_results, name='save_simulation_results'),
    path('simulation_results/', get_simulation_results, name='simulation_results'),
    path('execute_bigquery/', execute_bigquery, name='execute_bigquery'),
    path('save_query_simulation_results/', save_query_simulation_results, name='save_query_simulation_results'),
    path('get_query_simulation_results/', get_query_simulation_results, name='get_query_simulation_results'),
]

