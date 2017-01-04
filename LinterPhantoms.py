import sublime
import sublime_plugin
from SublimeLinter.lint import persist

from collections import defaultdict
import time


LEFT_IDENT = 15    # try to indent the phantoms bc it looks better
IDLE_TIME = 10000  # show phantoms after idle time

PhantomSets = {}
Cleared = set()
Active = True
LastErrors = defaultdict(list)
Phantoms = defaultdict(dict)

def get_phantom_set_for_view(view):
    try:
        return PhantomSets[view.id()]
    except KeyError:
        set = PhantomSets[view.id()] = sublime.PhantomSet(view, 'linter')
        return set


class ShowPhantomsCommand(sublime_plugin.EventListener):
    def __init__(self):
        self._timeout_token = None

    def on_post_save_async(self, view):
        if Active:
            show_phantoms(view)

    def on_modified_async(self, view):
        if Active:
            hide_phantoms(view)


    def on_selection_modified_async(self, view):
        if Active:
            timeout_token = self._timeout_token = time.time()
            sublime.set_timeout_async(
                lambda: self._timeout_handler(timeout_token, view), IDLE_TIME)

    def _timeout_handler(self, token, view):
        if token != self._timeout_token:
            return

        if Active:
            show_phantoms(view)


class ToggleLinterPhantomsCommand(sublime_plugin.WindowCommand):
    def run(self):
        global Active

        view = self.window.active_view()
        if view.id() not in Cleared:
            hide_phantoms(view)
            Active = False
        else:
            show_phantoms(view)
            Active = True

        sublime.status_message(
            'LintPhantoms is ' + ('active' if Active else 'inactive'))



def hide_phantoms(view):
    phantom_set = get_phantom_set_for_view(view)
    phantom_set.update([])
    Cleared.add(view.id())


def show_phantoms(view, margin=0):
    phantom_set = get_phantom_set_for_view(view)
    vid = view.id()
    if vid in Cleared:
        Cleared.remove(vid)

    try:
        current_errors = persist.errors[view.id()]
    except KeyError:
        current_errors = []

    needs_update = LastErrors[vid] != current_errors

    if needs_update:
        LastErrors[vid] = current_errors
        all_phantoms = Phantoms[vid] = gen_phantoms(view, current_errors)
    else:
        all_phantoms = Phantoms[vid]

    # I had this; ah well... If you set a margin, phantoms around the current,
    # edited line will not be drawn to reduce clutter.
    cr = current_row(view)
    rg = range(cr - margin, cr + margin) if cr else []
    phantoms = [phantom for row, phantom in all_phantoms.items()
                if row not in rg]
    phantom_set.update(phantoms)

    show_above_below_markers(view, all_phantoms)


def show_above_below_markers(view, all_phantoms):
    visible_region = view.visible_region()
    first_row, _ = view.rowcol(visible_region.begin())
    last_row, _ = view.rowcol(visible_region.end())

    above = False
    below = False
    for row in sorted(all_phantoms.keys()):
        if row < first_row - 1:
            above = True
        elif row > last_row + 1:
            if above:
                # If we're here we're below the visible region, and since we
                # only show above or below, we can break
                break
            below = True
        elif first_row - 1 < row < last_row + 1:
            # We already show phantoms within the visible region and don't want
            # to distract even more
            return

    # Although above and below could be True at the same time as a fact, we can
    # only show one popup at any time. So we just shortcut here:
    if above:
        content = style_messages([center('Errors above')])
        line_start = view.text_point(first_row, 0)
        view.show_popup(content, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                        max_width=800, location=line_start)
    if below:
        content = style_messages([center('Errors below')])
        line_start = view.text_point(last_row - 2, 0)
        view.show_popup(content, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                        max_width=800, location=line_start)


def center(text, cols=80, char='&nbsp;'):
    fill_len = (cols - len(text)) // 2
    fill = fill_len * char
    return fill + text + fill

def gen_phantoms(view, all_errors):
    # type: (...) -> Dict[Row, Phantom]

    phantoms = {}
    for (row, errors) in all_errors.items():
        html = style_messages({error[1] for error in errors})

        line_start = view.text_point(row, 0)
        prev_line_len = (line_start - 1) - view.text_point(row - 1, 0)
        region = sublime.Region(
            view.text_point(row - 1, min(LEFT_IDENT, prev_line_len)))
        layout = sublime.LAYOUT_BELOW

        phantoms[row] = sublime.Phantom(region, html, layout)

    return phantoms




def style_messages(messages):
    html = ('<div style="'
            # 'background-color: #e62d96; '
            # 'background-color: #af3912; '
            'background-color: #af1912; '
            'color: #fff; '
            'padding: 2px 4px">')
    for message in messages:
        html += "<div>{}</div>".format(message)

    html += "</div>"
    return html


def current_row(view):
    try:
        cursor = view.sel()[0]
    except IndexError:
        return

    selected_row, _ = view.rowcol(cursor.begin())
    return selected_row
