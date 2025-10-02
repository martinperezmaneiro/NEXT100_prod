"""
This script takes the txt output of a nexus simulation with NextFlex geometry, where the following 
parameters need to be set to true:

/Geometry/NextFlex/ep_with_PMTs       true
/Geometry/NextFlex/ep_verbosity       true
/Geometry/NextFlex/tp_sipm_verbosity  true

And converts that output into a simpler txt file with just the PMT and SiPM positions, in a format
that can be used to create a DataBase.
"""

import re

in_file  = '/path/to/nexus/text/output.txt'
out_file = '/path/to/save/pmt_sipm_positions.txt'

def get_pmt_sipm_positions(input_file_path, output_file_path):
    # Define patterns to capture both PMT and TP_SiPM positions
    pmt_pattern = r'\* PMT (\d+) position: \(([-\d.eE+]+),([-\d.eE+]+),([-\d.eE+]+)\)'
    sipm_pattern = r'\* TP_SiPM (\d+) position: \(([-\d.eE+]+),([-\d.eE+]+),([-\d.eE+]+)\)'
    
    # List to store the transformed text lines
    transformed_lines = []
    found_sipm = False
    
    # Open the input file and read it line by line
    with open(input_file_path, 'r') as file:
        for line in file:
            # Check if the line matches the PMT pattern
            pmt_match = re.search(pmt_pattern, line)
            if pmt_match:
                pmt_number = pmt_match.group(1)
                x = pmt_match.group(2)
                y = pmt_match.group(3)
                z = pmt_match.group(4)
                transformed_line = f'PMT {pmt_number} ({x},{y},{z})'
                transformed_lines.append(transformed_line)
                continue  # Move to the next line after matching
            
            # Check if the line matches the TP_SiPM pattern
            sipm_match = re.search(sipm_pattern, line)
            if sipm_match:
                if not found_sipm:
                    transformed_lines.append('')
                    found_sipm = True
                sipm_number = sipm_match.group(1)
                x = sipm_match.group(2)
                y = sipm_match.group(3)
                z = sipm_match.group(4)
                transformed_line = f'TP_SiPM {sipm_number} ({x},{y},{z})'
                transformed_lines.append(transformed_line)
    
    # # Write the transformed text to the output file
    with open(output_file_path, 'w') as output_file:
        # Join the transformed lines with newlines and write to the file
        output_file.write('\n'.join(transformed_lines))

get_pmt_sipm_positions(in_file, out_file)