from django.core.urlresolvers import reverse
from django.test import Client
from utils.test import GQTestCase

MENU_ACTIVE = 'menu_active'


class BasePageTest(object):
    client = Client()
    menu_link = None
    url_name = None
    page_text = None

    def test_status_code(self):
        response = self.client.get(reverse(self.url_name))
        self.assert_200(response)

    def test_page_text(self):
        response = self.client.get(reverse(self.url_name))
        texts = [self.page_text] if isinstance(self.page_text, basestring) else self.page_text
        for text in texts:
            self.assertContains(response, text, msg_prefix='In {}'.format(self.url_name))

    def test_menu_active(self):
        response = self.client.get(reverse(self.url_name))
        self.assertTrue(MENU_ACTIVE in response.context, 'context response has not {} key'.format(MENU_ACTIVE))
        self.assertTrue(response.context[MENU_ACTIVE] == self.menu_link, '{} != {}'.format(
            response.context[MENU_ACTIVE], self.menu_link))


class AboutPageTestCase(GQTestCase, BasePageTest):
    menu_link = 'about'
    url_name = 'about'
    page_text = 'To start using GeneQuery, all you need is'


class ContactsPageTestCase(GQTestCase, BasePageTest):
    menu_link = 'contacts'
    url_name = 'contacts'
    page_text = ['Alex Predeus', 'Ivan Arbuzov', 'Maxim Artyomov Lab']


class ExamplePageTestCase(GQTestCase, BasePageTest):
    menu_link = 'example'
    url_name = 'example'
    page_text = ['Following is a list of 50 genes',
                 '<a href="/searcher/?example=true" role="button" target="_blank">Run it on search page</a>']


class SearcherPageTestCase(GQTestCase, BasePageTest):
    menu_link = 'searcher'
    url_name = 'searcher:index'
    page_text = ['Homo sapiens', 'Mus musculus', 'Run example', 'Gene list']