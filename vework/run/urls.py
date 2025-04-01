from django.urls import path
from .views import index, pricing_details, generate_marketing_pdf

urlpatterns = [
    path("", index, name="index"),
    path("pricing_details/", pricing_details, name="pricing_details"),
    path('generate_pdf/', generate_marketing_pdf, name="pdf")
]
