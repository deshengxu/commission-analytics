#!/usr/bin/env python

# ...

import os
import sys
import csv
import pandas as pd

sys.path.append(".")

try:
    from . import folder_validator
    from . import booking_validator
except:
    import folder_validator
    import booking_validator


def refine_booking(booking_files, current_year, current_quarter):
    '''
    clean up booking file and export data to file with name like: Refined-FY16Q2-Booking.csv
    during refine, following actions will be taken:
        1) Whitespace will be moved from all field
        2) except header row and name column, all field will be replaced with 0.0 if it is not a real number.
    :param booking_files: current booking file list to be refined
    :param current_year: current fiscal year
    :param current_quarter: current fiscal quarer
    :return: validate_status, refined booking file list.
    '''

    refined_booking_list = []
    success = False

    for booking_file in booking_files:
        success = False
        newfilename = os.path.join(os.path.dirname(booking_file), "Refined-" + os.path.basename(booking_file))
        cleanedfilename = os.path.join(os.path.dirname(booking_file), "Cleaned-" + os.path.basename(booking_file))

        # refined_booking_list.append(newfilename)

        with open(booking_file, "r") as oldfile, open(newfilename, "w") as newfile:
            oldcsv = csv.reader(oldfile)
            newcsv = csv.writer(newfile)

            first_line = True
            name_index = -1
            tmp_fy_str = 'FY%2d' % current_year
            tmp_q_str = 'Q%d' % current_quarter
            for rix, line in enumerate(oldcsv):
                if first_line:
                    header_list = []
                    for ix, cell in enumerate(line):
                        tmp_str = (cell.upper().replace(tmp_fy_str, "").replace(tmp_q_str, ""))
                        tmp_str = tmp_str.replace("?", "").strip()
                        if tmp_str == "NAME":
                            name_index = ix
                        else:
                            header_list.append(tmp_str)

                    newcsv.writerow(header_list)
                    first_line = False
                else:
                    # if rix==1:
                    #    print(line)
                    data_list = []

                    for ix, cell in enumerate(line):
                        # if rix==1:
                        #    print(cell)
                        tmp_str = ""
                        try:
                            if ix != name_index:
                                tmp_str = cell.strip().replace(",", "")
                                float(tmp_str)
                                data_list.append(tmp_str)
                        except:
                            tmp_str = r'0.0'
                            data_list.append(tmp_str)
                            # if rix==1:
                            #    print(cell + "\t-->"+ tmp_str)

                    newcsv.writerow(data_list)
            df = pd.read_csv(newfilename, index_col="EMPLOYEE NO")
            for col in df.columns:
                if 'TOTAL' in col:
                    del df[col]

            df.to_csv(cleanedfilename)
            refined_booking_list.append(cleanedfilename)
            success = True

    return success, refined_booking_list


def main():
    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"
    validated, current_year, current_quarter = folder_validator.validate_current_folder(test_str1)
    validated, filelists = booking_validator.validate_booking_files(test_str1, current_year, current_quarter)
    validated, refined_files = refine_booking(filelists, current_year, current_quarter)

    if validated:
        print(refined_files)
    else:
        print("Error Happened!")


if __name__ == "__main__":
    main()
