##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2024, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import uuid
import os
import json
from pgadmin.utils.route import BaseTestGenerator
from regression.python_test_utils import test_utils as utils
from ...tests import utils as job_scheduler_utils
from pgadmin.browser.server_groups.servers.databases.tests import \
    utils as database_utils


# Load test data from json file.
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
with open(CURRENT_PATH + "/dbms_jobs_test_data.json") as data_file:
    test_cases = json.load(data_file)


class DBMSEnableJobTestCase(BaseTestGenerator):
    """This class will test the enable job in the DBMS job API"""
    scenarios = utils.generate_scenarios("dbms_enable_job",
                                         test_cases)

    def setUp(self):
        super().setUp()
        # Load test data
        self.data = self.test_data

        if not job_scheduler_utils.is_supported_version(self):
            self.skipTest(job_scheduler_utils.SKIP_MSG)

        # Create db
        self.db_name, self.db_id = job_scheduler_utils.create_test_database(
            self)
        db_con = database_utils.connect_database(self,
                                                 utils.SERVER_GROUP,
                                                 self.server_id,
                                                 self.db_id)
        if db_con["info"] != "Database connected.":
            raise Exception("Could not connect to database.")

        # Create extension required for job scheduler
        job_scheduler_utils.create_job_scheduler_extensions(self)

        if not job_scheduler_utils.is_dbms_job_scheduler_present(self):
            self.skipTest(job_scheduler_utils.SKIP_MSG_EXTENSION)

        self.job_name = "test_job_enable%s" % str(uuid.uuid4())[1:8]
        self.data['job_name'] = self.job_name
        self.job_id = job_scheduler_utils.create_dbms_job(
            self, self.job_name, False)

    def runTest(self):
        """ This function will test DBMS job under test database."""
        response = job_scheduler_utils.api_put(self, self.job_id)

        # Assert response
        utils.assert_status_code(self, response)

    def tearDown(self):
        """This function will do the cleanup task."""
        job_scheduler_utils.delete_dbms_job(self, self.job_name)

        job_scheduler_utils.clean_up(self)
