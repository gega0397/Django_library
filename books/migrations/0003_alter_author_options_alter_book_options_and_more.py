# Generated by Django 5.0.6 on 2024-05-26 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0002_borrow_returned_reserve_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="author",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["id"]},
        ),
        migrations.AlterModelOptions(
            name="genre",
            options={"ordering": ["name"]},
        ),
        migrations.AlterField(
            model_name="reserve",
            name="status",
            field=models.BooleanField(default=True, verbose_name="Status"),
        ),
    ]
