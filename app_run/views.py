from django.shortcuts import render
from django.http import JsonResponse


def company_details_view(request):
    return JsonResponse({
        'company_name': 'Runners for the values',
        'slogan':'Anywhere, anytime, anywhat...',
        'contacts':'city-district-country'
    })
