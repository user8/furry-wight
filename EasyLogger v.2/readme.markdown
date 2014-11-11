
![](res/icon.png) EasyLogger
============================

**EasyLogger** displays and records data from a microcontroller,
with *dual-channel* version of the [EasyLogger](http://www.obdev.at/products/vusb/easylogger.html) firmware.
Dual-channel version of the firmware was developed by *Yves Lebrac* and published
in [his blog](http://yveslebrac.blogspot.ru/2008/10/cheapest-dual-trace-scope-in-galaxy.html)
back in 2008. A little more information is available at the
[Code and Life](http://codeandlife.com/2012/02/22/v-usb-with-attiny45-attiny85-without-a-crystal/).
The firmware uses the [V-USB](http://www.obdev.at/products/vusb/index.html) library.

Files:

    File to start the program:      EasyLogger.pyw
    Settings file:                  config.py
    Dependencies:                   Windows, Python 3, PyQt4, PyLab (optional)

Folders:

    img/                            folder for the images to be saved
    log/                            folder for recording data (.log)
    res/                            program resources (necessary modules)
    __pycache __/                   Python bytecode

Settings are described in the settings file.

Program info
============

Maximum resolution — about 1000 samples per second.

Mouse and buttons
-----------------

    Single click                - drag the window
    Double click                - channel switching [1,2], [1], [2], [2/1]
    Right click                 - save a picture to the img/ folder
    Wheel                       - change speed of data acquisition and update window
                                  (the change occurs at the end of a current phase,
                                  so it is necessary to wait long delays sometimes)

    Escape                      - hide program to tray
    Space                       - clear window
    1                           - show first channel
    2                           - show second channel
    3                           - [1,2] channels
    4                           - [2,1] channels
    /                           - XY-mode, first channel - X, second - Y
    *                           - XY-mode, first channel - Y, second - X

Files
-----

Names of images to be stored have the format:

    YYYY-MM-DM--HH-mm-ss.mss-[C]-[CR].png

        - .mss  - milliseconds,
        - [C]   - a list of channels displayed while saving, top to bottom,
        - [CR]  - resolution of channels (time between the vertical lines or dots)

Names of `.log`-files are about the same. Averaged by `avg_by` measurements data is written into a file in the foramt of:

    time in seconds <TAB> value of 1st channel <TAB> value of 2nd channel

Misc
----

The settings are edited in a text editor such as **Notepad++**.
By double-clicking the `config.py`, ordinary notepad opens with the file itself.

After changing the settings, you need to restart the program.

You can run multiple instances of the program at the same time.

There is a script `res/pylab_plot.py`, which plots graphs using data from `.log`-file.
Several keys were assigned to run the script with different parameters:

    P           - channel 1 time plot
    Shift + P   - channel 2 time plot
    N           - channels 1 and 2, reduced to one

    X           - channel 1 - as Y, channel 2 - as X
    Shift + X   - channel 2 - as Y, channel 1 - as X

    H           - histogram of distribution of channel 1
    Shift + H   - histogram of distribution of channel 2

    L           - regression channel 1(channel 2)
    Shift + L   - regression channel 2(channel 1)

    C           - channel 1 and channel 1 as regression of channel 2
    Shift + C   - channel 2 and channel 2 as regression of channel 1

    D           - channel 1 without channel 1(Channel 2)
    Shift + D   - channel 2 without channel 2(channel 1)

    J           - histogram of channel 1 across the regression line
    Shift + J   - histogram of channel 2 across the regression line

    F           - spectrum of channel 1 (DFT)
    Shift + F   - spectrum of channel 2 (DFT)

The `pylab_plot.py` script works only with **PyLab** python library installed.
*It is = NumPy + Matplotlib + six + dateutil + pyparsing. So, everything is difficult,
especially when you're on 64-bit version of Python.*

In the theory
=============

Data packets are read from the controller by `N` values per iteration.
Speed of obtaining the packets — `1000/N` per second. The packets then
put into the buffer, so that all obtained data is available simultaneously.

The graph is drawn by stripes (or dots) one pixel wide. The height of a stripe
is proportional to the current value. The value is calculated as the average
of `k` samples. So that at one moment the buffer contains `L/k` *stripes*,
wherein `L` is the total amount of untreated data.

You can render all `L/k` stripes or only the latest `n`. If there is too much
data in the buffer and not enough time to redraw it, then a part of the data is removed.

Settings `N`, `k` and `n` are called `read_samples`, `draw_by` and `latest_n` respectively.
And, like, used for changing the quantity and quality of data rendered on a broad range.

For example, you can read 100 samples instantly at the end of a minute ​​and then display them as one point,
or you can read 100 samples periodically during one minute and then display them as a one point.

---
