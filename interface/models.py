from django.db import models


# Create your models here.
class Location(models.Model):
    locationKey = models.AutoField(primary_key=True)
    locName = models.CharField(max_length=100, default='')
    oLangKey = models.SmallIntegerField(default=0)
    locNameOL = models.CharField(max_length=100, null=True)
    extraInfo = models.CharField(max_length=100, null=True)
    notes = models.TextField(null=True)
    resolved = models.BooleanField(default=False)
    latitude = models.CharField(max_length=100, null=True)
    longitude = models.CharField(max_length=100, null=True)
    radius = models.CharField(max_length=100, null=True)
    osm_id = models.BigIntegerField(null=True)
    osm_record = models.TextField(null=True)
    queryName = models.CharField(max_length=100, default='')


    def __str__(self):
        return self.locName

    class Meta:
        db_table = 'location'
