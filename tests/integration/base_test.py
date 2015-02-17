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

from xblockutils.base_test import SeleniumBaseTest
from selenium.webdriver.support.ui import WebDriverWait


class MentoringBaseTest(SeleniumBaseTest):
    module_name = __name__
    default_css_selector = 'div.mentoring'

    def wait_until_visible(self, elem):
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: e.is_displayed(), u"{} should be hidden".format(elem.text))
