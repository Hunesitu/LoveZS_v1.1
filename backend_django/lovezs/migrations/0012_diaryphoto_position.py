from django.db import migrations, models


def preserve_attachment_order(apps, schema_editor):
    diary_photo = apps.get_model('lovezs', 'DiaryPhoto')
    diary_ids = diary_photo.objects.values_list('diary_id', flat=True).distinct()
    for diary_id in diary_ids.iterator():
        relations = diary_photo.objects.filter(diary_id=diary_id).order_by('attached_at', 'id')
        for position, relation in enumerate(relations):
            relation.position = position
            relation.save(update_fields=['position'])


class Migration(migrations.Migration):
    dependencies = [('lovezs', '0011_diaryfavorite')]

    operations = [
        migrations.AddField(
            model_name='diaryphoto',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name='显示顺序'),
        ),
        migrations.RunPython(preserve_attachment_order, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='diaryphoto',
            index=models.Index(fields=['diary', 'position'], name='lovezs_diar_diary_i_086ac2_idx'),
        ),
        migrations.AlterModelOptions(
            name='diaryphoto',
            options={'ordering': ['position', 'id'], 'verbose_name': '日记照片关联', 'verbose_name_plural': '日记照片关联'},
        ),
    ]
