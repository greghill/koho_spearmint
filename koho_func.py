import re
from subprocess import (Popen, call, check_output, STDOUT)

emulators = [





(       '2017-01-04T07-24-AWS-Brazil-1-to-Brazil-10-runs/',  '97.11',   '1',  '366',     '0',     '0'),
(           '2017-01-02T03-54-India-to-AWS-India-10-runs/', '117.65',  '13',  '144',     '0',     '0'),
(      '2016-12-30T21-38-China-ppp0-to-AWS-Korea-10-runs/',   '6.25', '152',  '362', '.0025',     '0'),
('2016-12-30T22-50-AWS-Brazil-2-to-Colombia-ppp0-10-runs/',   '5.65',  '88', '3665', '.0026', '.0001'),
(           '2017-01-03T21-30-Nepal-to-AWS-India-10-runs/',  '13.38',  '32',   '37',  '.003',     '0')
]

def koho_func(delay_window_delta, delay_threshold, loss_window_delta):
    result = 0.0
    for run_id in range(1, len(emulators)):
        emulator = emulators[run_id - 1]
        trace_dir = '../travis_extras/calibrated_emulators/%s%smbps.trace' % (emulator[0], emulator[1])
        extra_sender_args = '%f %f %f' % (delay_window_delta, delay_threshold, loss_window_delta)
        cmd = '../pantheon/test/test.py --uplink-trace %s --downlink-trace %s --prepend-mm-cmds "mm-delay %s mm-loss uplink %s mm-loss downlink %s" --extra-mm-link-args "--uplink-queue=droptail --uplink-queue-args=packets=%s" --extra-sender-args "%s" --run-id %d -t 10 new_koho' % (trace_dir, trace_dir, emulator[2], emulator[4], emulator[5], emulator[3], extra_sender_args, run_id)
        print cmd
        call(cmd, shell=True)
        log_path = '../pantheon/test/new_koho_datalink_run%d.log' % run_id
        cmd = '../pantheon/analyze/tunnel_graph.py 500 %s' % log_path
        print cmd
        output = check_output(cmd, shell=True, stderr=STDOUT)
        output_lines = output.split('\n')
        print output_lines[2]
        throughput_match = re.match('Average throughput: (\d+\.\d+) Mbit/s', output_lines[2])
        assert(throughput_match)
        print throughput_match.group(1)
        print output_lines[3]
        delay_match = re.match('95th percentile per-packet one-way delay: (\d+\.\d+) ms', output_lines[3])
        assert(delay_match)
        print delay_match.group(1)
        power_score = (float(throughput_match.group(1))*1000.)/ float(delay_match.group(1))
        print "power score = %f" % power_score
        power_score = (float(throughput_match.group(1))/float(emulator[1]))/ (float(delay_match.group(1)) / float(emulator[2]))
        print "semi-normalized power score = %f" % power_score
        result += power_score

    print 'Result = %f' % result
    #time.sleep(np.random.randint(60))
    return result

# Write a function like this called 'main'
def main(job_id, params):
    print 'Anything printed here will end up in the output directory for job #%d' % job_id
    print params
    return koho_func(params['delay_window_delta'], params['delay_threshold'], params['loss_window_delta'])

if __name__ == '__main__':
    koho_func(.2, 12., 1.2)
