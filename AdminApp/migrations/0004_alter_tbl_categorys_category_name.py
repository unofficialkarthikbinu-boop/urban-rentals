# Generated migration to add unique constraint to category_name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0003_tbl_categorys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbl_categorys',
            name='category_name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
    ]
