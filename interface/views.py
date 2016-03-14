import json
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Location
from geopy.geocoders import Nominatim

TESTRESULT = [{"class": "historic", "display_name": "Ani",
               "boundingbox": ["40.4999752", "40.5124925", "43.5658492", "43.5797752"],
               "osm_id": "157441696", "osm_type": "way", "type": "ruins",
               "lat": "40.5062237", "lon": "43.5743956004602"},
              {"class": "place", "display_name": "Anush",
               "icon": "https://nominatim.openstreetmap.org/images/mapicons/poi_place_village.p.20.png",
               "boundingbox": ["31.3297", "31.3697", "77.403", "77.443"],
               "osm_id": "245771732", "osm_type": "node", "type": "village",
               "lat": "31.3497", "lon": "77.423"}]


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
        candidates = TESTRESULT
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
