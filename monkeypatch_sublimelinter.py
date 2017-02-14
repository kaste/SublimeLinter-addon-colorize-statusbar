
import sublime
import sublime_plugin

from SublimeLinter import sublimelinter
old_fn = None


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

LINTER_FINISHED = 'sublinter_finished'


def plugin_loaded():
    global old_fn

    old_fn = sublimelinter.SublimeLinter.highlight

    def replacement(self, view, linters, hit_time):
        old_fn(self, view, linters, hit_time)

        view.window().run_command(LINTER_FINISHED, {'vid': view.id()})

    sublimelinter.SublimeLinter.highlight = replacement


def plugin_unloaded():
    global old_fn

    if old_fn:
        sublimelinter.SublimeLinter.highlight = old_fn


# Without a real listener, sublime will *NOT* issue the event at all,
# so we must register a dummy listener here.
class SublinterFinished(sublime_plugin.WindowCommand):
    def run(self, *args, **kwargs):
        pass


class CatchSublimeLinterRuns:
    def on_window_command(self, window, command_name, kwargs):
        if command_name != LINTER_FINISHED:
            return
        vid = kwargs['vid']

        for view in window.views():
            if view.id() == vid:
                sublime.set_timeout_async(
                    lambda: self.on_linter_finished_async(view))
                return

    def on_linter_finished_async(self, view):
        """Callback to be invoked when a view has been linted."""
        pass
