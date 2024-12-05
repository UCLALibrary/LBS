from django.db import models


class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Staff"

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Staff, through="Recipient")

    def __str__(self):
        return self.name


class Recipient(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Staff, on_delete=models.CASCADE)
    role_choices = [("aul", "AUL"), ("head", "Head"), ("assoc", "Assoc")]
    role = models.CharField(max_length=100, choices=role_choices)

    def __str__(self):
        return self.recipient.name


class Subcode(models.Model):
    code = models.CharField(max_length=4)
    titles = models.TextField()
    notes = models.TextField()

    def __str__(self):
        return self.code


class Account(models.Model):
    account = models.CharField(max_length=6)
    cost_center = models.CharField(max_length=2)
    title = models.TextField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.account


class CronJob(models.Model):
    # Use charfield to support wildcards and intervals.
    # No attempt at validation.
    # Set reasonable defaults for midnight Jan 1 (any day of week),
    # basic echo command, with job disabled.
    # 0 0 1 1 * echo 'Hello' >> /tmp/cron.log 2>&1
    minutes = models.CharField(max_length=20, null=False, blank=False, default="0")
    hours = models.CharField(max_length=20, null=False, blank=False, default="0")
    days_of_month = models.CharField(
        max_length=20, null=False, blank=False, default="1"
    )
    months = models.CharField(max_length=20, null=False, blank=False, default="1")
    days_of_week = models.CharField(max_length=20, null=False, blank=False, default="*")
    command = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        default="echo 'Hello' >> /tmp/cron.log 2>&1",
    )
    enabled = models.BooleanField(null=False, default=False)
    # With custom save(), ensure there's only one record, with pk = 1:
    # each new record replaces the previous (and only) one.
    permanent_id = models.SmallIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.pk = self.permanent_id
        super().save(*args, **kwargs)
