import sublime
import sublime_plugin
from SublimeLinter.lint import persist, highlight

from collections import defaultdict

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
    def on_post_save_async(self, view):
        if Active:
            show_phantoms(view)

    def on_modified_async(self, view):
        if Active:
            hide_phantoms(view)


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

    cr = current_row(view)
    rg = range(cr - margin, cr + margin) if cr else []
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
    # type: (...) -> Dict[Row, Phantom]

    phantoms = {}
    for (row, errors) in all_errors.items():
        html = style_messages({error[1] for error in errors})

        line_start = view.text_point(row, 0)
        prev_line_len = (line_start - 1) - view.text_point(row - 1, 0)
        region = sublime.Region(
            view.text_point(row - 1, min(20, prev_line_len)))
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


