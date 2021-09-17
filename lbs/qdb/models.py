from django.db import models


class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Units(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Staff, through = 'Recipients')

    def __str__(self):
        return self.name

class Recipients(models.Model):
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Staff, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    
    def __str__(self):
        return self.recipient

class Subcodes(models.Model):
    code = models.CharField(max_length=4)
    titles = models.TextField()
    notes = models.TextField()
    
    def __str__(self):
        return self.code
    
class Accounts(models.Model):
    account = CharField(max_length=6)
    cost_center = CharField(max_length=2)
    title = TextField()
    unit = models.ForeignKey(Units)

    def __str__(self):
        return self.account
