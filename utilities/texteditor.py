# Adapted from https://gist.github.com/LegoStormtroopr/6146161

from PyQt5 import QtGui, QtCore, QtWidgets


class myTextEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent, codingTabBrowser):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.sourceTab = parent
        self.codingTabs = codingTabBrowser
        self.textChanged.connect(self.textChange)
        self.undoAvailable['bool'].connect(self.undoStatus)
        self.changed = False

    def markAsSaved(self, state):
        self.changed = not state

    def undoStatus(self, s):
        if s == False:
            fname = self.codingTabs.tabText(self.codingTabs.indexOf(self.sourceTab))
            if (fname[-1] == '*'):
                self.codingTabs.setTabText(self.codingTabs.indexOf(self.sourceTab), fname[:-1])
                self.changed = False

    def textChange(self):
        fname = self.codingTabs.tabText(self.codingTabs.indexOf(self.sourceTab))
        if (fname[-1] != '*'):
            self.changed = True
            self.codingTabs.setTabText(self.codingTabs.indexOf(self.sourceTab), fname + '*')

    def keyPressEvent(self, event):
        # Shift + Tab is not the same as trying to catch a Shift modifier and a tab Key.
        # Shift + Tab is a Backtab!!
        cursor = self.textCursor()

        if event.key() == QtCore.Qt.Key.Key_Tab:
            if cursor.selectionStart() == cursor.selectionEnd():
                return QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

            tab = "\t"
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(end)
            cursor.movePosition(cursor.EndOfLine)
            end = cursor.position()
            cursor.setPosition(start)
            cursor.movePosition(cursor.StartOfLine)
            start = cursor.position()
            while cursor.position() < end:
                cursor.movePosition(cursor.StartOfLine)
                cursor.insertText(tab)
                # end += tab.count()
                cursor.movePosition(cursor.EndOfLine)
                cursor.movePosition(QtGui.QTextCursor.Right, 1)

        elif event.key() == QtCore.Qt.Key.Key_Backtab:
            self.unindentSelectedBlock()
            return

            # Copy the current selection
            pos = cursor.position()  # Where a selection ends
            anchor = cursor.anchor()  # Where a selection starts (can be the same as above)
            # Can put QtGui.QTextCursor.MoveAnchor as the 2nd arg, but this is the default
            cursor.setPosition(pos)
            # Move the position back one, selection the character prior to the original position
            cursor.setPosition(pos - 1, QtGui.QTextCursor.KeepAnchor)

            if str(cursor.selectedText()) == "\t":
                # The prior character is a tab, so delete the selection
                cursor.removeSelectedText()
                # Reposition the cursor with the one character offset
                cursor.setPosition(anchor - 1)
                cursor.setPosition(pos - 1, QtGui.QTextCursor.KeepAnchor)
            else:
                # Try all of the above, looking before the anchor (This helps if the achor is before a tab)
                cursor.setPosition(anchor)
                cursor.setPosition(anchor - 1, QtGui.QTextCursor.KeepAnchor)
                if str(cursor.selectedText()) == "\t":
                    self.unindentSelectedBlock()
                    return
                    cursor.removeSelectedText()
                    cursor.setPosition(anchor - 1)
                    cursor.setPosition(pos - 1, QtGui.QTextCursor.KeepAnchor)
                else:
                    # Its not a tab, so reset the selection to what it was
                    cursor.setPosition(anchor)
                    cursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        else:
            return QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

    def unindentSelectedBlock(self):
        cursor = self.textCursor()
        # Copy the current selection

        # Save the current cursor position
        original_position = cursor.position()

        # Get the selected text
        selected_text = cursor.selectedText()
        # Perform replacement on the selected text
        modified_text = selected_text.replace('\u2029\t', '\u2029')
        if modified_text.startswith('\t'):
            print('remove starting tab')
            modified_text=modified_text[1:]

        #print('unindent', selected_text, modified_text)
        # Replace the original selected block with the modified text
        cursor.removeSelectedText()
        cursor.insertText(modified_text)

        # Restore the cursor position
        cursor.setPosition(original_position)

        # Set the cursor position to the updated position
        self.setTextCursor(cursor)