from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_pinnedmessage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='title',
            new_name='name_kg',
        ),
        migrations.AddField(
            model_name='category',
            name='ru_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ] 