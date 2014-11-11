#################################################

# Data gathering process

#################################################

import multiprocessing as mp
import res.myusb.myusb as usb
import time

class GetDataProcess(mp.Process):
    def __init__(self, buff=50, qd=5, sleep=0):
        mp.Process.__init__(self)
        self.buff = buff
        self.Q = mp.Queue()
        self.sleep = mp.Value('d', sleep)

    def stop(self):
        # there is no function for disconnect
        self.terminate()
        print("Bye!")

    def run(self):
        device = usb.HIDInputDevice(vid="4242", pid="0002")

        if device.open():
            while "John" is not "dead":
                data = [[], []]

                for j in range(self.buff):
                    raw_data = device.read()
                    c1_val = (raw_data[3]*256+raw_data[4]) / 2557
                    c2_val = (raw_data[1]*256+raw_data[2]) / 2557

                    data[0].append(c1_val)
                    data[1].append(c2_val)

                self.Q.put(data)

                if self.sleep.value > 0:
                    time.sleep(self.sleep.value)


#################################################
