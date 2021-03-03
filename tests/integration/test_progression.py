# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Harvard
#
# Authors:
#          Xavier Antoviaque <xavier@antoviaque.org>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

# Imports ###########################################################

import urllib
from .base_test import MentoringBaseTest


# Classes ###########################################################

class MentoringProgressionTest(MentoringBaseTest):

    def get_base_url(self, url):
        """
        Extract base url from the given url

        :param url: to extract base url from
        :return: string - base url
        """

        parsed_url = urllib.parse.urlparse(url)
        return '{url.scheme}://{url.netloc}'.format(url=parsed_url)

    def assert_warning(self, warning_dom, link_href):
        """
        Check that the provided DOM element is a progression warning, and includes a link with a href
        pointing to `link_href`
        """
        self.assertEqual(warning_dom.text, 'You need to complete the previous step before attempting this step.')
        warning_link = warning_dom.find_element_by_xpath('./*')
        base_url = self.get_base_url(self.browser.current_url)
        link_href = '{}{}'.format(base_url, link_href)
        self.assertEqual(warning_link.get_attribute('href'), link_href)

    def assert_warning_is_hidden(self, mentoring):
        for elem in mentoring.find_elements_by_css_selector('.warning'):
            self.assertFalse(elem.is_displayed())

    def test_progression(self):  # pylint: disable=too-many-statements
        """
        Mentoring blocks after the current step in the workflow should redirect user to current step
        """
        # Initial - Step 1 ok, steps 2&3 redirect to step 1
        mentoring = self.go_to_page('Progression 1')
        self.assert_warning_is_hidden(mentoring)
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        self.assertFalse(submit.is_enabled())

        mentoring = self.go_to_page('Progression 2')
        warning = mentoring.find_element_by_css_selector('.warning')
        self.assert_warning(warning, '/jump_to_id/mentoring_first')
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        self.assertFalse(submit.is_enabled())

        mentoring = self.go_to_page('Progression 3')
        warning = mentoring.find_element_by_css_selector('.warning')
        self.assert_warning(warning, '/jump_to_id/mentoring_first')
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        self.assertFalse(submit.is_enabled())

        # Should be impossible to complete step 2
        mentoring = self.go_to_page('Progression 2')
        answer = mentoring.find_element_by_css_selector('textarea')
        answer.send_keys('This is the answer')
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        submit.click()
        self.wait_until_disabled(submit)

        messages = mentoring.find_element_by_css_selector('.messages')
        self.assertTrue(messages.is_displayed())
        self.assertIn(
            'You need to complete all previous steps before being able to complete the current one.',
            messages.text)

        mentoring = self.go_to_page('Progression 2')
        warning = mentoring.find_element_by_css_selector('.warning')
        self.assert_warning(warning, '/jump_to_id/mentoring_first')

        mentoring = self.go_to_page('Progression 3')
        warning = mentoring.find_element_by_css_selector('.warning')
        self.assert_warning(warning, '/jump_to_id/mentoring_first')

        # Complete step 1 - now only step 3 should redirect, and to step 2
        mentoring = self.go_to_page('Progression 1')
        answer = mentoring.find_element_by_css_selector('textarea')
        answer.send_keys('This is the answer')
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        submit.click()
        self.wait_until_disabled(submit)
        self.assert_warning_is_hidden(mentoring)

        messages = mentoring.find_element_by_css_selector('.messages')
        self.assertFalse(messages.is_displayed())

        mentoring = self.go_to_page('Progression 3')
        warning = mentoring.find_element_by_css_selector('.warning')
        self.assert_warning(warning, '/jump_to_id/progression_2')

        mentoring = self.go_to_page('Progression 2')
        self.assert_warning_is_hidden(mentoring)

        # Complete step 2 - no more warnings anywhere
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        submit.click()  # Already filled the textarea in previous step
        self.wait_until_disabled(submit)

        messages = mentoring.find_element_by_css_selector('.messages')
        self.assertFalse(messages.is_displayed())

        mentoring = self.go_to_page('Progression 1')
        self.assert_warning_is_hidden(mentoring)

        mentoring = self.go_to_page('Progression 2')
        self.assert_warning_is_hidden(mentoring)

        mentoring = self.go_to_page('Progression 3')
        self.assert_warning_is_hidden(mentoring)

        # Should be able to complete step 3 too now
        answer = mentoring.find_element_by_css_selector('textarea')
        answer.send_keys('This is the answer')
        submit = mentoring.find_element_by_css_selector('.submit input.input-main')
        submit.click()
        self.wait_until_disabled(submit)

        messages = mentoring.find_element_by_css_selector('.messages')
        self.assertFalse(messages.is_displayed())
