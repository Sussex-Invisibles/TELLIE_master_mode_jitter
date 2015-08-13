from core import serial_command
import os
import sys
import optparse
import time
import sweep
import scopes
import scope_connections
import utils

def save_scopeTraces(fileName, scope, channel, noTraces):
    """Save a number of scope traces to file - uses compressed .pkl"""
    scope._get_preamble(channel)
    results = utils.PickleFile(fileName, 1)
    results.add_meta_data("timeform_1", scope.get_timeform(channel))

    t_start, loopStart = time.time(),time.time()
    for i in range(noTraces):
        try:
            results.add_data(scope.get_waveform(channel), 1)
    	except Exception as e:
            print "Scope died, acquisition lost."
            print e
    	if i % 100 == 0 and i > 0:
            print "%d traces collected - This loop took : %1.1f s" % (i, time.time()-loopStart)
            loopStart = time.time()
    print "%d traces collected TOTAL - took : %1.1f s" % (i, (time.time()-t_start))
    results.save()
    results.close()

def check_dir(dname):
    """Check if directory exists, create it if it doesn't"""
    direc = os.path.dirname(dname)
    try:
        os.stat(direc)
    except:
        os.mkdir(direc)
        print "Made directory %s...." % dname
    return dname

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b",dest="box",help="Box number (1-12)")
    parser.add_option("-c",dest="channel",help="Channel number (1-8)")
    parser.add_option("-d",dest="directory",help="Name of directory to save data into")
    (options,args) = parser.parse_args()

    check_dir(options.directory)

    #Time
    total_time = time.time()

    #Set passed TELLIE parameters
    box = int(options.box)
    channel = int(options.channel)
    #Fixed parameters
    delay = 0.1 # 1ms -> kHz

    #run the initial setup on the scope
    usb_conn = scope_connections.VisaUSB()
    scope = scopes.Tektronix3000(usb_conn)
    ###########################################
    scope_chan = 1 # We're using channel 1!
    termination = 50 # Ohms
    trigger_level = 0.5 # half peak minimum
    falling_edge = True
    min_trigger = -0.004
    y_div_units = 1 # volts
    x_div_units = 200e-6 # seconds

    #y_offset = -2.5*y_div_units # offset in y (2.5 divisions up)
    y_offset = 0
    x_offset = 0
    record_length = 5e6 # trace is 1e3 samples long
    half_length = record_length / 2 # For selecting region about trigger point
    ###########################################
    scope.unlock()
    scope.set_horizontal_scale(x_div_units)
    scope.set_horizontal_delay(x_offset) #shift to the left 2 units
    scope.set_channel_y(scope_chan, y_div_units, pos=2.5)
    #scope.set_display_y(scope_chan, y_div_units, offset=y_offset)
    scope.set_channel_termination(scope_chan, termination)
    scope.set_single_acquisition() # Single signal acquisition mode
    scope.set_record_length(record_length)
    scope.set_data_mode(0, record_length)
    scope.lock()
    scope.begin() # Acquires the pre-amble!

    # TELLIE stuff
    sc = serial_command.SerialCommand("/dev/tty.usbserial-FTE3C0PG")
    #fixed options
    width = 0
    height = 16383
    fibre_delay = 0
    trigger_delay = 0
    pulse_number = 100
    #first select the correct channel and provide settings
    logical_channel = (box-1)*8 + channel

    sc.select_channel(logical_channel)
    sc.set_pulse_width(width)
    sc.set_pulse_height(16383)
    sc.set_pulse_number(pulse_number)
    sc.set_pulse_delay(delay)
    sc.set_fibre_delay(fibre_delay)
    sc.set_trigger_delay(trigger_delay)
    sc.fire_continuous()
    time.sleep(1)

    for i in range(50):
        save_scopeTraces("%s/file_%i"%(options.directory, i), scope, 1, 10)
