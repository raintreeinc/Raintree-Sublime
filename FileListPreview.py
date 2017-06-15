import functools
import re
import os
import sublime
import sublime_plugin

class FileListPreview(sublime_plugin.ViewEventListener):
	pending = 0
	opened = ""

	@classmethod
	def is_applicable(cls, settings):
		syntax = settings.get('syntax')
		return syntax == "Packages/Raintree/FileList.sublime-syntax"

	def on_selection_modified(self):
		self.pending = self.pending + 1
		sublime.set_timeout_async(self.timeout, 100)

	def timeout(self):
		self.pending = self.pending - 1
		if self.pending == 0:
			self.trigger()

	def trigger(self):
		selection = self.view.sel()[0]
		if selection.b - selection.a == 0:
			selection = self.view.expand_by_class(selection, 
				sublime.CLASS_LINE_START|sublime.CLASS_LINE_END, "\n")
		word = self.view.substr(selection)
		word = word.strip()

		m = re.search('^([a-zA-Z]:\\\\)?([^:]+):(\\-?[0-9]+):(\\-?[0-9]+)?:?', word)
		if not m:
			return

		drive = m.group(1)
		localfile = m.group(2)
		lineno = m.group(3)
		colno = m.group(4)

		path = drive + localfile
		filespec = drive + localfile
		if int(lineno) >= 1:
			filespec = filespec + ":" + lineno
			if int(colno) >= 0:
				filespec = filespec + ":" + colno

		if not os.path.isfile(path):
			return
		self.open_transient(filespec)

	def open_transient(self, filespec):
		if filespec == self.opened:
			return
		self.opened = filespec

		window = sublime.active_window()
		preview = window.open_file(filespec, sublime.ENCODED_POSITION | sublime.TRANSIENT)
		window.set_view_index(preview, 1, -1)
		window.focus_view(self.view)
