#################################################

# EasyLoggeer start file

#################################################

if __name__ == "__main__":
    from PyQt4 import QtCore, QtGui
    from res.window import *

    app = QtGui.QApplication([])
    window = Graph()
    window.show()
    exit(app.exec_())


#################################################
