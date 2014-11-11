import sys, os

def help(message=""):
    """
    This script shows a PyLab plot of a data from a file.

    Usage:
        pylab_plot.py <datafile> <plot type>


    Datafile is a text file which has three records per each line:
        <record time in seconds> <channel 1 data> <channel 2 data>

    Records are delimited by whitespace character.


    Plot type is one of the following:
        P1  - channel 1 time plot
        P2  - channel 2 time plot
        PN  - normalized channels 1 and 2 time plot

        X1  - channel 1 (y) vs channel 2 (x)
        X2  - channel 2 (y) vs channel 1 (x)

        H1  - channel 1 histogram
        H2  - channel 2 histogram

        L1  - channel 1 as linear function of channel 2
        L2  - channel 2 as linear function of channel 1

        C1  - channel 1 and channel 1 as f(channel 2) time plot
        C2  - channel 2 and channel 2 as f(channel 1) time plot

        D1  - channel 1 minus f(channel 2) time plot, detrand
        D2  - channel 2 minus f(channel 1) time plot, detrand

        HL1 - channel 1 across f(channel 2) histogram
        HL2 - channel 2 across f(channel 1) histogram

        F1  - FFT for channel 1
        F2  - FFT for channel 2

    """

    if message:
        sys.stderr.write('\n!!! ' + message + ' !!!\n')

    print(help.__doc__)


if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
    help("No file specified or it doesn't exist")
    sys.exit(-1)

try:
    import pylab as pl
    t, c1, c2 = pl.genfromtxt(sys.argv[1]).T
except:
    help("Wrong file structure or there's no PyLab module installed")
    sys.exit(-2)

t = (t-min(t)) / 60     # time in munutes
points = str(len(t)) + " points"

