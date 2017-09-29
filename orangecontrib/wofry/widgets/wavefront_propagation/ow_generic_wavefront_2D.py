import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class OWGenericWavefront2D(WofryWidget):

    name = "Generic Wavefront 2D"
    id = "GenericWavefront2D"
    description = "Generic Wavefront 2D"
    icon = "icons/gw2d.png"
    priority = 2

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"GenericWavefront2D",
                "type":GenericWavefront2D,
                "doc":"GenericWavefront2D",
                "id":"GenericWavefront2D"}]

    units = Setting(1)
    energy = Setting(1000.0)
    wavelength = Setting(1e-10)
    number_of_points_h = Setting(100)
    number_of_points_v = Setting(100)

    initialize_from = Setting(0)

    range_from_h  = Setting(-0.0005)
    range_to_h    = Setting(0.0005)
    steps_start_h = Setting(-0.0005)
    steps_step_h  = Setting(1e-6)
    range_from_v  = Setting(-0.0005)
    range_to_v    = Setting(0.0005)
    steps_start_v = Setting(-0.0005)
    steps_step_v  = Setting(1e-6)

    kind_of_wave = Setting(0)

    initialize_amplitude = Setting(0)
    complex_amplitude_re = Setting(1.0)
    complex_amplitude_im = Setting(0.0)
    radius = Setting(1.0)

    gaussian_sigma_h = Setting(0.001)
    gaussian_sigma_v = Setting(0.001)
    gaussian_amplitude = Setting(1.0)
    gaussian_mode_h = Setting(0)
    gaussian_mode_v = Setting(0)

    amplitude = Setting(1.0)
    phase = Setting(0.0)

    wavefront2D = None

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=False)

        self.runaction = widget.OWAction("Generate Wavefront", self)
        self.runaction.triggered.connect(self.generate)
        self.addAction(self.runaction)

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Generate", callback=self.generate)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        gui.separator(self.controlArea)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT + 50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Generic Wavefront 2D Settings")

        box_energy = oasysgui.widgetBox(self.tab_sou, "Energy Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_energy, self, "units", label="Units in use", labelWidth=350,
                     items=["Electron Volts", "Meters"],
                     callback=self.set_Units,
                     sendSelectedValue=False, orientation="horizontal")

        self.units_box_1 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_1, self, "energy", "Photon Energy [eV]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.units_box_2 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_2, self, "wavelength", "Photon Wavelength [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Units()

        box_space = oasysgui.widgetBox(self.tab_sou, "Space Settings", addSpace=False, orientation="vertical")

        number_of_points_box = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="horizontal")

        oasysgui.lineEdit(number_of_points_box, self, "number_of_points_h", "Number of Points                    (H)",
                          labelWidth=200, valueType=int, orientation="horizontal")
        oasysgui.lineEdit(number_of_points_box, self, "number_of_points_v", "x (V)",
                          valueType=int, orientation="horizontal")

        gui.comboBox(box_space, self, "initialize_from", label="Space Initialization", labelWidth=350,
                     items=["From Range", "From Steps"],
                     callback=self.set_Initialization,
                     sendSelectedValue=False, orientation="horizontal")

        self.initialization_box_1 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_from_h", "(H) From [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_to_h", "          To [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_from_v", "(V) From [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_to_v", "          To [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.initialization_box_2 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_start_h", "(H) Start [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_step_h", "      Step [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_start_v", "(V) Start [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_step_v", "      Step [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Initialization()

        box_amplitude = oasysgui.widgetBox(self.tab_sou, "Amplitude Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_amplitude, self, "kind_of_wave", label="Kind of Wave", labelWidth=350,
                     items=["Plane", "Spherical", "Gaussian", "Gaussian Shell Model"],
                     callback=self.set_KindOfWave,
                     sendSelectedValue=False, orientation="horizontal")


        self.plane_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)
        self.spherical_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)
        self.gaussian_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)
        self.gsm_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)

        # --- PLANE

        gui.comboBox(self.plane_box, self, "initialize_amplitude", label="Amplitude Initialization", labelWidth=350,
                     items=["Complex", "Real"],
                     callback=self.set_Amplitude,
                     sendSelectedValue=False, orientation="horizontal")

        self.amplitude_box_1 = oasysgui.widgetBox(self.plane_box, "", addSpace=False, orientation="horizontal", height=50)

        oasysgui.lineEdit(self.amplitude_box_1, self, "complex_amplitude_re", "Complex Amplitude ",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.amplitude_box_1, self, "complex_amplitude_im", " + ",
                          valueType=float, orientation="horizontal")

        oasysgui.widgetLabel(self.amplitude_box_1, "i", labelWidth=15)

        self.amplitude_box_2 = oasysgui.widgetBox(self.plane_box, "", addSpace=False, orientation="vertical", height=50)

        oasysgui.lineEdit(self.amplitude_box_2, self, "amplitude", "Amplitude",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.amplitude_box_2, self, "phase", "Phase",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Amplitude()

        # ------ SPHERIC

        oasysgui.lineEdit(self.spherical_box, self, "radius", "Radius [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        amplitude_box_3 = oasysgui.widgetBox(self.spherical_box, "", addSpace=False, orientation="horizontal", height=50)

        oasysgui.lineEdit(amplitude_box_3, self, "complex_amplitude_re", "Complex Amplitude ",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(amplitude_box_3, self, "complex_amplitude_im", " + ",
                          valueType=float, orientation="horizontal")

        oasysgui.widgetLabel(amplitude_box_3, "i", labelWidth=15)

        # ---- GAUSSIAN

        oasysgui.lineEdit(self.gaussian_box, self, "gaussian_sigma_h", "Sigma (H)",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gaussian_box, self, "gaussian_sigma_v", "Sigma (V)",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gaussian_box, self, "gaussian_amplitude", "Amplitude of the Spectral Density",
                          labelWidth=250, valueType=float, orientation="horizontal")

        # ---- GAUSSIAN SHELL MODEL

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_sigma_h", "Sigma (H)",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_sigma_v", "Sigma (V)",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_amplitude", "Amplitude of the Spectral Density",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_mode_h", "Mode (H)",
                          labelWidth=250, valueType=int, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_mode_v", "Mode (V)",
                          labelWidth=250, valueType=int, orientation="horizontal")

        self.set_KindOfWave()


    def set_Units(self):
        self.units_box_1.setVisible(self.units == 0)
        self.units_box_2.setVisible(self.units == 1)

    def set_Initialization(self):
        self.initialization_box_1.setVisible(self.initialize_from == 0)
        self.initialization_box_2.setVisible(self.initialize_from == 1)

    def set_Amplitude(self):
        self.amplitude_box_1.setVisible(self.initialize_amplitude == 0)
        self.amplitude_box_2.setVisible(self.initialize_amplitude == 1)

    def set_KindOfWave(self):
        self.plane_box.setVisible(self.kind_of_wave == 0)
        self.spherical_box.setVisible(self.kind_of_wave == 1)
        self.gaussian_box.setVisible(self.kind_of_wave == 2)
        self.gsm_box.setVisible(self.kind_of_wave == 3)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Wavefront 1D"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def check_fields(self):
        if self.units == 0:
            congruence.checkStrictlyPositiveNumber(self.energy, "Energy")
        else:
            congruence.checkStrictlyPositiveNumber(self.wavelength, "Wavelength")

        congruence.checkStrictlyPositiveNumber(self.number_of_points_h, "Number of Points (H)")
        congruence.checkStrictlyPositiveNumber(self.number_of_points_v, "Number of Points (V)")

        if self.initialize_from == 0:
            congruence.checkGreaterThan(self.range_to_h, self.range_from_h, "(H) Range To", "Range From")
            congruence.checkGreaterThan(self.range_to_v, self.range_from_v, "(V) Range To", "Range From")
        else:
            congruence.checkStrictlyPositiveNumber(self.steps_step_h, "Step (H)")
            congruence.checkStrictlyPositiveNumber(self.steps_step_v, "Step (V)")

        if self.kind_of_wave == 1:
            congruence.checkStrictlyPositiveNumber(numpy.abs(self.radius), "Radius")
        elif self.kind_of_wave > 1:
            congruence.checkStrictlyPositiveNumber(self.gaussian_sigma_h, "Sigma (H)")
            congruence.checkStrictlyPositiveNumber(self.gaussian_sigma_v, "Sigma (V)")
            congruence.checkStrictlyPositiveNumber(self.gaussian_amplitude, "Amplitude of the Spectral Density")

            if self.kind_of_wave == 3:
                congruence.checkPositiveNumber(self.gaussian_mode_h, "Mode (H)")
                congruence.checkPositiveNumber(self.gaussian_mode_v, "Mode (V)")

    def generate(self):
        try:
            self.progressBarInit()

            self.check_fields()

            if self.initialize_from == 0:
                self.wavefront2D = GenericWavefront2D.initialize_wavefront_from_range(x_min=self.range_from_h, x_max=self.range_to_h,
                                                                                      y_min=self.range_from_v, y_max=self.range_to_v,
                                                                                      number_of_points=(self.number_of_points_h, self.number_of_points_v))
            else:
                self.wavefront2D = GenericWavefront2D.initialize_wavefront_from_steps(x_start=self.steps_start_h, x_step=self.steps_step_h,
                                                                                      y_start=self.steps_start_v, y_step=self.steps_step_v,
                                                                                      number_of_points=(self.number_of_points_h, self.number_of_points_v))

            if self.units == 0:
                self.wavefront2D.set_photon_energy(self.energy)
            else:
                self.wavefront2D.set_wavelength(self.wavelength)

            if self.kind_of_wave == 0: #plane
                if self.initialize_amplitude == 0:
                    self.wavefront2D.set_plane_wave_from_complex_amplitude(complex_amplitude=complex(self.complex_amplitude_re, self.complex_amplitude_im))
                else:
                    self.wavefront2D.set_plane_wave_from_amplitude_and_phase(amplitude=self.amplitude, phase=self.phase)
            elif self.kind_of_wave == 1: # spheric
                self.wavefront2D.set_spherical_wave(radius=self.radius, complex_amplitude=complex(self.complex_amplitude_re, self.complex_amplitude_im))
            elif self.kind_of_wave == 2: # gaussian
                self.wavefront2D.set_gaussian(sigma_x=self.gaussian_sigma_h,
                                              sigma_y=self.gaussian_sigma_v,
                                              amplitude=self.gaussian_amplitude)
            elif self.kind_of_wave == 3: # g.s.m.
                self.wavefront2D.set_gaussian_hermite_mode(sigma_x=self.gaussian_sigma_h,
                                                           sigma_y=self.gaussian_sigma_v,
                                                           amplitude=self.gaussian_amplitude,
                                                           nx=self.gaussian_mode_h,
                                                           ny=self.gaussian_mode_v)

            self.initializeTabs()
            self.plot_results()

            self.send("GenericWavefront2D", self.wavefront2D)
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            #raise exception

            self.progressBarFinished()

    def do_plot_results(self, progressBarValue):
        if not self.wavefront2D is None:

            self.progressBarSet(progressBarValue)

            titles = ["Wavefront 2D Intensity"]

            self.plot_data2D(data2D=self.wavefront2D.get_intensity(),
                             dataX=self.wavefront2D.get_coordinate_x(),
                             dataY=self.wavefront2D.get_coordinate_y(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=titles[0],
                             xtitle="Horizontal Coordinate",
                             ytitle="Vertical Coordinate")


            self.plot_canvas[0].resetZoom()

            self.progressBarFinished()
