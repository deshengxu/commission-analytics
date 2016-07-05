#!/usr/bin/env python

# ...
import os, re


def validate_current_folder(current_folder):
    '''

    :param current_folder: folder to be validated
    folder should be in pattern like: FY16Q1 FY17Q3 etc.
    :return: validated FY-year quarter.
      for example:True 16 1 or False None None
    '''

    if not current_folder or not (os.path.isdir(current_folder)):
        print("It's not a folder!")
        return False, None, None

    abspathname = os.path.abspath(current_folder)  # return /Desheng/sample/FY16Q1
    project_folder = abspathname[abspathname.rfind(os.path.sep) + 1:]  # return FY16Q1

    if not project_folder:
        print("You are not in a right project folder!")
        return False, None, None

    project_folder = re.sub('[\s+]', '', project_folder).upper()  # remove space and upper it.

    if len(project_folder) != 6 or project_folder[0:2] != 'FY' or project_folder[4:5] != 'Q':
        print("Wrong project folder name!")
        return False, None, None
    current_year_str = project_folder[2:4]
    current_quarter_str = project_folder[5:6]
    try:
        current_year = int(current_year_str)
        current_quarter = int(current_quarter_str)

        if 15 < current_year < 100 and 0 < current_quarter < 5:
            return True, current_year, current_quarter
        else:
            print("Year or quarter number is out of scope in folder structure!")
            return False, None, None
    except ValueError:
        print("Wrong year or quarter in folder name!")
        return False, None, None


def main():
    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"
    test_str2 = r"/Users/desheng/builds/commission-analytics/Sample/FY16 Q3  "
    test_str3 = r"/Users/desheng/builds/commission-analytics/Sample"
    test_str4 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3Fake"

    validated, current_year, current_quarter = validate_current_folder(test_str1)

    if validated and current_year == 16 and current_quarter == 3:
        print("Test is right on string %s!" % test_str1)
    else:
        print("Test is wrong on string %s!" % test_str1)

    validated, current_year, current_quarter = validate_current_folder(test_str2)

    if validated and current_year == 16 and current_quarter == 3:
        print("Test is right on string %s!" % test_str2)
    else:
        print("Test is wrong on string %s!" % test_str2)

    validated, current_year, current_quarter = validate_current_folder(test_str3)

    if (not validated) and current_year == None and current_quarter == None:
        print("Test is right on string %s!" % test_str3)
    else:
        print("Test is wrong on string %s!" % test_str3)

    validated, current_year, current_quarter = validate_current_folder(test_str4)

    if (not validated) and current_year == None and current_quarter == None:
        print("Test is right on string %s!" % test_str4)
    else:
        print("Test is wrong on string %s!" % test_str4)


if __name__ == "__main__":
    main()
