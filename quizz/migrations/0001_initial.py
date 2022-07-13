# Generated by Django 4.0.6 on 2022-07-07 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='QuizProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total Score')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizprofiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html', models.TextField(verbose_name='Question Text')),
                ('is_published', models.BooleanField(default=False, verbose_name='Has been published?')),
                ('maximum_marks', models.DecimalField(decimal_places=2, default=4, max_digits=6, verbose_name='Maximum Marks')),
                ('categorie', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='quizz.categorie')),
            ],
        ),
        migrations.CreateModel(
            name='Parcours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('categorie', models.ManyToManyField(related_name='parcourss', to='quizz.categorie')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Is this answer correct?')),
                ('html', models.TextField(verbose_name='Choice Text')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='quizz.question')),
            ],
        ),
        migrations.CreateModel(
            name='AttemptedQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Was this attempt correct?')),
                ('marks_obtained', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Marks Obtained')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizz.question')),
                ('quiz_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='quizz.quizprofile')),
                ('selected_choice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='quizz.choice')),
            ],
        ),
    ]
