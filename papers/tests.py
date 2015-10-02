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
from papers.models import *
import papers.doi

class ResearcherTest(django.test.TestCase):
    def test_creation(self):
        r = Researcher.get_or_create_by_name('Marie', 'Farge')
        r2 = Researcher.get_or_create_by_name(' Marie', ' Farge')
        self.assertEqual(r, r2)

        r3 = Researcher.get_or_create_by_orcid('0000-0002-4445-8625')
        self.assertNotEqual(r, r3)

    def test_name_conflict(self):
        # Both are called "John Doe"
        r1 = Researcher.get_or_create_by_orcid('0000-0001-7295-1671')
        r2 = Researcher.get_or_create_by_orcid('0000-0001-5393-1421')
        self.assertNotEqual(r1, r2)

import doctest
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(papers.doi))
    return tests


