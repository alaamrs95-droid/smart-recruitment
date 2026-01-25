# Generated migration for CandidateResumeProfile model
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0004_add_built_resume_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateResumeProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_resume_type', models.CharField(choices=[('uploaded', 'Uploaded Resume'), ('built', 'Built Resume'), ('both', 'Both - Prioritize Built')], default='uploaded', help_text='Which resume type to prioritize for matching', max_length=10, verbose_name='Primary Resume Type')),
                ('is_active_for_matching', models.BooleanField(default=True, verbose_name='Active for Matching')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('built_resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profile_primary', to='resumes.builtresume', verbose_name='Built Resume')),
                ('candidate', models.OneToOneField(limit_choices_to={'role': 'candidate'}, on_delete=django.db.models.deletion.CASCADE, related_name='resume_profile', to=settings.AUTH_USER_MODEL, verbose_name='Candidate')),
                ('uploaded_resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profile_primary', to='resumes.resume', verbose_name='Uploaded Resume')),
            ],
            options={
                'verbose_name': 'Candidate Resume Profile',
                'verbose_name_plural': 'Candidate Resume Profiles',
            },
        ),
    ]
