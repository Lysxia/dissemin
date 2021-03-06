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

import unittest
from datetime import date
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.forms import Form
from papers.models import OaiSource, Paper
from backend.tests import PrefilledTest
from deposit.models import Repository, DepositRecord
from deposit.protocol import DepositResult
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import os

# 1x1 px image used as default logo for the repository
simple_png_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xdf\n\x12\x0c+\x19\x84\x1d/"\x00\x00\x00\x19tEXtComment\x00Created with GIMPW\x81\x0e\x17\x00\x00\x00\x0cIDAT\x08\xd7c\xa8\xa9\xa9\x01\x00\x02\xec\x01u\x90\x90\x1eL\x00\x00\x00\x00IEND\xaeB`\x82'

# for sample abstracts
lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

class ProtocolTest(PrefilledTest):
    """
    Set of generic tests that any protocol should pass.
    """
    def __init__(self, *args, **kwargs):
        super(ProtocolTest, self).__init__(*args, **kwargs)

    @classmethod
    @override_settings(MEDIA_ROOT='mediatest/')
    def setUpClass(self):
        super(ProtocolTest, self).setUpClass()
        if self is ProtocolTest:
             raise unittest.SkipTest("Base test")
        if 'TRAVIS' in os.environ:
            raise unittest.SkipTest("Skipping deposit test on Travis to avoid mass submissions to sandboxes")
        self.p1 = Paper.get_or_create(
                "This is a test paper",
                [self.r1.name, self.r2.name, self.r4.name],
                date(year=2014,month=02,day=15))
        self.user, _ = User.objects.get_or_create(username='myuser')
        self.oaisource, _ = OaiSource.objects.get_or_create(
            identifier='deposit_oaisource',
            name='Repository OAI source',
            default_pubtype='preprint')
        logo = InMemoryUploadedFile(
                BytesIO(simple_png_image),
                None, 'logo.png',
                'image/png', len(simple_png_image), None, None)
        self.repo = Repository.objects.create(
                name='Repository Sandbox',
                description='babebibobu',
                logo=logo,
                protocol=self.__name__,
                oaisource=self.oaisource)
        self.proto = None
        self.form = None
       
    def test_protocol_identifier(self):
        self.assertTrue(len(self.proto.protocol_identifier()) > 1)

    def test_init_deposit(self):
        retval = self.proto.init_deposit(self.p1, self.user)
        self.assertIs(type(retval), bool)

    def test_get_form_return_type(self):
        self.proto.init_deposit(self.p1, self.user)
        retval = self.proto.get_form()
        self.assertIsInstance(retval, Form)

    @unittest.expectedFailure
    def test_submit_deposit_wrapper(self):
        pdf = 'mediatest/blank.pdf'
        deposit_result = self.proto.submit_deposit_wrapper(pdf, self.form)
        self.assertIsInstance(deposit_result, DepositResult)
        self.assertTrue(deposit_result.success())



