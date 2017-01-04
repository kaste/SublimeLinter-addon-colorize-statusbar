import sublime
import sublime_plugin
from SublimeLinter.lint import highlight, persist

from collections import defaultdict

PhantomSets = {}
Cleared = set()
Active = True
LastErrors = defaultdict(list)
Phantoms = defaultdict(dict)

def PhantomSet(view):
    try:
        return PhantomSets[view.id()]
    except KeyError:
        set = sublime.PhantomSet(view, 'linter')
        PhantomSets[view.id()] = set
        return set


class ClearLinterPhantomsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global Active

        view = self.view
        phantom_set = PhantomSet(view)
        if view.id() not in Cleared:
            phantom_set.update([])
            Cleared.add(view.id())
            Active = False
        else:
            Active = not Active
            if Active:
                Cleared.remove(view.id())
                show_phantoms(view, phantom_set, force=True)

        sublime.status_message('LintPhantoms is ' +
                               ('active' if Active else 'inactive'))




def show_phantoms(view, phantom_set, force=False, margin=10):
    vid = view.id()
    if vid in Cleared:
        force = True
        Cleared.remove(vid)

    try:
        current_errors = persist.errors[view.id()]
    except KeyError:
        current_errors = []

    needs_update = force is True or LastErrors[vid] != current_errors

    if needs_update:
        LastErrors[vid] = current_errors
        all_phantoms = gen_phantoms(view, current_errors)
        Phantoms[vid] = all_phantoms
    else:
        all_phantoms = Phantoms[vid]

    cr = current_row(view)
    rg = range(cr - 5, cr + 15) if cr else []
    phantoms = [phantom for row, phantom in all_phantoms.items()
                if row not in rg]
    phantom_set.update(phantoms)

    # show_above_below_markers(view, all_phantoms)


def show_above_below_markers(view, all_phantoms):
    visible_region = view.visible_region()
    first_row, _ = view.rowcol(visible_region.begin())
    last_row, _ = view.rowcol(visible_region.end())
    print(first_row, last_row)
    above = False
    below = False
    within = False
    for row in all_phantoms.keys():
        if row < first_row - 1:
            above = True
        elif row > last_row + 1:
            below = True
        elif first_row - 1 < row < last_row + 1:
            within = True

    if not within:
        if above:
            print('above')
            content = style_messages(['Errors above'])
            view.show_popup(content, sublime.COOPERATE_WITH_AUTO_COMPLETE,
                            max_width=600, location=visible_region.begin() + 1)
        if below:
            content = style_messages(['Errors below'])
            view.show_popup(content, 0,
                            max_width=600, location=visible_region.end())



def gen_phantoms(view, all_errors):
    phantoms = {}
    for (row, errors) in all_errors.items():
        html = style_messages({error[1] for error in errors})

        line_start = view.text_point(row, 0)
        prev_line_len = line_start - 1 - view.text_point(row - 1, 0)
        if prev_line_len == 0:
            region = sublime.Region(view.text_point(row - 1, 0))
            layout = sublime.LAYOUT_BLOCK
        else:
            region = sublime.Region(
                view.text_point(row - 1, min(20, prev_line_len)))
            layout = sublime.LAYOUT_BELOW


        if row == layout:
            region = sublime.Region()

        phantoms[row] = sublime.Phantom(
            region,
            html,
            layout)

    return phantoms




def style_messages(messages):
    html = ('<div style="'
            'background-color: #e62d96; '
            # 'background-color: #af3912; '
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


class ViewViewer(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view

    def on_selection_modified(self):
        if not Active:
            return

        sublime.set_timeout_async(
            lambda: show_phantoms(self.view, PhantomSet(self.view), margin=10),
            3000)


class ViewCalculator(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self.timeout_scheduled = 0

        self.update_phantoms()

    def update_phantoms(self):
        show_phantoms(self.view, PhantomSet(self.view))

    def handler(self):
        self.timeout_scheduled -= 1
        if self.timeout_scheduled == 0:
            self.update_phantoms()

    def on_activated_async(self):
        if not Active:
            return

        self.timeout_scheduled += 1
        sublime.set_timeout(lambda: self.handler(), 1000)

    def on_modified_async(self):
        if not Active:
            return

        self.timeout_scheduled += 1
        sublime.set_timeout(lambda: self.handler(), 2500)
        # sublime.set_timeout(lambda: self.update_phantoms(), 10)
        # self.update_phantoms()

