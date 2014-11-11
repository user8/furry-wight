#################################################

# Main window and program main functionality

#################################################

from PyQt4 import QtCore, QtGui
from config import *
from res.gdproc import *
import time, subprocess

#------------------------------------------------

class Graph(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle("EasyLogger")
        self.resize(*params['window_size'])
        self.setStyleSheet("background-color: black;")
        self.setMouseTracking(True)
        self.icon = QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage("res/icon.png")))
        self.setWindowIcon(self.icon)

        self.tray = QtGui.QSystemTrayIcon()
        self.tray.activated.connect(self.toggleWindow)
        self.tray.setIcon(self.icon)
        self.tray.show()

        self.image = QtGui.QPixmap(self.size())
        self.image.fill(QtCore.Qt.black)
        self.grid = QtGui.QPixmap(self.size())
        self.grid.fill(QtCore.Qt.white)
        self.ip = QtGui.QPainter(self.image)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.getData)

        if params['log']:
            t = time.time()
            ft = "{0}-{1:02d}-{2:02d}--{3:02d}-{4:02d}-{9:06.3f}".format(*(time.localtime(t)+(t%60,)))
            self.log_file = open('log/' + ft +'.log', 'w')

        self.channels_queue = [ [1,2], [1], [2], [2/1] ]
        self.X = [0, 0]
        self.vlines = [0, 0]
        self.XY_mode = False
        self.XY_pre = None

        if type(params['channels'][0]) == float:
            self.XY_mode = True

        self.c1_data, self.c2_data  = [0], [0]
        self.c1ad, self.c2ad = [], []
        self.avg_data = [0, 0]

        if channel_1['draw_avg']:
            channel_1['draw_by']  = 1
            channel_1['latest_n'] = 1
        if channel_2['draw_avg']:
            channel_2['draw_by']  = 1
            channel_2['latest_n'] = 1

        self.p = GetDataProcess(params['read_samples'])
        self.set_latency()
        self.p.start()

        time.clock()
        self.timer.start(params['refresh_ms'])

#------------------------------------------------

    def getData(self):
        c1d, c2d = [], []
        while not self.p.Q.empty():
            data = self.p.Q.get()
            c1d += data[0]
            c2d += data[1]

        if (1 in params['channels'] or self.XY_mode) and not channel_1['draw_avg']:
            self.c1_data = self.c1_data + c1d
        if (2 in params['channels'] or self.XY_mode) and not channel_2['draw_avg']:
            self.c2_data = self.c2_data + c2d

        if c1d:
            self.c1ad = (self.c1ad + c1d)[-channel_1['avg_by']:]
            self.avg_data[0] = channel_1['function'](sum(self.c1ad) / len(self.c1ad))
            self.c2ad = (self.c2ad + c2d)[-channel_2['avg_by']:]
            self.avg_data[1] = channel_2['function'](sum(self.c2ad) / len(self.c2ad))

            if params['log']:
                self.log_file.write(str(time.time()) + '\t' + str(self.avg_data[0]) + '\t' + str(self.avg_data[1]) + '\n')

        self.drawOnImage()

        if self.isVisible():
            self.update()
        elif params['tray_icon_draw']:
            self.updateIcon()

