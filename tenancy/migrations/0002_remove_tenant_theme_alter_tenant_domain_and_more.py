from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE tenancy_tenant DROP COLUMN IF EXISTS theme;",
                    reverse_sql="ALTER TABLE tenancy_tenant ADD COLUMN theme varchar(100) NULL;"
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE tenancy_tenant DROP COLUMN IF EXISTS domain;",
                    reverse_sql="ALTER TABLE tenancy_tenant ADD COLUMN domain varchar(255) NULL;"
                ),
            ],
            state_operations=[
                # Modelde bu alanlar yok; state'e dokunmuyoruz.
            ],
        ),
        # 0002’de theme/domain dışındaki işlemler varsa onları bırak.
    ]
