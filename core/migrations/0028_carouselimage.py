# Generated manually for carousel image feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_populate_leadership_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarouselImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Image title/description', max_length=200)),
                ('image', models.ImageField(help_text='Carousel image (recommended: 1200x400px)', upload_to='carousel/')),
                ('order', models.IntegerField(default=0, help_text='Display order (lower numbers appear first)')),
                ('is_active', models.BooleanField(default=True, help_text='Show this image in the carousel')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Carousel Image',
                'verbose_name_plural': 'Carousel Images',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
