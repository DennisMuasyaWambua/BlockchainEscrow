# Generated by Django 4.2.7 on 2025-02-12 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testcases', '0004_repo_created_at_repo_testcase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repo',
            name='testcase',
            field=models.FileField(blank=True, null=True, upload_to='workflows/'),
        ),
    ]
