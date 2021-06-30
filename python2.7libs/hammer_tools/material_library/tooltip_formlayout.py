class ToolTipFormLayout(object):
    def __init__(self):
        self._rows = []

    def addRow(self, label, value):
        self._rows.append((label, value))

    def __str__(self):
        text = '<p style="white-space:pre"><table border=\"0\">'
        for label, value in self._rows:
            text += '<tr> <td>{}</td><td>{}</td> </tr>'.format(label, value)
        text += '</table></p>'
        return text
