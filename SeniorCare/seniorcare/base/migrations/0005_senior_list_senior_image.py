# Generated by Django 4.2.7 on 2023-11-20 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_delete_example'),
    ]

    operations = [
        migrations.AddField(
            model_name='senior_list',
            name='senior_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
