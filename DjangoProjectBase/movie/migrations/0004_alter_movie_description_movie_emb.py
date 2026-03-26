# Generated migration for Workshop 3 AI integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0003_alter_movie_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='movie',
            name='emb',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
