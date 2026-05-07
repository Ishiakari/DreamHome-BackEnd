

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leases', '0005_alter_leaseagreement_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- JL Function 1
                CREATE OR REPLACE FUNCTION fn_trigger_validate_branch()
                RETURNS TRIGGER
                LANGUAGE plpgsql
                AS $$
                DECLARE
                    v_manager_position TEXT;
                BEGIN
                    -- Required Field Validations (Using the NEW record)
                    IF NULLIF(trim(NEW.street), '') IS NULL THEN
                        RAISE EXCEPTION 'Street is required';
                    END IF;

                    IF NULLIF(trim(NEW.city), '') IS NULL THEN
                        RAISE EXCEPTION 'City is required';
                    END IF;

                    -- Local District Validation 
                    IF NEW.area IS NOT NULL AND NEW.area NOT IN ('Carmen', 'Lapasan', 'Macasandig', 'Poblacion', 'Lumbia') THEN
                        RAISE EXCEPTION 'Invalid area: %', NEW.area;
                    END IF;

                    -- Pattern Matching (Regex)
                    IF NEW.postcode IS NULL OR NEW.postcode !~ '^[A-Za-z0-9 -]{3,20}$' THEN
                        RAISE EXCEPTION 'Invalid postcode format';
                    END IF;

                    IF NEW.telephone_no IS NULL OR NEW.telephone_no !~ '^\+?[0-9()[:space:]-]{7,50}$' THEN
                        RAISE EXCEPTION 'Invalid telephone format';
                    END IF;

                    -- Manager Role & Existence Check
                    IF NEW.manager_no IS NOT NULL THEN
                        SELECT position 
                        INTO v_manager_position
                        FROM staff
                        WHERE staff_no = NEW.manager_no;

                        IF NOT FOUND THEN
                            RAISE EXCEPTION 'Manager % does not exist', NEW.manager_no;
                        ELSIF v_manager_position <> 'Manager' THEN
                            RAISE EXCEPTION 'Staff % is not a Manager', NEW.manager_no;
                        END IF;
                    END IF;

                    -- MUST return NEW so the INSERT/UPDATE can proceed successfully
                    RETURN NEW;
                END;
                $$;
                
                CREATE TRIGGER trg_validate_branch_before_insert_update
                BEFORE INSERT OR UPDATE ON branch
                FOR EACH ROW
                EXECUTE FUNCTION fn_trigger_validate_branch();
                
                -- JL Trigger:
                
                DROP TRIGGER IF EXISTS trg_validate_branch_before_insert_update ON branch;
                CREATE TRIGGER trg_validate_branch_before_insert_update
                BEFORE INSERT OR UPDATE ON branch
                FOR EACH ROW
                EXECUTE FUNCTION fn_trigger_validate_branch();
                
                
            """
        )
    ]
