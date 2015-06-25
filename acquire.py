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
            except Exception, e:
            print "Scope died, acquisition lost."
            print e
            if i % 100 == 0 and i > 0:
            print "%d traces collected - This loop took : %1.1f s" % (i, time.time()-loopStart)
            loopStart = time.time()
    print "%d traces collected TOTAL - took : %1.1f s" % (i, (time.time()-t_start))
    results.save()
    results.close()

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b",dest="box",help="Box number (1-12)")
    parser.add_option("-c",dest="channel",help="Channel number (1-8)")
    parser.add_option("-f",dest="file",help="Name of file to be produced")
    (options,args) = parser.parse_args()

    #Time
    total_time = time.time()

    #Set passed TELLIE parameters
    box = int(options.box)
    channel = int(options.channel)
    #Fixed parameters
    delay = 1.0 # 1ms -> kHz

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
    x_div_units = 0.1 # seconds

    #y_offset = -2.5*y_div_units # offset in y (2.5 divisions up)
    y_offset = 0
    x_offset = 0
    record_length = 1.25e6 # trace is 1e3 samples long
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
    #scope.set_data_mode(half_length-50, half_length+50)
    scope.lock()
    scope.begin() # Acquires the pre-amble!

    
    save_scopeTraces(options.file, scope, 1, 500)
