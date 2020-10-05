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

import logging

from lazy import lazy
from xblock.fragment import Fragment

from .light_children import Boolean, Float, Integer, LightChild, Scope, String
from .models import Answer
from .step import StepMixin
from .utils import loader

# Globals ###########################################################

log = logging.getLogger(__name__)


# Classes ###########################################################

class AnswerBlock(LightChild, StepMixin):
    """
    A field where the student enters an answer

    Must be included as a child of a mentoring block. Answers are persisted as django model instances
    to make them searchable and referenceable across xblocks.
    """
    show_title = Boolean(help="Display the default title (QUESTION)?", default=True, scope=Scope.content)
    read_only = Boolean(help="Display as a read-only field", default=False, scope=Scope.content)
    default_from = String(help="If specified, the name of the answer to get the default value from",
                          default=None, scope=Scope.content)
    min_characters = Integer(help="Minimum number of characters allowed for the answer",
                             default=0, scope=Scope.content)
    question = String(help="Question to ask the student", scope=Scope.content, default="")
    weight = Float(help="Defines the maximum total grade of the light child block.",
                   default=1, scope=Scope.content, enforce_type=True)

    @classmethod
    def init_block_from_node(cls, block, node, attr):
        block.light_children = []
        for child_id, xml_child in enumerate(node):
            if xml_child.tag == 'question':
                block.question = xml_child.text
            else:
                cls.add_node_as_child(block, xml_child, child_id)

        for name, value in attr:
            setattr(block, name, value)

        return block

    @lazy
    def student_input(self):  # pylint: disable=E0202
        """
        Use lazy property instead of XBlock field, as __init__() doesn't support
        overwriting field values
        """
        # Only attempt to locate a model object for this block when the answer has a name
        if not self.name:
            return ''

        student_input = self.get_model_object().student_input

        # Default value can be set from another answer's current value
        if not student_input and self.default_from:
            student_input = self.get_model_object(name=self.default_from).student_input

        return student_input

    def mentoring_view(self, context=None):
        if not self.read_only:
            html = loader.custom_render_js_template('templates/html/answer_editable.html', {
                'self': self,
            })
        else:
            html = loader.custom_render_js_template('templates/html/answer_read_only.html', {
                'self': self,
            })

        fragment = Fragment(html)
        fragment.add_css_url(self.runtime.local_resource_url(self.xblock_container, 'public/css/answer.css'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self.xblock_container,
                                                                    'public/js/answer.js'))
        fragment.initialize_js('AnswerBlock')
        return fragment

    def mentoring_table_view(self, context=None):
        html = loader.custom_render_js_template('templates/html/answer_table.html', {
            'self': self,
        })
        fragment = Fragment(html)
        fragment.add_css_url(self.runtime.local_resource_url(self.xblock_container, 'public/css/answer_table.css'))
        return fragment

    def submit(self, submission):
        if not self.read_only:
            self.student_input = submission[0]['value'].strip()
            log.info('Answer submitted for`{}`: "{}"'.format(self.name, self.student_input))
        return self.calculate_results()

    def get_results(self, previous_result):
        # Previous result is actually stored in database table-- ignore.
        return self.calculate_results()

    def calculate_results(self):
        return {
            'student_input': self.student_input,
            'status': self.status,
            'weight': self.weight,
            'score': 1 if self.status == 'correct' else 0,
        }

    @property
    def status(self):
        answer_length_ok = self.student_input
        if self.min_characters > 0:
            answer_length_ok = len(self.student_input.strip()) >= self.min_characters

        return 'correct' if (self.read_only or answer_length_ok) else 'incorrect'

    def save(self):
        """
        Replicate data changes on the related Django model used for sharing of data accross XBlocks
        """
        super().save()

        # Only attempt to locate a model object for this block when the answer has a name
        if self.name:
            answer_data = self.get_model_object()
            if answer_data.student_input != self.student_input and not self.read_only:
                answer_data.student_input = self.student_input
                answer_data.save()

    def get_model_object(self, name=None):
        """
        Fetches the Answer model object for the answer named `name`
        """
        # By default, get the model object for the current answer's name
        if not name:
            name = self.name
        # Consistency check - we should have a name by now
        if not name:
            raise ValueError('AnswerBlock.name field need to be set to a non-null/empty value')

        # TODO: Why do we need to use `xmodule_runtime` and not `runtime`?
        student_id = self.xmodule_runtime.anonymous_student_id
        course_id = self.xmodule_runtime.course_id

        answer_data, _ = Answer.objects.get_or_create(
            student_id=student_id,
            course_id=course_id,
            name=name,
        )
        return answer_data
