#!/usr/bin/env python

# ...

import os
import sys
import csv

sys.path.append(".")

try:
    from . import folder_validator
    from . import sfdc_validator
except:
    import folder_validator
    import sfdc_validator


def refine_sfdc(sfdc_files, current_year, current_quarter):
    '''
    clean up booking file and export data to file with name like: Refined-FY16Q2-SFDC.csv
    during refine, following actions will be taken:
        1) Whitespace will be moved from all field
        2) "ID" will be replaced with "Employee NO".
    :param booking_files: current booking file list to be refined
    :param current_year: current fiscal year
    :param current_quarter: current fiscal quarer
    :return: validate_status, refined booking file list.
    '''

    refined_sfdc_list = []
    success = False

    for sfdc_file in sfdc_files:
        success = False
        newfilename = os.path.join(os.path.dirname(sfdc_file), "Refined-" + os.path.basename(sfdc_file))
        refined_sfdc_list.append(newfilename)

        with open(sfdc_file, "r") as oldfile, open(newfilename, "w") as newfile:
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
                        tmp_str = (cell.upper().replace(tmp_fy_str, "").replace(tmp_q_str, "")).strip()
                        tmp_str = tmp_str.replace("?", "")
                        if tmp_str == "NAME":
                            name_index = ix
                        elif tmp_str == "ID":
                            tmp_str = "EMPLOYEE NO"
                            header_list.append(tmp_str)
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
                                if tmp_str == "-":
                                    tmp_str = "0.0"
                                float(tmp_str)
                                data_list.append(tmp_str)
                        except:
                            tmp_str = cell.strip()
                            data_list.append(tmp_str)
                        if rix == 1:
                            print(cell + "\t-->" + tmp_str)

                    newcsv.writerow(data_list)

            success = True

    return success, refined_sfdc_list


def main():
    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"
    validated, current_year, current_quarter = folder_validator.validate_current_folder(test_str1)
    validated, filelists = sfdc_validator.validate_sfdc_files(test_str1, current_year, current_quarter)
    validated, refined_files = refine_sfdc(filelists, current_year, current_quarter)

    if validated:
        print(refined_files)
    else:
        print("Error Happened!")


if __name__ == "__main__":
    main()
