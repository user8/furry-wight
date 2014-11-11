#################################################

# Configuration file
# Restart the program after changing this file

#################################################


# MAIN PARAMETERS
params =    {
            'window_size':    (1024, 576),      # initial window size
            'channels':       [2],              # channels to show, [1], [2], [1,2] or [2,1]; [2/1] or [1/2] for XY-mode
            'refresh_ms':     1000,             # refresh interval, milliseconds
            'grid_values':    True,             # show grid values, True or False
            'tray_icon_draw': False,            # refresh icon in the system tray when window is hidden, True or False
            'log':            True,             # record data to .log file, (data averaged by 'avg_by' samples will be recorded)
            'read_samples':   50,               # samples read from device per interval
            }

# CHANNELS PARAMETERS
channel_1 = {
            'function':       lambda x: x,      # x conversion function; 0<=x<=1
            'f_range':        [0.8, 0.6],       # function range to show
            'grids':          [1/10, 1/100],    # greed lines interval in function units
            'vline_s':        60.0,             # vertical grid line interval in seconds, 0 - without vertical lines

            'draw_by':        50,               # samples per one point
            'latest_n':       1,                # how many points will be drawn at once if there's enough data

            'color_rgb':      (255,0,128),      # channel color (R, G, B)
            'dots':           False,            # draw dots (True) instead of lines (False)

            'text_val':       True,             # show data averaged by 'avg_by' samples as text
            'avg_by':         300,              # samples for averaging data
            'digits':         6,                # number of fractional digits in the text value
            'text_before':    '10K: ',          # text before value ('' or "" - without preceding text)
            'text_after':     '',               # text after value ('' or "" - without subsequent text)

            'draw_avg':       False,            # draw graph from 'avg_by' data instead of 'draw_by'
            }

channel_2 = {
            'function':       lambda x: (x * 2.2792049120597655 + 0.0154873618) * 100,  # x conversion function; 0<=x<=1
            'f_range':        [20, 30],         # function range to show
            'grids':          [1, 0.5],         # greed lines interval in function units
            'vline_s':        60.0,             # vertical grid line interval in seconds, 0 - without vertical lines

            'draw_by':        10,               # samples per one point
            'latest_n':       1,                # how many points will be drawn at once if there's enough data

            'color_rgb':      (0,220,255),      # channel color (R, G, B)
            'dots':           False,            # draw dots (True) instead of lines (False)

            'text_val':       True,             # show data averaged by 'avg_by' samples as text
            'avg_by':         300,              # samples for averaging data
            'digits':         2,                # number of fractional digits in the text value
            'text_before':    'LM35: ',         # text before value ('' or "" - without preceding text)
            'text_after':     ' °C',            # text after value ('' or "" - without subsequent text)

            'draw_avg':       True,             # draw graph from 'avg_by' data instead of 'draw_by'
            }


#################################################


if __name__ == "__main__":
    import os, sys
    os.execvp("notepad.exe", [' ',sys.argv[0]])


#################################################
