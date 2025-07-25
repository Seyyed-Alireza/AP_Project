# Generated by Django 5.2.4 on 2025-07-24 20:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_searchhistory_searched_at'),
        ('mainpage', '0009_product_likes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('interaction_type', models.CharField(choices=[('view', 'View'), ('like', 'Like'), ('wishlist', 'Wishlist'), ('cart', 'Cart')], max_length=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='browsing_histories', to='mainpage.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='browsing_histories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
