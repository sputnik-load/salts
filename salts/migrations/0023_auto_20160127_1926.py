# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0022_auto_20160127_1239'),
    ]

    operations = [
        migrations.RunSQL("""INSERT INTO salts_generatortype (id, name) VALUES
                                (1, 'phantom'),
                                (2, 'jmeter'),
                                (3, 'bfg')
                          """),
        migrations.RunSQL("""INSERT INTO salts_testresult_generator_types (testresult_id, generatortype_id)
                                SELECT tr.id tr_id, gt.id gt_id FROM salts_generatortype gt, salts_testresult tr
                                JOIN salts_generatortypelist gtl
                                ON tr.generator_type_list_id = gtl.id
                                WHERE gt.name = 'phantom' and gtl.name_list = 'phantom'
                          """),

        migrations.RunSQL("""INSERT INTO salts_testresult_generator_types (testresult_id, generatortype_id)
                                SELECT tr.id tr_id, gt.id gt_id FROM salts_generatortype gt, salts_testresult tr
                                JOIN salts_generatortypelist gtl
                                ON tr.generator_type_list_id = gtl.id
                                WHERE gt.name = 'jmeter' and gtl.name_list = 'jmeter'
                          """),
    ]
