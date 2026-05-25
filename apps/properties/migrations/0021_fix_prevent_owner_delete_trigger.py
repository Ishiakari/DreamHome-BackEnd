from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0020_add_rejected_property_status'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION prevent_owner_delete_with_active_properties()
                RETURNS TRIGGER AS $$
                DECLARE
                    v_active_count INTEGER;
                BEGIN
                    IF OLD.role = 'Owner' THEN
                        SELECT COUNT(*) INTO v_active_count
                        FROM property
                        WHERE owner_no_id = OLD.client_no
                          AND status IN ('Available', 'Rented');

                        IF v_active_count > 0 THEN
                            RAISE EXCEPTION 'Cannot delete owner % — they still have % active propert(ies). Withdraw them first.',
                                OLD.client_no, v_active_count;
                        END IF;
                    END IF;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
                CREATE OR REPLACE FUNCTION prevent_owner_delete_with_active_properties()
                RETURNS TRIGGER AS $$
                DECLARE
                    v_active_count INTEGER;
                BEGIN
                    IF OLD.role = 'Owner' THEN
                        SELECT COUNT(*) INTO v_active_count
                        FROM property
                        WHERE owner_id = OLD.client_no
                          AND status IN ('Available', 'Rented');

                        IF v_active_count > 0 THEN
                            RAISE EXCEPTION 'Cannot delete owner % — they still have % active propert(ies). Withdraw them first.',
                                OLD.client_no, v_active_count;
                        END IF;
                    END IF;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;
            """
        ),
    ]
