import os

from PyQt5.QtWidgets import QMessageBox

from orangewidget import gui, widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui, congruence

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

class OWWavefrontFileWriter(widget.OWWidget):
    name = "Generic Wavefront  File Writer"
    description = "Utility: Wofry Wavefront  File Writer"
    icon = "icons/file_writer.png"
    maintainer = "Manuel Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 6
    category = "Utility"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 0

    file_name = Setting("")
    is_automatic_run= Setting(1)

    inputs = [("GenericWavefront2D" , GenericWavefront2D, "setGenericWavefront2D" )]


    wavefront = None

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Write HDF5 File", self)
        self.runaction.triggered.connect(self.write_file)
        self.addAction(self.runaction)

        self.setFixedWidth(590)
        self.setFixedHeight(180)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "HDF5 File Selection", addSpace=True, orientation="vertical",
                                         width=570, height=100)

        gui.checkBox(left_box_1, self, 'is_automatic_run', 'Automatic Execution')

        gui.separator(left_box_1, height=10)

        figure_box = oasysgui.widgetBox(left_box_1, "", addSpace=True, orientation="horizontal", width=550, height=50)

        self.le_file_name = oasysgui.lineEdit(figure_box, self, "file_name", "File Name",
                                                    labelWidth=120, valueType=str, orientation="horizontal")
        self.le_file_name.setFixedWidth(330)

        gui.button(figure_box, self, "...", callback=self.selectFile)

        gui.separator(left_box_1, height=10)

        button = gui.button(self.controlArea, self, "Write File", callback=self.write_file)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

    def selectFile(self):
        self.le_file_name.setText(oasysgui.selectFileFromDialog(self, self.file_name, "Open HDF5 File"))

    def setGenericWavefront2D(self, data):
        if not data is None:
            self.wavefront = data

            if self.is_automatic_run:
                self.write_file()

    def write_file(self):
        self.setStatusMessage("")

        try:
            if not self.wavefront is None:
                congruence.checkDir(self.file_name)

                self.wavefront.save_h5_file(self.file_name)

                path, file_name = os.path.split(self.file_name)

                self.setStatusMessage("File Out: " + file_name)

            else:
                QMessageBox.critical(self, "Error",
                                     "Wavefront Data not present",
                                     QMessageBox.Ok)
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    a = QApplication(sys.argv)
    ow = OWWavefrontFileWriter()
    ow.file_name = "tmp.h5"

    ow.show()
    a.exec_()