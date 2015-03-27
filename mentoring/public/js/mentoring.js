function MentoringBlock(runtime, element) {
    var attemptsTemplate = _.template($('#xblock-attempts-template').html());
    var data = $('.mentoring', element).data();
    var children_dom = []; // Keep track of children. A Child need a single object scope for its data.
    var children = [];
    var step = data.step;

    function publish_event(data) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'publish_event'),
            data: JSON.stringify(data)
        });
    }

    $(document).on("click", function(event, ui) {
        var target = $(event.target);
        var question_feedback_selector = ".mentoring .feedback";
        var item_feedback_parent_selector = '.choice';
        var item_feedback_selector = ".choice .choice-tips";

        function clickedInside(selector, parent_selector){
            return target.is(selector) || target.parents(parent_selector).length>0;
        }

        if (!clickedInside(question_feedback_selector, question_feedback_selector)) {
            $(question_feedback_selector).not(':hidden').each(function (i, el) {
                $(el).hide();
                publish_event({event_type: 'xblock.mentoring.feedback.closed', content: $(el).text()});
            });
        }

        if (!clickedInside(item_feedback_selector, item_feedback_parent_selector)) {
            $(item_feedback_selector).not(':hidden').hide();
        }
    });

    function callIfExists(obj, fn) {
        if (typeof obj !== 'undefined' && typeof obj[fn] == 'function') {
            return obj[fn].apply(obj, Array.prototype.slice.call(arguments, 2));
        } else {
            return null;
        }
    }

    function setContent(dom, content) {
        dom.html('');
        dom.append(content);
        var template = $('#light-child-template', dom).html();
        if (template) {
            dom.append(template);
        }
    }

    function renderAttempts() {
        var data = $('.attempts', element).data();
        $('.attempts', element).html(attemptsTemplate(data));
    }

    function renderDependency() {
        var warning_dom = $('.missing-dependency', element);
        var data = warning_dom.data();

        if (data.missing === 'True') {
            warning_dom.show();
        }
    }

    function readChildren() {
        var doms = $('.xblock-light-child', element);

        $.each(doms, function(index, child_dom) {
            var child_type = $(child_dom).attr('data-type');
            var child = window[child_type];
            children_dom.push(child_dom);
            children.push(child);
            if (typeof child !== 'undefined') {
                child = child(runtime, child_dom, mentoring);
                child.name = $(child_dom).attr('name');
                children[children.length-1] = child;
            }
        });
    }

    /* Init and display a child. */
    function displayChild(index, options) {
        options = options || {};
        options.mode = data.mode;
        if (index >= children.length)
            return  children.length;

        var template = $('#light-child-template', children_dom[index]).html();
        $(children_dom[index]).append(template);
        $(children_dom[index]).show();
        var child = children[index];
        callIfExists(child, 'init', options);
        return child;
    }

    function displayChildren(options) {
        $.each(children_dom, function(index) {
            displayChild(index, options);
        });
    }

    function getChildByName(element, name) {
        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            if (child && child.name === name) {
                return child;
            }
        }
    }

    var mentoring = {
        callIfExists: callIfExists,
        setContent: setContent,
        renderAttempts: renderAttempts,
        renderDependency: renderDependency,
        readChildren: readChildren,
        children_dom: children_dom,
        children: children,
        displayChild: displayChild,
        displayChildren: displayChildren,
        getChildByName: getChildByName,
        step: step,
        publish_event: publish_event
    };

    if (data.mode === 'standard') {
        MentoringStandardView(runtime, element, mentoring);
    }
    else if (data.mode === 'assessment') {
        MentoringAssessmentView(runtime, element, mentoring);
    }

    publish_event({event_type:"xblock.mentoring.loaded"});
}
