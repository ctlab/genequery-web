from unittest import TestSuite
from django.core.management import call_command
from django.test import TestCase
from django.test.runner import DiscoverRunner
from django.conf import settings


def get_test_rest_response(species):
    return open('genequery/searcher/test/resource/test_rest_response_{}.txt'.format(species)).read()


class GQTestCase(TestCase):
    def assert_200(self, response):
        self.assertEqual(response.status_code, 200)

    def assertAllIn(self, *args):
        if len(args) < 2:
            return
        container = args[-1]
        members = args[:-1]
        if not isinstance(members, (list, tuple)):
            members = [members]
        for m in members:
            self.assertIn(m, container)

    def send_ajax(self, url, data={}, ok=True):
        response = self.client.get(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        if ok:
            self.assert_200(response)
        return response


class SharedFixtureTestCase(GQTestCase):
    def _fixture_setup(self):
        pass

    def _fixture_teardown(self):
        pass


class GQTestSuit(TestSuite):
    def _assert_same_class(self):
        if not self._tests:
            return
        t = type(self._tests[0])
        for test in self._tests:
            if type(test) != t:
                raise AssertionError(
                    "Tests in GQTestSuite must have the same types, but found: {} != {}".format(type(test), t))

    def _load_data(self):
        self._assert_same_class()
        if not self._tests or not self._tests[0].fixtures:
            return
        for db_name in self._tests[0]._databases_names(include_mirrors=False):
            call_command('loaddata', *self._tests[0].fixtures,
                         **{'verbosity': 0, 'database': db_name, 'skip_checks': True})

    def _flush_data(self):
        if self._tests and self._tests[0].fixtures:
            for db_name in self._tests[0]._databases_names(include_mirrors=False):
                call_command('flush', verbosity=0, interactive=False,
                             database=db_name, skip_checks=True,
                             reset_sequences=False,
                             allow_cascade=self._tests[0].available_apps is not None,
                             inhibit_post_migrate=self._tests[0].available_apps is not None)

    def run(self, result, debug=False):
        if recreate_db():
            self._load_data()
        super(GQTestSuit, self).run(result, debug)
        if recreate_db():
            self._flush_data()


def split_suite(suite):
    tests = {'base': TestSuite()}
    for test in suite._tests:
        if isinstance(test, SharedFixtureTestCase):
            cls = test.__class__
            if cls not in tests:
                tests[cls] = GQTestSuit()
            tests[cls].addTest(test)
        else:
            tests['base'].addTest(test)
    return TestSuite(tests.values())


class GQTestRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        suite = super(GQTestRunner, self).build_suite(test_labels, extra_tests, **kwargs)
        return split_suite(suite)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        import logging
        logging.disable(logging.CRITICAL)
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        old_config = None
        if recreate_db():
            old_config = self.setup_databases()
        else:
            # TODO do it better
            from django.db import connections, DEFAULT_DB_ALIAS
            connection = connections[DEFAULT_DB_ALIAS]
            connection.settings_dict['NAME'] = connection.creation._get_test_db_name()
        result = self.run_suite(suite)
        if old_config:
            self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(suite, result)


def recreate_db():
    return not getattr(settings, 'NOT_RECREATE_TEST_DB', False)