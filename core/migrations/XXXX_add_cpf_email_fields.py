from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', 'previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmacia',
            name='cpf',
            field=models.CharField(blank=True, help_text='Digite o CPF no formato: 000.000.000-00', max_length=14, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='farmacia',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ] 