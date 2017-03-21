from __future__ import unicode_literals

import json

import django
from django.test import TestCase, TransactionTestCase
from rest_framework import status

import job.test.utils as job_test_utils
import product.test.utils as product_test_utils
import source.test.utils as source_test_utils
import storage.test.utils as storage_test_utils
import util.rest as rest_util


class TestProductsView(TransactionTestCase):

    def setUp(self):
        django.setup()

        self.country = storage_test_utils.create_country()
        self.job_type1 = job_test_utils.create_job_type(name='test1', category='test-1', is_operational=True)
        self.job1 = job_test_utils.create_job(job_type=self.job_type1)
        self.job_exe1 = job_test_utils.create_job_exe(job=self.job1)
        self.product1 = product_test_utils.create_product(job_exe=self.job_exe1, has_been_published=True,
                                                          is_published=True, file_name='test.txt',
                                                          countries=[self.country])

        self.job_type2 = job_test_utils.create_job_type(name='test2', category='test-2', is_operational=False)
        self.job2 = job_test_utils.create_job(job_type=self.job_type2)
        self.job_exe2 = job_test_utils.create_job_exe(job=self.job2)
        self.product2a = product_test_utils.create_product(job_exe=self.job_exe2, has_been_published=True,
                                                           is_published=False, countries=[self.country])

        self.product2b = product_test_utils.create_product(job_exe=self.job_exe2, has_been_published=True,
                                                           is_published=True, is_superseded=True,
                                                           countries=[self.country])

        self.product2c = product_test_utils.create_product(job_exe=self.job_exe2, has_been_published=True,
                                                           is_published=True, countries=[self.country])

    def test_invalid_started(self):
        """Tests calling the product files view when the started parameter is invalid."""

        url = rest_util.get_url('/products/?started=hello')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_missing_tz_started(self):
        """Tests calling the product files view when the started parameter is missing timezone."""

        url = rest_util.get_url('/products/?started=1970-01-01T00:00:00')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_invalid_ended(self):
        """Tests calling the product files view when the ended parameter is invalid."""

        url = rest_util.get_url('/products/?started=1970-01-01T00:00:00Z&ended=hello')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_missing_tz_ended(self):
        """Tests calling the product files view when the ended parameter is missing timezone."""

        url = rest_util.get_url('/products/?started=1970-01-01T00:00:00Z&ended=1970-01-02T00:00:00')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_negative_time_range(self):
        """Tests calling the product files view with a negative time range."""

        url = rest_util.get_url('/products/?started=1970-01-02T00:00:00Z&ended=1970-01-01T00:00:00')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_job_type_id(self):
        """Tests successfully calling the product files view filtered by job type identifier."""

        url = rest_util.get_url('/products/?job_type_id=%s' % self.job_type1.id)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['id'], self.job_type1.id)

    def test_job_type_name(self):
        """Tests successfully calling the product files view filtered by job type name."""

        url = rest_util.get_url('/products/?job_type_name=%s' % self.job_type1.name)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['name'], self.job_type1.name)

    def test_job_type_category(self):
        """Tests successfully calling the product files view filtered by job type category."""

        url = rest_util.get_url('/products/?job_type_category=%s' % self.job_type1.category)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['category'], self.job_type1.category)

    def test_is_operational(self):
        """Tests successfully calling the product files view filtered by is_operational flag."""

        url = rest_util.get_url('/products/?is_operational=true')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['is_operational'], self.job_type1.is_operational)

    def test_is_published(self):
        """Tests successfully calling the product files view filtered by is_published flag."""

        url = rest_util.get_url('/products/?is_published=false')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['id'], self.product2a.id)
        self.assertFalse(result['results'][0]['is_published'])

    def test_file_name(self):
        """Tests successfully calling the product files view filtered by file name."""

        url = rest_util.get_url('/products/?file_name=test.txt')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['file_name'], self.product1.file_name)

    def test_successful(self):
        """Tests successfully calling the product files view."""

        url = rest_util.get_url('/products/')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 2)

        for entry in result['results']:

            # Make sure unpublished and superseded products are not included
            self.assertNotEqual(entry['id'], self.product2a.id)
            self.assertNotEqual(entry['id'], self.product2b.id)

            # Make sure country info is included
            self.assertEqual(entry['countries'][0], self.country.iso3)


