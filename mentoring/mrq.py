# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 edX
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

import logging


from .light_children import Integer, List, Scope
from .questionnaire import QuestionnaireAbstractBlock
from .utils import render_template


# Globals ###########################################################

log = logging.getLogger(__name__)


# Classes ###########################################################

class MRQBlock(QuestionnaireAbstractBlock):
    """
    An XBlock used to ask multiple-response questions
    """
    student_choices = List(help="Last submissions by the student", default=[], scope=Scope.user_state)
    max_attempts = Integer(help="Number of max attempts for this questions", default=None, scope=Scope.content)
    num_attempts = Integer(help="Number of attempts a user has answered for this questions", scope=Scope.user_state)

    # TODO REMOVE THIS, ONLY NEEDED FOR LIGHTCHILDREN
    @classmethod
    def get_fields_to_save(cls):
        return [
            'num_attempts'
        ]

    # TODO REMOVE ALL USE OF THE get() METHOD
    def submit(self, submissions):
        log.debug(u'Received MRQ submissions: "%s"', submissions)

        # Ensure our data are loaded from the db
        # TODO HACK, TO REMOVE.
        self.load_student_data()

        completed = True

        results = []
        for choice in self.custom_choices:
            choice_completed = True
            choice_tips_fragments = []
            choice_selected = choice.value.get() in submissions
            for tip in self.get_tips():
                if choice.value.get() in tip.display_with_defaults:
                    choice_tips_fragments.append(tip.render())

                if ((not choice_selected and choice.value.get() in tip.require_with_defaults) or
                        (choice_selected and choice.value.get() in tip.reject_with_defaults)):
                    choice_completed = False

            completed = completed and choice_completed
            results.append({
                'value': choice.value.get(),
                'selected': choice_selected,
                'completed': choice_completed,
                'tips': render_template('templates/html/tip_choice_group.html', {
                    'self': self,
                    'tips_fragments': choice_tips_fragments,
                    'completed': choice_completed,
                }),
            })

        self.message = u'Your answer is correct!' if completed else u'Your answer is incorrect.'

        num_attempts = self.num_attempts.get() + 1 if self.max_attempts else 0
        setattr(self, 'num_attempts', num_attempts)

        max_attempts_reached = False
        if self.max_attempts:
            max_attempts = self.max_attempts.get()
            num_attempts = self.num_attempts.get()
            max_attempts_reached = num_attempts >= max_attempts

        if max_attempts_reached and (not completed or num_attempts > max_attempts):
            completed = True
            self.message = self.message.get() + u' You have reached the maximum number of attempts for this question. ' \
            u'Your next answers won''t be saved. You can check the answer(s) using the "Show Answer(s)" button.'
        else:
            self.student_choices = submissions

        result = {
        'submissions': submissions,
        'completed': completed,
        'choices': results,
        'message': self.message.get(),
        'max_attempts': self.max_attempts.get() if self.max_attempts else None,
        'num_attempts': self.num_attempts.get()
        }

        log.debug(u'MRQ submissions result: %s', result)
        return result
