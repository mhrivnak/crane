import httplib
import json

import mock
import unittest2
from crane import exceptions

from crane.search import Solr
from crane.search.base import SearchResult


class BaseSolrTest(unittest2.TestCase):
    def setUp(self):
        super(BaseSolrTest, self).setUp()
        self.url = 'http://pulpproject.org/search?q={}'
        self.solr = Solr(self.url)


class TestInit(BaseSolrTest):
    def test_stores_data(self):
        self.assertEqual(self.solr.url_template, self.url)


class TestSearch(BaseSolrTest):
    @mock.patch('crane.search.solr.Solr._get_data')
    def test_quotes_query(self, mock_parse):
        self.solr.search('hi mom')

        mock_parse.assert_called_once_with(self.url.format('hi%20mom'))

    @mock.patch('crane.search.solr.Solr._filter_result', spec_set=True, return_value=True)
    @mock.patch('crane.search.solr.Solr._get_data', spec_set=True)
    @mock.patch('crane.search.solr.Solr._parse')
    def test_workflow_filter_true(self, mock_parse, mock_get_data, mock_filter):
        mock_parse.return_value = [SearchResult('rhel', 'Red Hat Enterprise Linux')]

        ret = self.solr.search('foo')

        mock_get_data.assert_called_once_with('http://pulpproject.org/search?q=foo')
        self.assertDictEqual(list(ret)[0], {
            'name': 'rhel',
            'description': 'Red Hat Enterprise Linux',
            'star_count': 5,
            'is_trusted': True,
            'is_official': True,
        })

    @mock.patch('crane.search.solr.Solr._filter_result', spec_set=True, return_value=False)
    @mock.patch('crane.search.solr.Solr._get_data', spec_set=True)
    @mock.patch('crane.search.solr.Solr._parse')
    def test_workflow_filter_true(self, mock_parse, mock_get_data, mock_filter):
        mock_parse.return_value = [SearchResult('rhel', 'Red Hat Enterprise Linux')]

        ret = self.solr.search('foo')

        mock_get_data.assert_called_once_with('http://pulpproject.org/search?q=foo')
        self.assertEqual(len(list(ret)), 0)


class TestParse(BaseSolrTest):
    def test_normal(self):
        result = list(self.solr._parse(json.dumps(fake_body)))

        self.assertEqual(len(result), 1)

        self.assertTrue(isinstance(result[0], SearchResult))
        self.assertEqual(result[0].name, 'foo/bar')
        self.assertEqual(result[0].description, 'marketing speak yada yada')

    def test_json_exception(self):
        """
        when an exception occurs, it should raise an HTTPError
        """
        with self.assertRaises(exceptions.HTTPError) as assertion:
            list(self.solr._parse('this is not valid json'))

        self.assertEqual(assertion.exception.status_code, httplib.BAD_GATEWAY)

    def test_attribute_exception(self):
        """
        when an exception occurs, it should raise an HTTPError
        """
        with self.assertRaises(exceptions.HTTPError) as assertion:
            list(self.solr._parse(json.dumps({})))

        self.assertEqual(assertion.exception.status_code, httplib.BAD_GATEWAY)


fake_body = {
    'response': {
        'docs': [
            {
                'allTitle': 'foo/bar',
                'ir_description': 'marketing speak yada yada',
            }
        ]
    }
}
