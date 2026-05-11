from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0014_auto_20260508_1815'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- =========================================================
            -- FIX: Update generate_branch_no to use the correct 'branch' table
            -- =========================================================
            CREATE OR REPLACE FUNCTION generate_branch_no()
            RETURNS VARCHAR AS $$
            DECLARE
                last_branch_no VARCHAR;
                new_seq INT;
            BEGIN
                -- SELECT FROM 'branch' INSTEAD OF 'branches_branch'
                SELECT branch_no INTO last_branch_no
                FROM branch
                ORDER BY branch_no DESC
                LIMIT 1;

                IF last_branch_no IS NOT NULL AND last_branch_no ~ '^B[0-9]+$' THEN
                    new_seq := CAST(SUBSTRING(last_branch_no FROM 2) AS INT) + 1;
                ELSE
                    new_seq := 1;
                END IF;

                RETURN 'B' || LPAD(new_seq::TEXT, 2, '0');
            END;
            $$ LANGUAGE plpgsql;

            -- =========================================================
            -- FIX: Update trigger to point to the correct 'branch' table
            -- =========================================================
            DROP TRIGGER IF EXISTS tgr_assign_branch_no ON branches_branch;
            DROP TRIGGER IF EXISTS tgr_assign_branch_no ON branch;
            
            CREATE TRIGGER tgr_assign_branch_no
            BEFORE INSERT ON branch
            FOR EACH ROW
            EXECUTE FUNCTION trigger_set_branch_no();
            """,
            reverse_sql="""
            -- Reverse is not strictly necessary for a fix, but good practice
            DROP TRIGGER IF EXISTS tgr_assign_branch_no ON branch;
            """
        ),
    ]
