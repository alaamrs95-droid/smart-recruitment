# Generated migration for built resume models
# تم إنشاء هذا الملف لإضافة نماذج السير الذاتية المبنية

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('resumes', '0003_alter_resume_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuiltResume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Resume Title')),
                ('summary', models.TextField(verbose_name='Professional Summary')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('is_default', models.BooleanField(default=False, verbose_name='Default Resume')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='built_resumes', to='accounts.user')),
            ],
            options={
                'verbose_name': 'Built Resume',
                'verbose_name_plural': 'Built Resumes',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Phone')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Location')),
                ('linkedin', models.URLField(blank=True, verbose_name='LinkedIn Profile')),
                ('github', models.URLField(blank=True, verbose_name='GitHub Profile')),
                ('website', models.URLField(blank=True, verbose_name='Personal Website')),
                ('resume', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personal_info', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Personal Information',
                'verbose_name_plural': 'Personal Information',
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=200, verbose_name='Company')),
                ('position', models.CharField(max_length=200, verbose_name='Position')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('current_job', models.BooleanField(default=False, verbose_name='Current Job')),
                ('description', models.TextField(verbose_name='Job Description')),
                ('achievements', models.TextField(blank=True, verbose_name='Key Achievements')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Work Experience',
                'verbose_name_plural': 'Work Experiences',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200, verbose_name='Institution')),
                ('degree', models.CharField(max_length=100, verbose_name='Degree')),
                ('degree_type', models.CharField(choices=[('high_school', 'High School'), ('bachelor', "Bachelor's Degree"), ('master', "Master's Degree"), ('phd', 'PhD'), ('diploma', 'Diploma'), ('certificate', 'Certificate')], max_length=20, verbose_name='Degree Type')),
                ('field_of_study', models.CharField(max_length=200, verbose_name='Field of Study')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('current_study', models.BooleanField(default=False, verbose_name='Currently Studying')),
                ('gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='GPA')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Education',
                'verbose_name_plural': 'Education',
                'ordering': ['-end_date'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Skill Name')),
                ('level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('expert', 'Expert')], max_length=20, verbose_name='Skill Level')),
                ('years_of_experience', models.IntegerField(blank=True, null=True, verbose_name='Years of Experience')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Skill',
                'verbose_name_plural': 'Skills',
                'ordering': ['-years_of_experience', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Language')),
                ('level', models.CharField(choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('fluent', 'Fluent'), ('native', 'Native')], max_length=20, verbose_name='Proficiency Level')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='languages', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
                'ordering': ['-level', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Project Name')),
                ('description', models.TextField(verbose_name='Project Description')),
                ('technologies', models.CharField(max_length=500, verbose_name='Technologies Used')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('project_url', models.URLField(blank=True, verbose_name='Project URL')),
                ('github_url', models.URLField(blank=True, verbose_name='GitHub URL')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Certification Name')),
                ('issuing_organization', models.CharField(max_length=200, verbose_name='Issuing Organization')),
                ('issue_date', models.DateField(verbose_name='Issue Date')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='Expiry Date')),
                ('credential_id', models.CharField(blank=True, max_length=100, verbose_name='Credential ID')),
                ('credential_url', models.URLField(blank=True, verbose_name='Credential URL')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to='resumes.builtresume')),
            ],
            options={
                'verbose_name': 'Certification',
                'verbose_name_plural': 'Certifications',
                'ordering': ['-issue_date'],
            },
        ),
    ]