#------------------------------------------------

    def drawOnImage(self):

        t               = time.clock()
        draw_data       = [ self.c1_data,               self.c2_data ]
        funcs           = [ channel_1['function'],      channel_2['function'] ]
        draw_by         = [ channel_1['draw_by'],       channel_2['draw_by']  ]
        latest          = [ channel_1['latest_n'],      channel_2['latest_n'] ]
        r               = [ channel_1['f_range'],       channel_2['f_range']  ]
        colors          = [ channel_1['color_rgb'],     channel_2['color_rgb']]
        vline           = [ channel_1['vline_s'],       channel_2['vline_s']  ]
        draw_avg        = [ channel_1['draw_avg'],      channel_2['draw_avg'] ]

        if self.XY_mode:

            draw_by = min(draw_by)
            latest = min(latest)

            if params['channels'][0] < 1:
                draw_data.reverse()
                funcs.reverse()
                r.reverse()
                colors.reverse()

            lx = len(draw_data[0])
            ly = len(draw_data[1])
            l = min(lx, ly)

            if l >= draw_by:
                draw_data[0] = draw_data[0][-l:]
                draw_data[1] = draw_data[1][-l:]

                rcx = r[0][1] - r[0][0]
                rcy = r[1][1] - r[1][0]
                kx = self.width() / rcx
                ky = self.height() / rcy

                for j in range(l//draw_by)[:latest]:
                    if any(draw_avg):
                        data = [self.avg_data[0], self.avg_data[1]]
                        if params['channels'][0] < 1:
                            data.reverse()
                    else:
                        xdata = sum(draw_data[0][:draw_by]) / draw_by
                        ydata = sum(draw_data[1][:draw_by]) / draw_by
                        data = [funcs[0](xdata), funcs[1](ydata)]
                        draw_data[0] = draw_data[0][draw_by:]
                        draw_data[1] = draw_data[1][draw_by:]

                    x = (data[0] - r[0][0]) * kx
                    y = self.height() - (data[1] - r[1][0]) * ky

                    self.ip.fillRect(0,0, self.width(),self.height(), QtGui.QColor.fromRgba(0x02000000))

                    if self.XY_pre:
                        line_from = QtCore.QPointF(*self.XY_pre)
                    else:
                        line_from = QtCore.QPointF(x,y)

                    line_to = QtCore.QPointF(x,y)

                    self.ip.setPen(QtGui.QPen(QtGui.QColor.fromRgb(*colors[0]), 1.0))
                    self.ip.drawLine(line_from, line_to)
                    self.XY_pre = [x,y]

                min_max_len = min(self.max_len)
                if len(draw_data[0]) > min_max_len:
                    draw_data[0] = draw_data[0][-min_max_len:]
                if len(draw_data[1]) > min_max_len:
                    draw_data[1] = draw_data[1][-min_max_len:]

            if params['channels'][0] < 1:
                draw_data.reverse()

        else:

            height          = self.height() / len(params['channels'])
            x12             = self.X
            dots            = [ channel_1['dots'],          channel_2['dots'] ]

            for i, c in enumerate(params['channels']):
                if len(draw_data[c-1]) >= draw_by[c-1]:
                    rc = r[c-1][1]-r[c-1][0]
                    k = height / rc
                    for j in range(len(draw_data[c-1]) // draw_by[c-1])[:latest[c-1]]:
                        if draw_avg[c-1]:
                            data = self.avg_data[c-1]
                        else:
                            data = sum(draw_data[c-1][:draw_by[c-1]]) / draw_by[c-1]
                            draw_data[c-1] = draw_data[c-1][draw_by[c-1]:]
                            data = funcs[c-1](data)

                        line_height = (data-r[c-1][0]) * k
                        if line_height > height:
                            line_height = height
                        elif line_height < 0:
                            line_height = 0

                        self.ip.setPen(QtGui.QPen(QtCore.Qt.black, 0.5))
                        self.ip.drawLine(x12[c-1], height*i+1, x12[c-1], height*(i+1))

                        if dots[c-1]:
                            line_from = QtCore.QPointF(x12[c-1]-2, height*(i+1)-line_height)
                        else:
                            line_from = QtCore.QPointF(x12[c-1]-1, height*(i+1))
                        line_to = QtCore.QPointF(x12[c-1]-1, height*(i+1)-line_height)

                        self.ip.setPen(QtGui.QPen(QtGui.QColor.fromRgb(*colors[c-1]), 0.5))
                        self.ip.drawLine(line_from, line_to)

                        x12[c-1] += 1
                        x12[c-1] %= self.width()+1

                    if len(draw_data[c-1]) > self.max_len[c-1]:
                        draw_data[c-1] = draw_data[c-1][-self.max_len[c-1]:]


                if vline[c-1]:
                    self.ip.setPen(QtGui.QPen(QtCore.Qt.white, 0.15, QtCore.Qt.DashLine))
                    if t >= vline[c-1] * self.vlines[c-1]:
                        self.ip.drawLine(x12[c-1]-1, height*i+1, x12[c-1]-1, height*(i+1))

        self.c1_data, self.c2_data =  draw_data
        self.vlines[0] = t//vline[0] + 1
        self.vlines[1] = t//vline[1] + 1
#         self.setWindowTitle("%i, %i, %i, %i, %f" % (len(self.c1_data), len(self.c2_data), self.max_len[0], self.max_len[1], self.lat))

#------------------------------------------------

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.drawPixmap(0,0, self.image)
        p.drawPixmap(0,0, self.grid)
        p.setFont(QtGui.QFont("Verdana", 20))

        data = self.avg_data[:]
        text = [ (channel_1['text_val'], channel_1['digits'], channel_1['text_before'], channel_1['text_after'], channel_1['color_rgb']),
                 (channel_2['text_val'], channel_2['digits'], channel_2['text_before'], channel_2['text_after'], channel_2['color_rgb']) ]

        if self.XY_mode:

            if params['channels'][0] < 1:
                data.reverse()
                text.reverse()

            if text[0][0]:
                t = (text[0][2]+"%0."+str(text[0][1])+"f"+text[0][3]) % data[0]
                p.setPen(QtGui.QColor(*text[0][-1]))
                p.drawText(10, self.height()-20, t)
            if text[1][0]:
                t = (text[1][2]+"%0."+str(text[1][1])+"f"+text[1][3]) % data[1]
                p.setPen(QtGui.QColor(*text[1][-1]))
                p.drawText(10, 40, t)

        else:

            height = self.height() / len(params['channels'])

            for i, c in enumerate(params['channels']):
                if text[c-1][0]:
                    t = (text[c-1][2]+"%0."+str(text[c-1][1])+"f"+text[c-1][3]) % data[c-1]
                    p.setPen(QtGui.QColor(*text[c-1][-1]))
                    p.drawText(10, i*height+40, t)

#------------------------------------------------

    def gen_grids(ra, px, gr):
        rc = ra[1]-ra[0]
        k = px / rc
        for i, g in enumerate(gr):
            pen = 0.3/(i+1)
            if rc<0:
                jrange = range(int(rc/g),1)
            else:
                jrange = range(int(rc/g)+1)
            for j in jrange:
                mod = ra[0]%g
                val = j*g + ((g - mod) if mod else 0)
                co = px - val * k
                txt_val = str(round(ra[0]+val, 3))
                first = (abs(j)>0 and i==0)
                yield co, pen, txt_val, first


    def resizeEvent(self, event):
        self.ip.end()
        new_size = self.size()

        if event:
            old_image = self.image.copy()

        self.image = QtGui.QPixmap(new_size)
        self.image.fill(QtCore.Qt.black)
        self.grid = QtGui.QPixmap(new_size)
        self.grid.fill(QtCore.Qt.white)

        self.ip = QtGui.QPainter(self.image)
        self.ip.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        if event:
            if self.XY_mode:
                w = self.width()
            else:
                w = old_image.width()
            self.ip.drawPixmap(0, 0, w, self.height(), old_image)

        self.XY_pre = None

        grid_alpha = QtGui.QPixmap(new_size)
        grid_alpha.fill(QtCore.Qt.black)
        gp = QtGui.QPainter(grid_alpha)

        r       = [ channel_1['f_range'], channel_2['f_range'] ]
        grids   = [ channel_1['grids'],   channel_2['grids']   ]

        if self.XY_mode:

            if params['channels'][0] < 1:
                r.reverse()
                grids.reverse()

            for co, pen, txt_val, first in Graph.gen_grids(r[0], self.width(), grids[0]):
                co = self.width() - co
                gp.setPen(QtGui.QPen(QtCore.Qt.white, pen, QtCore.Qt.DotLine))
                gp.drawLine(co, 0, co, self.height())

                if params['grid_values'] and first:
                    gp.drawText(co-30, self.height()-10, txt_val)

            for co, pen, txt_val, first in Graph.gen_grids(r[1], self.height(), grids[1]):
                gp.setPen(QtGui.QPen(QtCore.Qt.white, pen, QtCore.Qt.DotLine))
                gp.drawLine(0, co, self.width(), co)

                if params['grid_values'] and first:
                    gp.drawText(self.width()-30, co+10, txt_val)

        else:

            height = self.height() / len(params['channels'])

            for i, c in enumerate(params['channels']):
                for co, pen, txt_val, first in Graph.gen_grids(r[c-1], height, grids[c-1]):
                    co = co + height*i
                    gp.setPen(QtGui.QPen(QtCore.Qt.white, pen, QtCore.Qt.DotLine))
                    gp.drawLine(0, co, self.width(), co)

                    if params['grid_values'] and first:
                        gp.drawText(self.width()-30, co+10, txt_val)

        gp.end()
        self.grid.setAlphaChannel(grid_alpha)

        self.tray.setIcon(self.icon)
        if event and event.oldSize():
            self.setWindowTitle("Window size: " + str(self.width()) + " x " + str(self.height()))

#------------------------------------------------

    def updateIcon(self):
        self.tray.setIcon(QtGui.QIcon(self.image.scaled(32,32)))

#------------------------------------------------

    def toggleWindow(self, reason):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.tray.setIcon(self.icon)

#------------------------------------------------

    def keyPressEvent(self, event):
        k = event.key()
        m = event.modifiers()

        plot_type = ''

        if k == QtCore.Qt.Key_Space:
            self.image.fill(QtCore.Qt.black)
            self.X = [0, 0]
        elif k == QtCore.Qt.Key_Escape:
            self.toggleWindow(None)

        elif k == QtCore.Qt.Key_1:
            if params['channels'] != [1]: self.switch_channel([1])
        elif k == QtCore.Qt.Key_2:
            if params['channels'] != [2] or type(params['channels'][0]) == float: self.switch_channel([2])
        elif k == QtCore.Qt.Key_3:
            if params['channels'] != [1,2]: self.switch_channel([1,2])
        elif k == QtCore.Qt.Key_4:
            if params['channels'] != [2,1]: self.switch_channel([2,1])
        elif k == QtCore.Qt.Key_Slash:
            if params['channels'] != [2/1]  or type(params['channels'][0]) == int: self.switch_channel([2/1])
        elif k == QtCore.Qt.Key_Asterisk:
            if params['channels'] != [1/2]: self.switch_channel([1/2])

        elif k == QtCore.Qt.Key_P:
            plot_type = ['P1','P2'][bool(m)]
        elif k == QtCore.Qt.Key_N:
            plot_type = 'PN'
        elif k == QtCore.Qt.Key_X:
            plot_type = ['X1','X2'][bool(m)]
        elif k == QtCore.Qt.Key_H:
            plot_type = ['H1','H2'][bool(m)]
        elif k == QtCore.Qt.Key_L:
            plot_type = ['L1','L2'][bool(m)]
        elif k == QtCore.Qt.Key_C:
            plot_type = ['C1','C2'][bool(m)]
        elif k == QtCore.Qt.Key_D:
            plot_type = ['D1','D2'][bool(m)]
        elif k == QtCore.Qt.Key_J:
            plot_type = ['HL1','HL2'][bool(m)]
        elif k == QtCore.Qt.Key_F:
            plot_type = ['F1','F2'][bool(m)]

        if plot_type and params['log']:
            self.log_file.flush()
            subprocess.Popen(["pythonw.exe", "res/pylab_plot.py", self.log_file.name, plot_type])


#------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            self.setWindowTitle("EasyLogger")

        if event.button() == QtCore.Qt.RightButton:
            image = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_ARGB32)
            self.render(image)

            t = time.time()
            ft = "{0}-{1:02d}-{2:02d}--{3:02d}-{4:02d}-{9:06.3f}".format(*(time.localtime(t)+(t%60,)))

            if self.XY_mode:
                channels = ["[1X][2Y]", "[1Y][2X]"][params['channels'][0]<1]
                resolutions = "[" + str(params['refresh_ms']) + "ms]"
            else:
                channels = ''
                resolutions = ''
                for c in params['channels']:
                    channels += "[" + str(c) + "]"
                    resolutions += "[" + str([channel_1['vline_s'], channel_2['vline_s']][c-1]) + "s]"

            filename = "%s-%s-%s.png" % (ft, channels, resolutions)

            image.save('img/' + filename)
            self.setWindowTitle("Image %s saved" % filename)

#------------------------------------------------

    def switch_channel(self, ch=None):
        if not ch:
            next_ch = self.channels_queue[0]
            self.channels_queue = self.channels_queue[1:] + [self.channels_queue[0]]
        else:
            next_ch = ch

        params['channels'] = next_ch

        if type(params['channels'][0]) == float:
            self.XY_mode = True
            channels = ["[1X][2Y]", "[1Y][2X]"][params['channels'][0]<1]
        else:
            self.XY_mode = False
            channels = "".join(["[%i]"%c for c in params['channels']])

        self.setWindowTitle("Channels: " + channels)

        self.X = [0, 0]
        self.XY_pre = None

        self.resizeEvent(None)
        self.update()

#------------------------------------------------

    def mouseDoubleClickEvent (self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.switch_channel()

#------------------------------------------------

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)

#------------------------------------------------

    def set_latency(self):
        sps = 1000
        b = params['read_samples']
        i = params['refresh_ms'] / 1000
        p1 = channel_1['latest_n']
        o1 = channel_1['draw_by']
        p2 = channel_2['latest_n']
        o2 = channel_2['draw_by']

        delta1 = b * i / (p1 * o1) - b/sps
        delta2 = b * i / (p2 * o2) - b/sps

        lat = min(delta1, delta2)
        if lat < 0:
            lat = 0
        self.lat = lat

        self.p.sleep.value = self.lat
        self.max_len = [ round(self.lat*p1*o1 / i) + 1, round(self.lat*p2*o2 / i) + 1 ]

#------------------------------------------------

    def wheelEvent(self, event):
        k = [0.5,2][event.delta() < 0]
        if 5 <= int(params['refresh_ms'] * k) <= 10*1000:
            params['refresh_ms'] = params['refresh_ms'] * k
            self.set_latency()
            self.timer.setInterval(params['refresh_ms'])

            if 1000//params['refresh_ms']:
                self.setWindowTitle("Refrash rate: " + str(1000/params['refresh_ms']) + " Hz")
            else:
                self.setWindowTitle("Refrash interval: " + str(params['refresh_ms']/1000) + " s")

#------------------------------------------------

    def closeEvent(self, event):
        mb = QtGui.QMessageBox()
        mb.setWindowTitle("EasyLogger")
        mb.setWindowIcon(self.icon)
        mb.setText("Exit?")
        mb.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        hide_button = mb.addButton("Hide to tray", QtGui.QMessageBox.ActionRole)

        if mb.exec_() == QtGui.QMessageBox.Yes:
            self.timer.stop()
            self.p.stop()
            if params['log']:
                self.log_file.close()

        elif mb.clickedButton() == hide_button:
            self.toggleWindow(None)
            event.ignore()
        else:
            event.ignore()


#################################################
