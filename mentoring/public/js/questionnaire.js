// TODO: Split in two files

function MessageView(element, mentoring) {
    return {
        messageDOM: $('.feedback', element),
        allPopupsDOM: $('.choice-tips, .feedback', element),
        allResultsDOM: $('.choice-result', element),
        clearPopupEvents: function() {
            this.allPopupsDOM.hide();
            $('.close', this.allPopupsDOM).off('click');
        },
        showPopup: function(popupDOM) {
            var self = this;
            this.clearPopupEvents();

            // Set the width/height
            var tip = $('.tip', popupDOM)[0];
            var data = $(tip).data();
            if (data && data.width) {
                popupDOM.css('width', data.width);
                popupDOM.find('.tip-choice-group').css('width', data.width);
            } else {
                popupDOM.css('width', '');
                popupDOM.find('.tip-choice-group').css('width', '');
            }

            if (data && data.height) {
                popupDOM.css('height', data.height);
                popupDOM.css('maxHeight', data.height);
            } else {
                popupDOM.css('height', '');
                popupDOM.css('maxHeight', '');
            }
            // .tip-choice-group should always be the same height as the popup
            // for scrolling to work properly.
            popupDOM.find('.tip-choice-group').height(popupDOM.height());

            popupDOM.show();

            mentoring.publish_event({
                event_type:'xblock.mentoring.feedback.opened',
                content: $(popupDOM).text()
            });

            $('.close', popupDOM).on('click', function() {
                self.clearPopupEvents();
                mentoring.publish_event({
                    event_type:'xblock.mentoring.feedback.closed',
                    content: $(popupDOM).text()
                });
            });
        },
        showMessage: function(message) {
            if (_.isString(message)) {
                mentoring.setContent(this.messageDOM, message);
                this.showPopup(this.messageDOM);
            }
            else {
                this.showPopup(message); // already a DOM
            }
        },
        clearResult: function() {
            this.allPopupsDOM.html('').hide();
            this.allResultsDOM.removeClass(
                'checkmark-incorrect icon-exclamation fa-exclamation checkmark-correct icon-ok fa-check'
            );
        }
    };
}

function MCQBlock(runtime, element, mentoring) {
    return {
        mode: null,
        init: function(options) {
            this.mode = options.mode;
            $('input[type=radio]', element).on('change', options.onChange);
        },

        submit: function() {
            var checkedRadio = $('input[type=radio]:checked', element);

            if(checkedRadio.length) {
                return checkedRadio.val();
            } else {
                return null;
            }
        },

        handleReview: function(result){
            $('.choice input[value="' + result.submission + '"]', element).prop('checked', true);
            $('.choice input', element).prop('disabled', true);
        },

        handleSubmit: function(result) {

            var messageView = MessageView(element, mentoring);
            messageView.clearResult();

            var choiceInputs = $('.choice input', element);
            $.each(choiceInputs, function(index, choiceInput) {
                var choiceInputDOM = $(choiceInput);
                var choiceDOM = choiceInputDOM.closest('.choice');
                var choiceResultDOM = $('.choice-result', choiceDOM);
                var choiceTipsDOM = $('.choice-tips', choiceDOM);

                if (result.status === "correct" && choiceInputDOM.val() === result.submission) {
                    choiceResultDOM.addClass('checkmark-correct icon-ok fa-check');
                }
                else if (choiceInputDOM.val() === result.submission || _.isNull(result.submission)) {
                    choiceResultDOM.addClass('checkmark-incorrect icon-exclamation fa-exclamation');
                }

                if (result.tips && choiceInputDOM.val() === result.submission) {
                    mentoring.setContent(choiceTipsDOM, result.tips);
                }

                choiceResultDOM.off('click').on('click', function() {
                    if (choiceTipsDOM.html() !== '') {
                        messageView.showMessage(choiceTipsDOM);
                    }
                });
            });

            if (_.isNull(result.submission)) {
                messageView.showMessage('<div class="message-content">You have not provided an answer.</div>' +
                                        '<div class="close icon-remove-sign fa-times-circle"></div>');
            }
            else if (result.tips) {
                messageView.showMessage(result.tips);
            }
        },

        clearResult: function() {
            MessageView(element, mentoring).clearResult();
        },

        validate: function(){
            var checked = $('input[type=radio]:checked', element);
            return Boolean(checked.length);
        }
    };
}

function MRQBlock(runtime, element, mentoring) {
    return {
        mode: null,
        init: function(options) {
            this.mode = options.mode;
            $('input[type=checkbox]', element).on('change', options.onChange);
        },

        submit: function() {
            var checkedCheckboxes = $('input[type=checkbox]:checked', element);
            var checkedValues = [];

            $.each(checkedCheckboxes, function(index, checkedCheckbox) {
                checkedValues.push($(checkedCheckbox).val());
            });
            return checkedValues;
        },

        handleReview: function(result, options) {
            $.each(result.submissions, function (index, value) {
                $('input[type="checkbox"][value="' + value + '"]').prop('checked', true)
            });
            $('input', element).prop('disabled', true);
        },

        handleSubmit: function(result, options) {

            var messageView = MessageView(element, mentoring);

            if (result.message) {
                messageView.showMessage('<div class="message-content">' + result.message + '</div>'+
                                        '<div class="close icon-remove-sign fa-times-circle"></div>');
            }
            var questionnaireDOM = $('fieldset.questionnaire', element);
            var data = questionnaireDOM.data();
            var hide_results = (data.hide_results === 'True');
            $.each(result.choices, function(index, choice) {
                var choiceInputDOM = $('.choice input[value='+choice.value+']', element);
                var choiceDOM = choiceInputDOM.closest('.choice');
                var choiceResultDOM = $('.choice-result', choiceDOM);
                var choiceTipsDOM = $('.choice-tips', choiceDOM);
                /* show hint if checked or max_attempts is disabled */
                if (!hide_results &&
                    (result.completed || choiceInputDOM.prop('checked') || options.max_attempts <= 0)) {
                    if (choice.completed) {
                        choiceResultDOM.addClass('checkmark-correct icon-ok fa-check');
                    } else if (!choice.completed) {
                        choiceResultDOM.addClass('checkmark-incorrect icon-exclamation fa-exclamation');
                    }
                    mentoring.setContent(choiceTipsDOM, choice.tips);

                    choiceResultDOM.off('click').on('click', function() {
                        messageView.showMessage(choiceTipsDOM);
                    });
                }
            });
        },

        clearResult: function() {
            MessageView(element, mentoring).clearResult();
        },

        validate: function(){
            var checked = $('input[type=checkbox]:checked', element);
            if (checked.length) {
                return true;
            }
            return false;
        }

    };
}
