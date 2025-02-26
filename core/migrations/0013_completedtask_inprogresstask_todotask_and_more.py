# Generated by Django 4.2.13 on 2024-06-17 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_task'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedTask',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='InProgressTask',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.task',),
        ),
        migrations.CreateModel(
            name='TodoTask',
            fields=[
            ],
            options={
                'ordering': ('created_at',),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.task',),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='nickname',
            field=models.CharField(default='', max_length=255),
        ),
    ]
