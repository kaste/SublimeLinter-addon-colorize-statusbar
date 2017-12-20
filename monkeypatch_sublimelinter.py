
import sublime
import sublime_plugin

from SublimeLinter import sublime_linter


old_highlight = None
old_clear = None


"""
Monkeypatch core SublimeLinter so that it will send events after linting a
file has finished.

For convenience, a class is provided which users can inherit from. A new
`on_linter_finished_async` callback must be implemented by the user. It gets
called with exactly one argument, the view which has been linted.


    class MySuperNewAnnotator(sublime_plugin.EventListener,
                              CatchSublimeLinterRuns):

        def on_linter_finished_async(self, view):
            # Do something useful here
            ...


"""

BROADCAST_COMMAND = 'sublime_linter_broadcast'
FINISHED = 'FINISHED'
CLEAR = 'CLEAR'


def plugin_loaded():
    global old_highlight
    global old_clear

    old_highlight = sublime_linter.SublimeLinter.highlight
    old_clear = sublime_linter.SublimeLinter.clear

    def new_highlight(self, view, linters, hit_time):
        old_highlight(self, view, linters, hit_time)
        view.window().run_command(BROADCAST_COMMAND, {
            'vid': view.id(), 'action': FINISHED
        })

    def new_clear(self, view):
        old_clear(self, view)
        view.window().run_command(BROADCAST_COMMAND, {
            'vid': view.id(), 'action': CLEAR
        })

    sublime_linter.SublimeLinter.highlight = new_highlight
    sublime_linter.SublimeLinter.clear = new_clear


def plugin_unloaded():
    global old_highlight
    global old_clear

    if old_highlight:
        sublime_linter.SublimeLinter.highlight = old_highlight

    if old_clear:
        sublime_linter.SublimeLinter.clear = old_clear


# Without a real listener, sublime will *NOT* issue the event at all,
# so we must register a dummy listener here.
class SublimeLinterBroadcast(sublime_plugin.WindowCommand):
    def run(self, *args, **kwargs):
        pass


class CatchSublimeLinterRuns:
    def on_window_command(self, window, command_name, kwargs):
        if command_name != BROADCAST_COMMAND:
            return

        vid = kwargs['vid']
        action = kwargs['action']

        for view in window.views():
            if view.id() == vid:
                if action == FINISHED:
                    sublime.set_timeout_async(
                        lambda: self.on_linter_finished_async(view))
                elif action == CLEAR:
                    sublime.set_timeout_async(
                        lambda: self.on_clear_async(view))

                break

    def on_linter_finished_async(self, view):
        """Callback to be invoked after a view has been linted."""
        pass

    def on_clear_async(self, view):
        """Callback to be invoked after a view has been linted."""
        pass