if len(sys.argv) > 2:
    sys.argv[2] = sys.argv[2].upper()
    if sys.argv[2] == '':
        pass
    elif sys.argv[2] == 'P1':
        pl.plot(t, c1)
        pl.xlabel("Time, min")
        pl.title("Channel 1 time plot, " + points)
    elif sys.argv[2] == 'P2':
        pl.plot(t, c2)
        pl.xlabel("Time, min")
        pl.title("Channel 2 time plot, " + points)
    elif sys.argv[2] == 'PN':
        c1n = (c1-c1.min()) / c1.ptp()
        c2n = (c2-c2.min()) / c2.ptp()
        pl.plot(t, c1n, t, c2n)
        pl.xlabel("Time, min")
        pl.legend(["Channel 1", "Channel 2"])
        pl.title("Time plot, " + points)

    elif sys.argv[2] == 'X1':
        pl.hexbin(c2, c1, gridsize=200, bins='log', cmap=pl.cm.Greys, zorder=0)    # pl.cm.bone, pl.cm.Greys, pl.cm.hot
        pl.xlabel("Channel 2")
        pl.ylabel("Channel 1")
        pl.title("Channel 1 vs Channel 2, " + points)
    elif sys.argv[2] == 'X2':
        pl.hexbin(c1, c2, gridsize=200, bins='log', cmap=pl.cm.Greys, zorder=0)
        pl.xlabel("Channel 1")
        pl.ylabel("Channel 2")
        pl.title("Channel 2 vs Channel 1, " + points)

    elif sys.argv[2] == 'H1':
        pl.hist(c1, 100)
        pl.title("Channel 1 distribution, " + points)
    elif sys.argv[2] == 'H2':
        pl.hist(c2, 100)
        pl.title("Channel 2 distribution, " + points)

    elif sys.argv[2] == 'L1':
        f = pl.poly1d(pl.polyfit(c2,c1,1))
        pl.plot(c2, c1, 'x')
        pl.plot(c2, f(c2))
        pl.xlabel("Channel 2 (x)")
        pl.ylabel("Channel 1 (y)")
        pl.title( ("y = %f * x + %f" % tuple(f.coeffs)) + ("  (%s)" % points) )
    elif sys.argv[2] == 'L2':
        f = pl.poly1d(pl.polyfit(c1,c2,1))
        pl.plot(c1, c2, 'x')
        pl.plot(c1, f(c1))
        pl.xlabel("Channel 1 (x)")
        pl.ylabel("Channel 2 (y)")
        pl.title( ("y = %f * x + %f" % tuple(f.coeffs)) + ("  (%s)" % points) )

    elif sys.argv[2] == 'C1':
        f = pl.poly1d(pl.polyfit(c2,c1,1))
        pl.plot(t, f(c2))
        pl.plot(t, c1, zorder=0)
        pl.xlabel("Time, min")
        pl.legend(["f(Channel 2)", "Channel 1"])
        pl.title("Channel 1 as f(Channel 2), " + points)
    elif sys.argv[2] == 'C2':
        f = pl.poly1d(pl.polyfit(c1,c2,1))
        pl.plot(t, f(c1))
        pl.plot(t, c2, zorder=0)
        pl.xlabel("Time, min")
        pl.legend(["f(Channel 1)", "Channel 2"])
        pl.title("Channel 2 as f(Channel 1), " + points)

    elif sys.argv[2] == 'D1':
        f = pl.poly1d(pl.polyfit(c2,c1,1))
        pl.plot(t, c1-f(c2))
        pl.xlabel("Time, min")
        pl.title("Channel 1 minus f(Channel 2), " + points)
    elif sys.argv[2] == 'D2':
        f = pl.poly1d(pl.polyfit(c1,c2,1))
        pl.plot(t, c2-f(c1))
        pl.xlabel("Time, min")
        pl.title("Channel 2 minus f(Channel 1), " + points)

    elif sys.argv[2] == 'HL1':
        c1 = (c1-c1.mean()) / c1.ptp()
        c2 = (c2-c2.mean()) / c1.ptp()
        f = pl.poly1d(pl.polyfit(c2,c1,1))
        a = pl.arctan(f.coeffs[0]) + pl.pi
        tm = pl.matrix([[pl.cos(a), -pl.sin(a)], [pl.sin(a), pl.cos(a)]])
        along, across = pl.array([c2,c1]).T.dot(tm).T.getA()
        pl.hist(across, 100)
        pl.title("Channel 1 across f(Channel 2), " + points)
    elif sys.argv[2] == 'HL2':
        c1 = (c1-c1.mean()) / c1.ptp()
        c2 = (c2-c2.mean()) / c1.ptp()
        f = pl.poly1d(pl.polyfit(c1,c2,1))
        a = pl.arctan(f.coeffs[0]) + pl.pi
        tm = pl.matrix([[pl.cos(a), -pl.sin(a)], [pl.sin(a), pl.cos(a)]])
        along, across = pl.array([c1,c2]).T.dot(tm).T.getA()
        pl.hist(across, 100)
        pl.title("Channel 2 across f(Channel 1), " + points)

    elif sys.argv[2] == 'F1':
        ft = pl.log10(abs(pl.fft(c1)))
        ff = pl.fftfreq(c1.size, max(t)/len(t))
        n = c1.size // 2
        pl.plot(ff[:n], ft[:n])
#         pl.xscale('log')
        pl.xlabel("Frequency, 1/min")
        pl.ylabel("log10(amplitude)")
        pl.title("Channel 1 spectrum, " + points)
    elif sys.argv[2] == 'F2':
        ft = pl.log10(abs(pl.fft(c2)))
        ff = pl.fftfreq(c2.size, max(t)/len(t))
        n = c2.size // 2
        pl.plot(ff[:n], ft[:n])
#         pl.xscale('log')
        pl.xlabel("Frequency, 1/min")
        pl.ylabel("log10(amplitude)")
        pl.title("Channel 2 spectrum, " + points)
    else:
        help("Wrong plot type argument")
        sys.exit(-3)

    pl.tight_layout()
    pl.show()

else:
    help("Specify plot type argument")
    sys.exit(-4)
