# Generated migration to fix foreign key references after restructuring

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateresumeprofile',
            name='uploaded_resume',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='profile_primary',
                to='resumes.resume',
                verbose_name='Uploaded Resume'
            ),
        ),
        migrations.AlterField(
            model_name='candidateresumeprofile',
            name='built_resume',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='profile_primary',
                to='resumes.builtresume',
                verbose_name='Built Resume'
            ),
        ),
    ]
