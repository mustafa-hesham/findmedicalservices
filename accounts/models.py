from django.db import models
from services.models import CustomUser, PhoneNumbers, Governorates, service, reservation
# Create your models here.
class ServiceCount(models.Model):

    userObj       = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    service_name  = models.CharField(max_length = 20)
    service_count = models.IntegerField(default = 1)

    def __str__(self):
        return self.userObj.name + ' '+self.service_name

    
