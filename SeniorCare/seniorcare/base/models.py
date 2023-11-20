from django.db import models

class senior_list(models.Model):
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20)
    suffix = models.CharField(max_length=5, null=True)
    age = models.BigIntegerField(null=True)
    sex = models.CharField(max_length=10, null=True)
    birth_date = models.DateField(null=True)
    address = models.CharField(max_length=100, null=True)
    OSCA_ID = models.CharField(max_length=20, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_claimed = models.BooleanField(default=False)
    claimed_date = models.DateTimeField(null=True, blank=True)
    senior_image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f'senior_list {self.id}'
