"""NAPALM Cisco IOS Handler."""
# Copyright 2015 Spotify AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import re
# This is an extension of the napalm_ios driver
import napalm_ios

class IOSDriver(napalm_ios.IOSDriver):
    """Extension to NAPALM Cisco IOS Handler."""

    def get_cdp_neighbors(self):
        """IOS implementation of get_cdp_neighbors."""
        command = 'show cdp neighbors'
        output = self._send_command(command)

        # Check if router supports the command
        if '% Invalid input' in output:
            return {}

        cdp = {}

        # Process the output to obtain just the CDP entries
        try:
            split_output = re.split(r'^Device[ |-]ID.*$', output, flags=re.M)[1]
            split_output = re.split(r'^Total cdp entries displayed.*$', split_output, flags=re.M)[0]
        except IndexError:
            return {}

        split_output = split_output.strip()

        # Work through the CDP lines, treating lines starting with whitespace
        # as a continution of the previous line (long device ID)
        for cdp_entry in re.split("\n(?!\s+)", split_output):
            device_id = cdp_entry.split()[0]
            if len(cdp_entry.split('\n')) == 2:
                # Long named entry - device_id is first line
                tmp_field = cdp_entry.split('\n')[1].strip()
            else:
                # Single line entry - spilt at device_id
                tmp_field = cdp_entry.split(None,1)[1].strip()

            # First column is the local interface
            local_int_brief = tmp_field[:18].strip()
            local_port = self._expand_interface_name(local_int_brief)
            # Move to hold time (TODO: would regex be more reliable?)
            tmp_field = tmp_field[18:].strip()
            # Last column is remote port (not 100% reliable - CAT4507, for example)
            remote_port = tmp_field[33:].strip()

            entry = {'port': remote_port, 'hostname': device_id}
            cdp.setdefault(local_port, [])
            cdp[local_port].append(entry)

        return cdp