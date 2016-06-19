# -*- encoding: utf-8 -*-

# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from __future__ import unicode_literals

import unittest
import django.test
import json
from django.core.urlresolvers import reverse
from backend.tests import PrefilledTest
from backend.crossref import CrossRefAPI
from backend.oai import OaiPaperSource

from django.contrib.auth.models import User
from time import sleep
from papers.models import Paper

# TODO TO BE TESTED
#urlpatterns = patterns('',
##    url(r'^annotate-paper-(?P<pk>\d+)-(?P<status>\d+)$', annotatePaper, name='ajax-annotatePaper'),
##    url(r'^delete-researcher-(?P<pk>\d+)$', deleteResearcher, name='ajax-deleteResearcher'),
##    url(r'^change-department$', changeDepartment, name='ajax-changeDepartment'),
##    url(r'^change-paper$', changePaper, name='ajax-changePaper'),
##    url(r'^change-researcher$', changeResearcher, name='ajax-changeResearcher'),
##    url(r'^change-author$', changeAuthor, name='ajax-changeAuthor'),
#    url(r'^add-researcher$', addResearcher, name='ajax-addResearcher'),
#    url(r'^new-unaffiliated-researcher$', newUnaffiliatedResearcher, name='ajax-newUnaffiliatedResearcher'),
#    url(r'^change-publisher-status$', changePublisherStatus, name='ajax-changePublisherStatus'),
##    url(r'^harvesting-status-(?P<pk>\d+)$', harvestingStatus, name='ajax-harvestingStatus'),
#    url(r'^wait-for-consolidated-field$', waitForConsolidatedField, name='ajax-waitForConsolidatedField'),
#)

class JsonRenderingTest(PrefilledTest):
    @classmethod
    def setUpClass(self):
        super(JsonRenderingTest, self).setUpClass()
        self.client = django.test.Client()

    def checkJson(self, resp, expected_status=200):
        self.assertEqual(resp.status_code, expected_status)
        parsed = json.loads(resp.content)
        return parsed

    def ajaxGet(self, *args, **kwargs):
        kwargs['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        return self.client.get(*args, **kwargs)

    def ajaxPost(self, *args, **kwargs):
        kwargs['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        return self.client.post(*args, **kwargs)

    def getPage(self, *args, **kwargs):
        urlargs = kwargs.copy()
        if 'getargs' in kwargs:
            del urlargs['getargs']
            return self.ajaxGet(reverse(*args, **urlargs), kwargs['getargs'])
        return self.ajaxGet(reverse(*args, **kwargs))

    def postPage(self, *args, **kwargs):
        urlargs = kwargs.copy()
        del urlargs['postargs']
        if 'postkwargs' in urlargs:
            del urlargs['postkwargs']
        return self.ajaxPost(reverse(*args, **urlargs), kwargs['postargs'], **kwargs.get('postkwargs',{}))


class PaperAjaxTest(JsonRenderingTest):
    @classmethod
    def setUpClass(cls):
        super(PaperAjaxTest, cls).setUpClass()
        u = User.objects.create_user('terry', 'pit@mat.io', 'yo')
        u.save()

    def test_valid_search(self):
        for args in [
            {'first':'John','last':'Doe'},
            {'first':'Gilbeto','last':'Gil'},
            ]:
            parsed = self.checkJson(self.postPage('ajax-newUnaffiliatedResearcher',
                postargs=args))
            self.assertTrue('disambiguation' in parsed or 'url' in parsed)

    def test_invalid_search(self):
        for args in [
            {'orcid':'0000-0002-8435-1137'},
            {'first':'John'},
            {'last':'Doe'},
            {},
            ]:
            parsed = self.checkJson(self.postPage('ajax-newUnaffiliatedResearcher',
                postargs=args), 403)
            self.assertTrue(len(parsed) > 0)

    def test_consolidate_paper(self):
        p = Paper.create_by_doi('10.1175/jas-d-15-0240.1')
        self.client.login(username='terry',password='yo')
        print "X1"
        page = self.getPage(
                'ajax-waitForConsolidatedField', getargs={
                    'field':'abstract',
                    'id': p.id})
        print "X2"
        result = self.checkJson(page)
        print "X3"
        self.client.logout()
        print "X4"
        self.assertTrue(result['success'])
        self.assertTrue(len(result['value']) > 10)

        
class PublisherAjaxTest(JsonRenderingTest):
    @classmethod
    def setUpClass(cls):
        super(PublisherAjaxTest, cls).setUpClass()
        u = User.objects.create_user('patrick', 'pat@mat.io', 'yo')
        u.is_superuser = True
        u.save()

    def setUp(self):
        super(PublisherAjaxTest, self).setUp()
        self.papers = map(Paper.create_by_doi,
                ['10.1038/526052a','10.1038/nchem.1829','10.1038/nchem.1365'])
        self.publisher = self.papers[0].publications[0].publisher
        self.assertEqual(self.publisher.name, 'Nature Publishing Group')

    def test_logged_out(self):
        self.client.logout()
        req = self.postPage('ajax-changePublisherStatus',
                postargs={'pk':self.publisher.pk,'status':'OA'})
        self.assertEqual(req.status_code, 302)

    def test_change_publisher_status(self):
        self.client.login(username='patrick', password='yo')
        p = self.postPage('ajax-changePublisherStatus',
                postargs={'pk':self.publisher.pk,
                          'status':'OA'})
        self.assertEqual(p.status_code, 200)
        sleep(3)
        papers = [Paper.objects.get(pk=p.pk) for p in self.papers]
        self.assertTrue(all([p.oa_status == 'OA' for p in papers]))


