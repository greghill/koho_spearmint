#!/usr/bin/env python

import re
import sys
from subprocess import call

emulators = [
(       '2017-01-04T07-24-AWS-Brazil-1-to-Brazil-10-runs',  '97.11',   '1',  '366',     '0',     '0'),
(           '2017-01-02T03-54-India-to-AWS-India-10-runs', '117.65',  '13',  '144',     '0',     '0'),
(      '2016-12-30T21-38-China-ppp0-to-AWS-Korea-10-runs',   '6.25', '152',  '362', '.0025',     '0'),
('2016-12-30T22-50-AWS-Brazil-2-to-Colombia-ppp0-10-runs',   '5.65',  '88', '3665', '.0026', '.0001'),
(           '2017-01-03T21-30-Nepal-to-AWS-India-10-runs',  '13.38',  '32',   '37',  '.003',     '0')
]

def koho_func(up_delay_threshold, up_delay_window_delta, down_delay_threshold, down_delay_window_delta, loss_window_delta):
    thresholds_valid = float(down_delay_threshold - up_delay_threshold)
    if thresholds_valid < 0.:
        return {"score" : 999, "thresholds_valid" : thresholds_valid}

    #for run_id in range(1, len(emulators) + 1):
    schemes = ["new_koho", "default_tcp", "vegas", "ledbat", "pcc", "verus", "scream", "sprout", "koho_cc"]
    for emulator in emulators:
        for scheme in schemes:
            #emulator = emulators[run_id - 1]
            emulator = emulators[0]
            trace_dir = '../travis_extras/calibrated_emulators/%s/%smbps.trace' % (emulator[0], emulator[1])
            extra_sender_args = '%f %f %f %f %f' % (up_delay_threshold, up_delay_window_delta, down_delay_threshold, down_delay_window_delta, loss_window_delta)
            cmd = '../pantheon/test/test.py --uplink-trace %s --downlink-trace %s --prepend-mm-cmds "mm-delay %s mm-loss uplink %s mm-loss downlink %s" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=%s" %s' % (trace_dir, trace_dir, emulator[2], emulator[4], emulator[5], emulator[3], scheme)
            if scheme is "new_koho":
                cmd += ' --extra-sender-args "%s"' % extra_sender_args

            print cmd
            call(cmd, shell=True)
        cmd = '../pantheon/analyze/analyze.py --data-dir ../pantheon/test/'
        call(cmd, shell=True)
        cmd = 'mv ../pantheon/test/pantheon_report.pdf ../pantheon/test/pantheon_report_%s.pdf' % emulator[0]
        call(cmd, shell=True)

if __name__ == '__main__':
    koho_func(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
