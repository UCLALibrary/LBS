from django.db import models


class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Staff, through = 'Recipient')

    def __str__(self):
        return self.name

class Recipient(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Staff, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

class Subcode(models.Model):
    code = models.CharField(max_length=4)
    titles = models.TextField()
    notes = models.TextField()
