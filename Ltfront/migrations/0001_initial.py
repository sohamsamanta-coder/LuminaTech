from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, unique=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Laptops", "Laptops"),
                            ("Smartphones", "Smartphones"),
                            ("Headphones", "Headphones"),
                            ("Televisions", "Televisions"),
                            ("Gaming", "Gaming"),
                            ("Accessories", "Accessories"),
                        ],
                        max_length=30,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("image", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]
