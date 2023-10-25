#Adapted from https://gist.github.com/LegoStormtroopr/6146161

from PyQt5 import QtGui,QtCore,QtWidgets

class myTextEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent):
        QtWidgets.QPlainTextEdit.__init__(self, parent)

    def keyPressEvent(self, event):
        # Shift + Tab is not the same as trying to catch a Shift modifier and a tab Key.
        # Shift + Tab is a Backtab!!
        if event.key() == QtCore.Qt.Key.Key_Tab:
            tab = "\t"
            cursor = self.textCursor()
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
                #end += tab.count()
                cursor.movePosition(cursor.EndOfLine)
                cursor.movePosition(QtGui.QTextCursor.Right, 1)
        elif event.key() == QtCore.Qt.Key.Key_Backtab:
            cur = self.textCursor()
            # Copy the current selection
            pos = cur.position()  # Where a selection ends
            anchor = cur.anchor()  # Where a selection starts (can be the same as above)
            # Can put QtGui.QTextCursor.MoveAnchor as the 2nd arg, but this is the default
            cur.setPosition(pos)

            # Move the position back one, selection the character prior to the original position
            cur.setPosition(pos - 1, QtGui.QTextCursor.KeepAnchor)

            if str(cur.selectedText()) == "\t":
                # The prior character is a tab, so delete the selection
                cur.removeSelectedText()
                # Reposition the cursor with the one character offset
                cur.setPosition(anchor - 1)
                cur.setPosition(pos - 1, QtGui.QTextCursor.KeepAnchor)
            else:
                # Try all of the above, looking before the anchor (This helps if the achor is before a tab)
                cur.setPosition(anchor)
                cur.setPosition(anchor - 1, QtGui.QTextCursor.KeepAnchor)
                if str(cur.selectedText()) == "\t":
                    cur.removeSelectedText()
                    cur.setPosition(anchor - 1)
                    cur.setPosition(pos - 1, QtGui.QTextCursor.KeepAnchor)
                else:

                    # Its not a tab, so reset the selection to what it was
                    cur.setPosition(anchor)
                    cur.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        else:
            return QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
