import os
import sys
import csv
import ConfigParser
import pandas as pd
import numpy as np

sys.path.append(".")

try:
    from . import folder_validator
    from . import sfdc_validator
    from . import sfdc_refiner
    from . import booking_refiner
    from . import booking_validator
except:
    import folder_validator
    import sfdc_validator
    import sfdc_refiner
    import booking_refiner
    import booking_validator


def getConfiguration(section=r'Booking Summary Rule', configuration_file=r'./config.ini'):
    '''
    read all configurations in dict from specific section in specific configuration file.
    :param configuration_file:
    :param section:
    :return: parsed configuration, header will be translated into list.
    '''
    caconfig = ConfigParser.ConfigParser()
    caconfig.read(configuration_file)
    current_config = {}

    options = caconfig.options(section)
    for option in options:
        try:
            current_config[option] = caconfig.get(section, option)
            if not (current_config[option] == -1 or current_config[option] is None):
                pivot_header_list = []
                for x in (current_config[option]).split(","):
                    pivot_header_list.append(x.strip())
                current_config[option] = pivot_header_list
        except:
            print("Booking Total has exception on %s!" % option)
            current_config[option] = None

    return current_config


def pickupFYQ_fromfile(datafile):
    filename = os.path.basename(datafile)
    return filename[-18:-12]


def calculate_total_booking(booking_files, section=r'Booking Summary Rule', configuration_file=r'./config.ini'):
    '''
    calculate all booking files and:
    1) calculate into individual total files based on configuration
    2) concat all total files into one sintle YTD files.
    :param booking_files:
    :param section:
    :param configuration_file:
    :return: Sucess?, total file name in list.
    '''
    current_config = getConfiguration(section, configuration_file)
    calculated_files = []
    key_header = "EMPLOYEE NO"

    if current_config is None:
        print("Booking_tootal->calculate_total_booking can't find right configurations!")
        return None, calculated_files

    base_dir_name = None
    for cleaned_file in booking_files:
        fyq_str = pickupFYQ_fromfile(cleaned_file)
        base_dir_name = os.path.dirname(cleaned_file)
        newfilename = os.path.join(base_dir_name, "Total-" + fyq_str + "-Booking.csv")

        cleaned_df = pd.read_csv(cleaned_file, index_col=key_header)
        new_headers = []
        new_headers.append(key_header)
        for totalkey, headers_for_total in current_config.iteritems():
            new_col = fyq_str + " " + totalkey.upper() + " Total"
            cleaned_df[new_col] = cleaned_df[headers_for_total].sum(axis=1)
            new_headers.append(new_col)

        for col in cleaned_df.columns:
            if not (col in new_headers):
                del cleaned_df[col]

        cleaned_df.to_csv(newfilename)  # save individual total file.
        calculated_files.append(newfilename)

    cleaned_df = None  # save memory?
    new_total_name = os.path.join(base_dir_name, "Total-" + fyq_str[0:4] + "YTD-Booking.csv")
    df_list = []
    for calculated_file in calculated_files:
        cleaned_df = pd.read_csv(calculated_file, index_col=key_header)
        df_list.append(cleaned_df)
    total_result = pd.concat(df_list, axis=1)  # concat to one total file.

    total_result.to_csv(new_total_name)

    calculated_files = []  # without this, all individual total files will be returned.
    calculated_files.append(new_total_name)

    return True, calculated_files


def main():
    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"
    validated, current_year, current_quarter = folder_validator.validate_current_folder(test_str1)
    filelists = None
    if validated:
        validated, filelists = booking_validator.validate_booking_files(test_str1, current_year, current_quarter)
    else:
        print("Stopped at booking_validator!")
        return

    if validated:
        validated, filelists = booking_refiner.refine_booking(filelists, current_year, current_quarter)
    else:
        print("Stopped at booking_refiner!")
        return

    if validated:
        validated, filelists = calculate_total_booking(filelists)
    else:
        print("Stopped at calculate_total_booking!")
        return

    if validated:
        print(filelists)
    else:
        print("Error Happened!")


if __name__ == "__main__":
    main()
