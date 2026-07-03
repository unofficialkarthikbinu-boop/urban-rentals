# Generated migration for return request system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CustomerApp', '0007_tbl_review'),
        ('GuestApp', '0004_tbl_vendor_gstin'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_return_request',
            fields=[
                ('return_id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('requested', 'Return Requested'), ('scheduled', 'Pickup Scheduled'), ('picked_up', 'Item Picked Up'), ('completed', 'Return Completed'), ('cancelled', 'Cancelled')], default='requested', max_length=20)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('pickup_scheduled_date', models.DateTimeField(blank=True, null=True)),
                ('pickup_completed_date', models.DateTimeField(blank=True, null=True)),
                ('actual_return_date', models.DateField(blank=True, help_text='Date when customer returns the product', null=True)),
                ('defect_status', models.CharField(choices=[('no_defect', 'No Defect'), ('minor', 'Minor Defect (5% deduction)'), ('moderate', 'Moderate Defect (15% deduction)'), ('major', 'Major Defect (30% deduction)')], default='no_defect', max_length=20)),
                ('defect_description', models.TextField(blank=True, null=True)),
                ('defect_image', models.ImageField(blank=True, null=True, upload_to='return_defect_images/')),
                ('extra_days', models.IntegerField(default=0, help_text='Days beyond the scheduled rental period')),
                ('defect_deduction_percentage', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage deducted for defects (e.g., 5, 15, 30)', max_digits=5)),
                ('defect_deduction_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('extra_days_deduction_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total deduction for extra days', max_digits=10)),
                ('total_deduction', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='GuestApp.tbl_customer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='CustomerApp.tbl_order')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='CustomerApp.tbl_order_item')),
            ],
            options={
                'verbose_name': 'Return Request',
                'verbose_name_plural': 'Return Requests',
                'db_table': 'tbl_return_request',
                'ordering': ['-request_date'],
            },
        ),
    ]
