from collections import defaultdict

import sublime
import sublime_plugin

from SublimeLinter.lint import persist, events

from . import settings


Settings = settings.Settings('SublimeLinter-addon-alt-ui')

PHANTOM_SET_NAME = 'sublime_linter'

State = {}
PhantomSets = {}
LastErrors = defaultdict(list)
Phantoms = defaultdict(dict)
InvalidBuffer = set()


def get_phantom_set_for_view(view):
    try:
        return PhantomSets[view.id()]
    except KeyError:
        set = PhantomSets[view.id()] = sublime.PhantomSet(
            view, PHANTOM_SET_NAME
        )
        return set


def plugin_loaded():
    events.subscribe(events.LINT_RESULT, on_lint_result)

    State.update(
        {'active_view': sublime.active_window().active_view(), 'errors': []}
    )


def plugin_unloaded():
    events.unsubscribe(events.LINT_RESULT, on_lint_result)

    for vid in PhantomSets.keys():
        view = sublime.View(vid)
        if view:
            clear_phantoms(view)


def on_lint_result(buffer_id, **kwargs):
    active_view = State['active_view']
    if active_view.buffer_id() != buffer_id:
        return

    InvalidBuffer.discard(buffer_id)
    State.update({'errors': get_errors(active_view)})
    draw(**State)


class ShowPhantomsCommand(sublime_plugin.EventListener):
    def on_activated_async(self, active_view):
        State.update(
            {'active_view': active_view, 'errors': get_errors(active_view)}
        )

    def on_modified(self, view):
        active_view = State['active_view']
        # It is possible that views (e.g. panels) update in the background.
        # So we check here and return early.
        if active_view.buffer_id() != view.buffer_id():
            return

        InvalidBuffer.add(active_view.buffer_id())

    def on_selection_modified_async(self, view):
        active_view = State['active_view']
        # It is possible that views (e.g. panels) update in the background.
        # So we check here and return early.
        if active_view.buffer_id() != view.buffer_id():
            return

        sublime.set_timeout(lambda: draw(**State), 1)


def get_errors(view):
    errors = sorted(
        persist.errors[view.buffer_id()],
        key=lambda e: (e['line'], e['error_type'], e['start'], e['linter']),
    )
    errors_by_line = defaultdict(list)
    for error in errors:
        pos = view.text_point(error['line'], error['start'])
        row, _col = view.rowcol(pos)
        if row != error['line']:  # for now skip multi-line errors
            continue
        errors_by_line[row].append(error)
    return errors_by_line


def clear_phantoms(view):
    view.erase_phantoms(PHANTOM_SET_NAME)


def draw(active_view, errors, margin=1, **kwargs):
    if not Settings.get('annotations', False):
        return

    if active_view.buffer_id() in InvalidBuffer:
        return

    phantom_set = get_phantom_set_for_view(active_view)
    vid = active_view.id()

    needs_update = LastErrors[vid] != errors

    if needs_update:
        LastErrors[vid] = errors
        all_phantoms = Phantoms[vid] = gen_phantoms(active_view, errors)
    else:
        all_phantoms = Phantoms[vid]

    # If you set a margin, phantoms around the current,
    # edited line will not be drawn to reduce clutter.
    cr = current_row(active_view)
    rg = range(cr - margin + 1, cr + margin) if cr is not None else []
    phantoms = [
        phantom for row, phantom in all_phantoms.items() if row not in rg
    ]
    phantom_set.update(phantoms)


def gen_phantoms(view, all_errors):
    # type: (...) -> Dict[Row, Phantom]

    phantoms = {}
    for (row, errors) in all_errors.items():
        html = style_messages({error['msg'] for error in errors})

        last_char = last_char_of_row(view, row)
        region = sublime.Region(last_char)
        layout = sublime.LAYOUT_INLINE

        phantoms[row] = sublime.Phantom(region, html, layout)

    return phantoms


def style_messages(messages):
    html = (
        '<div style="'
        'background-color: #e62d96; '
        'background-color: #ff3737; '
        'background-color: #df5912; '
        'background-color: #af1912; '
        'background-color: transparent; '
        # 'border-left: 2px solid #df5912;'
        'border-left: 1px solid #777;'
        'border-right: 1px solid #777;'
        # 'background-color: #111; '
        'font-size: .9em;'
        'word-wrap: break-word;'
        'color: #777; '
        # 'color: #110; '
        # 'color: #ddd; '
        # 'color: #df5912; '
        'padding: 0px 6px; '
        'margin-top: 2px; '
        'margin-left: 8px;'
        #
        # 'padding: 0px 1px; '
        # 'margin-top: 1px; '
        # 'margin-left: 3px;'
        '">'
    )
    for message in messages:
        html += "<span>{}</span> ".format(message)
        break

    html += "</div>"
    return html


def current_row(view):
    try:
        cursor = view.sel()[0]
    except IndexError:
        return

    row, _ = view.rowcol(cursor.begin())
    return row


def last_char_of_row(view, row):
    return view.text_point(row + 1, 0) - 1
