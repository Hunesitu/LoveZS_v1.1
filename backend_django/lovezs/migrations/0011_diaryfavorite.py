from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('lovezs', '0010_alter_diary_options_diary_is_pinned_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaryFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
                ('diary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='lovezs.diary', verbose_name='日记')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_diaries', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '日记收藏',
                'verbose_name_plural': '日记收藏',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', '-created_at'], name='lovezs_diar_user_id_8ff242_idx')],
                'constraints': [models.UniqueConstraint(fields=('user', 'diary'), name='unique_user_diary_favorite')],
            },
        ),
    ]
