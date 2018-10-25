from functools import lru_cache

import sublime
import sublime_plugin
from SublimeLinter.lint import persist, events

from . import settings
from .utils import get_visible_error_ids


Settings = settings.Settings('SublimeLinter-addon-alt-ui')
STYLESHEET = '''
    <style>
        .container {
            background-color: var(--background);
            color: var(--foreground);
            color: color(var(--foreground) blend(white 50%));

            font-size: .9em;
            padding: 2px 1px 0 3px;
            margin: 0px -4px -2px;
        }
    </style>
'''

State = {}


def plugin_loaded():
    State.update(
        {
            'active_view': sublime.active_window().active_view(),
            'current_pos': (None, None),
            'prev_pos': (None, None),
            'errors': [],
        }
    )

    events.subscribe(events.LINT_RESULT, on_lint_result)


def plugin_unloaded():
    events.unsubscribe(events.LINT_RESULT, on_lint_result)


def on_lint_result(buffer_id, **kwargs):
    active_view = State['active_view']
    if active_view.buffer_id() != buffer_id:
        return

    State.update({'errors': get_errors(active_view)})
    sublime.set_timeout_async(lambda: draw(**State), 1)


class ShowTooltipsSublimeLinterCommand(sublime_plugin.EventListener):
    def on_activated_async(self, active_view):
        current_pos = get_current_pos(active_view)

        State.update(
            {
                'active_view': active_view,
                'current_pos': current_pos,
                'prev_pos': (None, None),
                'errors': get_errors(active_view),
            }
        )

    def on_selection_modified_async(self, view):
        active_view = State['active_view']
        # It is possible that views (e.g. panels) update in the background.
        # So we check here and return early.
        if active_view.buffer_id() != view.buffer_id():
            return

        prev_pos = State['current_pos']
        current_pos = get_current_pos(active_view)
        if current_pos == prev_pos:
            return

        State.update({'current_pos': current_pos, 'prev_pos': prev_pos})

        # print('on_selection_modified_async')
        # sublime.set_timeout_async(lambda: draw(**State), 1)
        draw(**State)


_last_errors_under_cursor = []
_last_messages = ''


def draw(active_view, current_pos, prev_pos, errors, **kwargs):
    if not Settings.get('tooltips', False):
        return

    if current_pos == (None, None):
        return

    global _last_errors_under_cursor, _last_messages

    row, col = current_pos
    prev_row, _ = prev_pos

    visible_error_ids = get_visible_error_ids(active_view)

    errors_on_line = [
        error
        for error in errors
        if error['line'] == row and error['uid'] in visible_error_ids
    ]
    errors_under_cursor = [
        error
        for error in errors_on_line
        if error['start'] <= col <= error['end']
    ]

    errors_to_show = errors_under_cursor or errors_on_line
    messages = [error['msg'] for error in errors_to_show]

    if row == prev_row and (
        len(errors_under_cursor) == 0
        or (
            len(_last_errors_under_cursor) == len(errors_under_cursor)
            and messages == _last_messages
        )
    ):
        html = None
    else:
        html = get_html(messages)

    _last_errors_under_cursor = errors_under_cursor
    _last_messages = messages

    if html and (len(errors_to_show) == 1 or errors_under_cursor):
        location = min(
            last_char_of_row(active_view, row),
            active_view.text_point(
                row, max(error['end'] for error in errors_to_show)
            ),
        )
        # Do not show the tooltip on the left side of the cursor
        if location < active_view.text_point(row, col):
            location = last_char_of_row(active_view, row)

    else:
        location = last_char_of_row(active_view, row)
    display_popup(active_view.id(), html, location)


def get_errors(view):
    return sorted(
        persist.errors[view.buffer_id()],
        key=lambda e: (e['line'], e['error_type'], e['start'], e['linter']),
    )


@lru_cache(maxsize=1)
def display_popup(vid, html, location):
    view = sublime.View(vid)
    if not html:
        view.hide_popup()
    elif view.is_popup_visible():
        view.update_popup(html)
    else:
        view.show_popup(
            html, sublime.COOPERATE_WITH_AUTO_COMPLETE, location=location
        )


def get_html(messages):
    message_divs = ''.join('<div>' + m + '</div>' for m in messages)
    return (
        (STYLESHEET + '<div class="container">' + message_divs + '</div>')
        if message_divs
        else ''
    )


def get_current_pos(view):
    try:
        sel = view.sel()[0]
        return view.rowcol(sel.begin()) if sel.empty() else (None, None)
    except (AttributeError, IndexError):
        return (None, None)


def last_char_of_row(view, row):
    return view.text_point(row + 1, 0) - 1
