# Generated by Django 5.1.2 on 2024-11-13 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_userprofile_bio_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='province',
            field=models.CharField(choices=[('Blagoevgrad', 'Blagoevgrad'), ('Burgas', 'Burgas'), ('Dobrich', 'Dobrich'), ('Gabrovo', 'Gabrovo'), ('Haskovo', 'Haskovo'), ('Kardzhali', 'Kardzhali'), ('Kyustendil', 'Kyustendil'), ('Lovech', 'Lovech'), ('Montana', 'Montana'), ('Pazardzhik', 'Pazardzhik'), ('Pernik', 'Pernik'), ('Pleven', 'Pleven'), ('Plovdiv', 'Plovdiv'), ('Razgrad', 'Razgrad'), ('Ruse', 'Ruse'), ('Shumen', 'Shumen'), ('Silistra', 'Silistra'), ('Sliven', 'Sliven'), ('Smolyan', 'Smolyan'), ('Sofia City', 'Sofia City'), ('Sofia Province', 'Sofia Province'), ('Stara Zagora', 'Stara Zagora'), ('Targovishte', 'Targovishte'), ('Varna', 'Varna'), ('Veliko Tarnovo', 'Veliko Tarnovo'), ('Vidin', 'Vidin'), ('Vratsa', 'Vratsa'), ('Yambol', 'Yambol')], default='Sofia Province', max_length=60),
        ),
    ]