class TestProductDetailsView(TestCase):

    def setUp(self):
        django.setup()

        self.source = source_test_utils.create_source()
        self.ancestor = product_test_utils.create_product(file_name='test_ancestor.txt')
        self.descendant = product_test_utils.create_product(file_name='test_descendant.txt')
        self.product = product_test_utils.create_product(file_name='test_product.txt')

        product_test_utils.create_file_link(ancestor=self.source, descendant=self.ancestor)
        product_test_utils.create_file_link(ancestor=self.source, descendant=self.product)
        product_test_utils.create_file_link(ancestor=self.source, descendant=self.descendant)
        product_test_utils.create_file_link(ancestor=self.ancestor, descendant=self.product)
        product_test_utils.create_file_link(ancestor=self.ancestor, descendant=self.descendant)
        product_test_utils.create_file_link(ancestor=self.product, descendant=self.descendant)

    def test_id(self):
        """Tests successfully calling the product files view by id."""

        url = rest_util.get_url('/products/%i/' % self.product.id)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(result['id'], self.product.id)
        self.assertEqual(result['file_name'], self.product.file_name)
        self.assertEqual(result['job_type']['id'], self.product.job_type_id)

        self.assertEqual(len(result['sources']), 1)
        self.assertEqual(result['sources'][0]['id'], self.source.id)

        self.assertEqual(len(result['ancestors']), 1)
        self.assertEqual(result['ancestors'][0]['id'], self.ancestor.id)

        self.assertEqual(len(result['descendants']), 1)
        self.assertEqual(result['descendants'][0]['id'], self.descendant.id)

    def test_file_name(self):
        """Tests successfully calling the product files view by file name."""

        url = rest_util.get_url('/products/%s/' % self.product.file_name)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(result['id'], self.product.id)
        self.assertEqual(result['file_name'], self.product.file_name)
        self.assertEqual(result['job_type']['id'], self.product.job_type_id)

        self.assertEqual(len(result['sources']), 1)
        self.assertEqual(result['sources'][0]['id'], self.source.id)

        self.assertEqual(len(result['ancestors']), 1)
        self.assertEqual(result['ancestors'][0]['id'], self.ancestor.id)

        self.assertEqual(len(result['descendants']), 1)
        self.assertEqual(result['descendants'][0]['id'], self.descendant.id)

    def test_missing(self):
        """Tests calling the source files view with an invalid id or file name."""

        url = rest_util.get_url('/products/12345/')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.content)

        url = rest_util.get_url('/products/missing_file.txt/')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.content)


class TestProductsUpdatesView(TransactionTestCase):

    def setUp(self):
        django.setup()

        self.country = storage_test_utils.create_country()
        self.job_type1 = job_test_utils.create_job_type(name='test1', category='test-1', is_operational=True)
        self.job1 = job_test_utils.create_job(job_type=self.job_type1)
        self.job_exe1 = job_test_utils.create_job_exe(job=self.job1)
        self.product1 = product_test_utils.create_product(job_exe=self.job_exe1, has_been_published=True,
                                                          is_published=True, file_name='test.txt',
                                                          countries=[self.country])

        self.job_type2 = job_test_utils.create_job_type(name='test2', category='test-2', is_operational=False)
        self.job2 = job_test_utils.create_job(job_type=self.job_type2)
        self.job_exe2 = job_test_utils.create_job_exe(job=self.job2)
        self.product2a = product_test_utils.create_product(job_exe=self.job_exe2, has_been_published=True,
                                                           is_published=False, countries=[self.country])
        self.product2b = product_test_utils.create_product(job_exe=self.job_exe2, has_been_published=True,
                                                           is_published=True, is_superseded=True,
                                                           countries=[self.country])
        self.product2c = product_test_utils.create_product(job_exe=self.job_exe2, has_been_published=True,
                                                           is_published=True, countries=[self.country])

    def test_invalid_started(self):
        """Tests calling the product file updates view when the started parameter is invalid."""

        url = rest_util.get_url('/products/updates/?started=hello')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_missing_tz_started(self):
        """Tests calling the product file updates view when the started parameter is missing timezone."""

        url = rest_util.get_url('/products/updates/?started=1970-01-01T00:00:00')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_invalid_ended(self):
        """Tests calling the product file updates view when the ended parameter is invalid."""

        url = rest_util.get_url('/products/updates/?started=1970-01-01T00:00:00Z&ended=hello')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_missing_tz_ended(self):
        """Tests calling the product file updates view when the ended parameter is missing timezone."""

        url = rest_util.get_url('/products/updates/?started=1970-01-01T00:00:00Z&ended=1970-01-02T00:00:00')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_negative_time_range(self):
        """Tests calling the product file updates view with a negative time range."""

        url = rest_util.get_url('/products/updates/?started=1970-01-02T00:00:00Z&ended=1970-01-01T00:00:00')
        response = self.client.generic('GET', url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_job_type_id(self):
        """Tests successfully calling the product file updates view filtered by job type identifier."""

        url = rest_util.get_url('/products/updates/?job_type_id=%s' % self.job_type1.id)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['id'], self.job_type1.id)

    def test_job_type_name(self):
        """Tests successfully calling the product file updates view filtered by job type name."""

        url = rest_util.get_url('/products/updates/?job_type_name=%s' % self.job_type1.name)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['name'], self.job_type1.name)

    def test_job_type_category(self):
        """Tests successfully calling the product file updates view filtered by job type category."""

        url = rest_util.get_url('/products/updates/?job_type_category=%s' % self.job_type1.category)
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['category'], self.job_type1.category)

    def test_is_operational(self):
        """Tests successfully calling the product file updates view filtered by is_operational flag."""

        url = rest_util.get_url('/products/updates/?is_operational=true')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['job_type']['is_operational'], self.job_type1.is_operational)

    def test_file_name(self):
        """Tests successfully calling the product file updates view filtered by file name."""

        url = rest_util.get_url('/products/updates/?file_name=test.txt')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['file_name'], self.product1.file_name)

    def test_successful(self):
        """Tests successfully calling the product file updates view."""

        url = rest_util.get_url('/products/updates/')
        response = self.client.generic('GET', url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        result = json.loads(response.content)
        self.assertEqual(len(result['results']), 3)

        for entry in result['results']:

            # Make sure superseded products are not included
            self.assertNotEqual(entry['id'], self.product2b.id)

            # Make sure additional attributes are present
            self.assertIsNotNone(entry['update'])
            self.assertIsNotNone(entry['source_files'])
            self.assertEqual(entry['countries'][0], self.country.iso3)
