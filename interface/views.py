import sys
import json
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Location
from geopy.geocoders import Nominatim

# Create your views here.
@ensure_csrf_cookie
def index(request):
    context = {
        'all_locations': Location.objects.order_by('locName')
    }
    return render(request, 'index.html', context)


def placequery(request):
    # Save the query string to the place in question
    qname = request.GET.get('q')
    locid = request.GET.get('for')
    thislocation = Location.objects.get(locationKey=locid)
    if qname != thislocation.locName:
        thislocation.queryName = qname
        thislocation.save()
    # Run the query
    candidates = None
    try:
        geolocator = Nominatim()
        result = geolocator.geocode(qname, exactly_one=False)
        if result is None:
            result = []
        candidates = [x.raw for x in result]
    except:
        errmsg = sys.exc_info()[0]
        return HttpResponseServerError(errmsg) 
    return HttpResponse(json.dumps(candidates), content_type='application/json')


def locationplace(request, locid):
    thislocation = Location.objects.get(locationKey=locid)
    if request.method == 'GET':
        # Return the OSM XML data if it exists
        xmldata = thislocation.osm_record
        if xmldata:
            return HttpResponse(xmldata, content_type='application/xml')
        else:
            raise Http404("No data for location")
    else:
        # Save the OSM XML data in request
        xmldata = request.body.decode('utf-8')
        thislocation.osm_record = xmldata
        thislocation.save()
        return HttpResponse('Success', content_type='text/plain')
