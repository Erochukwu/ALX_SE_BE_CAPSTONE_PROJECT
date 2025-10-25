from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='Shed',
            name='domain',
            field=models.CharField(
                max_length=2,
                choices=[
                    ('CB', 'Clothings and Beddings'),
                    ('EC', 'Electronics and Computer wares'),
                    ('FB', 'Food and Beverages'),
                    ('JA', 'Jewelry and Accessories'),
                ],
                default='CB',  # Temporary default for existing records
                help_text="Category/domain of the shed."
            ),
        ),
    ]