from django.db import migrations

def set_confident_flags(apps, schema_editor):
    Ad = apps.get_model("ads", "Ad")
    # Для всех старых объявлений ставим False
    Ad.objects.update(is_confident=False)

class Migration(migrations.Migration):

    dependencies = [
        ('ads', '000X_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='is_confident',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_confident_flags),
    ]
