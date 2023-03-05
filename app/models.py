from django.db import models


# Create your models here.
class Artist(models.Model):

    artist_id = models.CharField(max_length=15, primary_key=True)
    monthly_listeners = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.artist_id} - {self.monthly_listeners}"
