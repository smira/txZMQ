from optparse import OptionParser


def getOptionsAndArgs():
    parser = OptionParser("")
    parser.add_option(
        "-m", "--method", dest="method",
        help="0MQ socket connection: bind|connect")
    parser.add_option(
        "-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
    parser.add_option(
        "-M", "--mode", dest="mode", help="Mode: publisher|subscriber")
    parser.set_defaults(
        method="connect", endpoint="epgm://eth1;239.0.5.3:10011")
    return parser.parse_args()
