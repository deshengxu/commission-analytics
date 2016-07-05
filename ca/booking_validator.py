#!/usr/bin/env python

# ...

import os
import sys

sys.path.append(".")

try:
    from . import folder_validator
except:
    import folder_validator


def booking_validator(current_folder, current_year, current_quarter):
    '''

    :param current_folder: validated folder with name in pattern: FY16Q3 etc.
    :param current_year: validated fiscal year, which is between 16 and 99
    :param current_quarter: validated quarter, which is between 1 and 4
    :return: Validated_Status and Validated File List in full path.
    '''
    # from os import listdir
    # from os.path import isfile, join
    # onlyfiles = [f for f in listdir(current_folder) if isfile(join(current_folder, f))]

    validated_file_list = []
    if current_quarter == 1:
        return True, validated_file_list

    for i in range(current_quarter - 1):
        booking_file = os.path.join(current_folder, "FY%2dQ%1d-Booking.csv" % (current_year, (i + 1)))
        # print(booking_file)
        if os.path.isfile(booking_file) and os.path.exists(booking_file):
            validated_file_list.append(booking_file)
        else:
            return False, validated_file_list

    return True, validated_file_list


def main():
    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"
    validated, current_year, current_quarter = folder_validator.validate_current_folder(test_str1)
    validated, filelists = booking_validator(test_str1, current_year, current_quarter)

    if validated:
        print(filelists)
    else:
        print("nothing found!")


if __name__ == "__main__":
    main()
