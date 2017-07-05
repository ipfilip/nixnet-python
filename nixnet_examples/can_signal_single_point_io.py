from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import pprint
import six
import sys
import time

from nixnet import constants
from nixnet import nx


pp = pprint.PrettyPrinter(indent=4)


def main():
    database_name = 'NIXNET_example'
    cluster_name = 'CAN_Cluster'
    input_signal_list = 'CANEventSignal1,CANEventSignal2'
    output_signal_list = 'CANEventSignal1,CANEventSignal2'
    interface1 = 'CAN1'
    interface2 = 'CAN2'
    input_mode = constants.CreateSessionMode.SIGNAL_IN_SINGLE_POINT
    output_mode = constants.CreateSessionMode.SIGNAL_OUT_SINGLE_POINT

    with nx.Session(database_name, cluster_name, input_signal_list, interface1, input_mode) as input_session:
        with nx.Session(database_name, cluster_name, output_signal_list, interface2, output_mode) as output_session:
            print('Are you using a terminated cable? Enter Y or N')
            terminated_cable = six.moves.input()
            if terminated_cable.lower() == "y":
                output_session.intf_can_term = constants.CanTerm.OFF
                input_session.intf_can_term = constants.CanTerm.ON
            elif terminated_cable.lower() == "n":
                input_session.intf_can_term = constants.CanTerm.ON
                output_session.intf_can_term = constants.CanTerm.ON
            else:
                print("Unrecognised input ({}), assuming 'n'".format(terminated_cable))
                input_session.intf_can_term = constants.CanTerm.ON
                output_session.intf_can_term = constants.CanTerm.ON

            # Start the input session manually to make sure that the first
            # signal value sent before the initial read will be received.
            input_session.start(constants.StartStopScope.NORMAL)

            user_value = six.moves.input('Enter two signal values [float, float]: ')
            try:
                value_buffer = [float(x.strip()) for x in user_value.split(",")]
            except ValueError:
                value_buffer = [24.5343, 77.0129]
                print('Unrecognized input ({}). Setting data buffer to {}', user_value, value_buffer)

            if len(value_buffer) != 2:
                value_buffer = [24.5343, 77.0129]
                print('Invalid number of signal values entered. Setting data buffer to {}', value_buffer)

            epoch = time.gmtime(0)
            delta = datetime.datetime(epoch.tm_year, epoch.tm_mon, epoch.tm_mday) - datetime.datetime(1601, 1, 1)

            print('The same values should be received. Press q to quit')
            i = 0
            while True:
                for index, value in enumerate(value_buffer):
                    value_buffer[index] = value + i
                output_session.write_signal_single_point(value_buffer)
                print('Sent signal values: %s' % value_buffer)

                # Wait 1 s and then read the received values.
                # They should be the same as the ones sent.
                time.sleep(1)

                num_signals = len(value_buffer)
                signals = input_session.read_signal_single_point(num_signals)
                for timestamp, value in signals:
                    date = datetime.datetime.fromtimestamp(timestamp / 1e9) + delta
                    print('Received signal with timepstamp %s and value %s' % (date, value))

                i += 1
                if max(value_buffer) + i > sys.float_info.max:
                    i = 0

                inp = six.moves.input()
                if inp == 'q':
                    break

            print('Data acquisition stopped.')


if __name__ == '__main__':
    main()
