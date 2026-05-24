# Generated manually to shorten homepage carousel timing.

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_tribe_ckeditor5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='carousel_duration',
            field=models.IntegerField(
                default=3000,
                help_text='Carousel image duration in milliseconds (default: 3000 = 3 seconds). Minimum: 2000ms (2 seconds)',
                validators=[django.core.validators.MinValueValidator(2000)],
            ),
        ),
    ]
