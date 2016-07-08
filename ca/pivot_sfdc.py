#!/usr/bin/env python

# ...

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
except:
    import folder_validator
    import sfdc_validator
    import sfdc_refiner


def getConfiguration(section=r'General Rule', configuration_file=r'./config.ini'):
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
            if current_config[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            current_config[option] = None

    pivot_header_list = []
    if not (current_config["sfdc_pivot_header"] == -1 or current_config["sfdc_pivot_header"] is None):
        for x in (current_config["sfdc_pivot_header"]).split(","):
            pivot_header_list.append(x.strip())

    current_config["sfdc_pivot_header"] = pivot_header_list

    return current_config


def pivot_sfdc_files(sfdc_files, section=r'General Rule', configuration_file=r'./config.ini'):
    config = getConfiguration(section, configuration_file)
    sfdc_load_key = config.get("sfdc_load_key", None)
    sfdc_pivot_key = config.get("sfdc_pivot_key", None)
    sfdc_pivot_header = config.get("sfdc_pivot_header", None)

    sfdc_pivot_files = []
    if sfdc_load_key is None or sfdc_pivot_key is None or sfdc_pivot_header is None or len(sfdc_pivot_header) == 0:
        print("SFDC Pivot Configuration Parameter Error!\n")
        return False, sfdc_pivot_files

    for sfdc_file in sfdc_files:
        pivot_result = pivot_one_sfdc(sfdc_file, sfdc_load_key, sfdc_pivot_key, sfdc_pivot_header)
        if pivot_result:
            sfdc_pivot_files.append(pivot_result)
        else:
            return False, sfdc_pivot_files

    return True, sfdc_pivot_files


def pivot_one_sfdc(sfdc_file, sfdc_load_key, sfdc_pivot_key, sfdc_pivot_header):
    if sfdc_file is None or not os.path.isfile(sfdc_file) or not os.path.exists(sfdc_file):
        return None

    sfdc_dataframe = pd.read_csv(sfdc_file, index_col=sfdc_load_key)

    pivoted_file_name = os.path.join(os.path.dirname(sfdc_file), "Pivot_" + os.path.basename(sfdc_file))

    pivot_dataframe = pd.pivot_table(sfdc_dataframe, index=sfdc_pivot_key, values=sfdc_pivot_header, aggfunc=np.sum)

    pivot_dataframe.to_csv(pivoted_file_name)

    return pivoted_file_name


def main():
    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"
    validated, current_year, current_quarter = folder_validator.validate_current_folder(test_str1)
    validated, filelists = sfdc_validator.validate_sfdc_files(test_str1, current_year, current_quarter)
    validated, refined_files = sfdc_refiner.refine_sfdc(filelists, current_year, current_quarter)

    if validated:
        print(refined_files)
        validated, pivoted_files = pivot_sfdc_files(refined_files)
        if validated:
            print(pivoted_files)
        else:
            print("Error in pivoting!")
    else:
        print("Error Happened!")


if __name__ == "__main__":
    main()
