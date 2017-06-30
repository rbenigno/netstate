#!/usr/bin/env python

from cdp_gather import *
import pprint
import sys

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

# Main function (when running as an executable)
if __name__ == '__main__':
    cdpfile = sys.argv[1]

    with open(cdpfile, 'r') as f:
        filename = f.name
        read_data = f.read()

    cdp_data = parse_cdp_neighbors(read_data)

    print_cdp_csv(cdp_data, filename)
