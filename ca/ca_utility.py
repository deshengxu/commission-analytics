import os
import sys
import csv
import ConfigParser
import pandas as pd
import numpy as np

sys.path.append(".")

try:
    from . import casession
except:
    import casession


def allocate_remaining_GEO(ca_session):
    '''
    allocate SFDC summary from GEO after big deal reduction.
    have to be careful for a stiuation that a up level manager who has many low level managers but also
    has individual direct sales rep in GEO forecast.
    this has to be avoided from GEO forecast check.
    :param ca_session:
    :return:
    '''

    # step 1, get all non-big deal SFDC (from file Pivot-FY6Q3-SFDC.csv)
    # Step 2, filtered by Eligible List
    # Step 3, summary posivie numbers by manager in Step 1 and calculate percentage
    # Step 4, Split 15-Merged-GEO-SFDC-BigDeal based on percentage.

    # Step 1, beginning code is copied from summary_filtered_pivot_SFDC()
    # but changed criteria from "YES" to NO.
    # and changed from file list to default SFDC pivoted file.
    config_dict = getGeneralConfigurationDict("SFDC Summary Rule", ca_session.get_configuration_file())
    # get summary title list.
    filtered_pivot = ca_session.get_default_pivot_SFDC_file()  # get default filtered_pivot_SFDC, not file list.

    allocation_step1_sfdc = ca_session.get_allocation_step1_filename()
    filtered_df = pd.read_csv(filtered_pivot, index_col=['EMPLOYEE NO', 'BIG DEAL'])
    for key, column_list in config_dict.iteritems():
        filtered_df[(key.upper() + "-NONBIGDEAL")] = filtered_df[column_list].sum(axis=1)
        filtered_df = filtered_df.drop(column_list, axis=1)

    for col in filtered_df.columns:
        if "TOTAL" in col:
            filtered_df.drop(col, axis=1, inplace=True)

    filtered_df = filtered_df.iloc[filtered_df.index.get_level_values('BIG DEAL') == 'NO']
    filtered_df.reset_index(level=1, drop=True, inplace=True)
    filtered_df.to_csv(allocation_step1_sfdc)

    # Step 2, merge with Eligible list.
    return


def get_key_from_filename(filename, ca_session):
    index_key = "FY%2dQ" % ca_session.get_year()
    index_found = filename.rfind(index_key)

    return filename[index_found:index_found + 6]


def merge_summary_filtered_booking(ca_session):
    '''sum booking based on predefined keys in two sections
    [Booking Summary Rule] and [SFDC Summary Rule]
    only common keys will be used'''
    summary_keys = getGeneralConfigurationKeys("SFDC Summary Rule", ca_session.get_configuration_file())
    # print(summary_keys)
    summary_cols = getGeneralConfigurationDict("Booking Summary Rule", ca_session.get_configuration_file())
    # print(summary_cols)
    booking_list = ca_session.get_filtered_booking_filelist()
    booking_df_dict = {}
    for booking_file in booking_list:
        booking_df = pd.read_csv(booking_file, index_col="EMPLOYEE NO")
        fyq_key = get_key_from_filename(booking_file, ca_session)  # FY16Q2 etc.

        for key, column_list in summary_cols.iteritems():
            if key.upper() in summary_keys:
                booking_df[key.upper()] = booking_df[column_list].sum(axis=1)

        for col in booking_df.columns:
            if not col in summary_keys:
                booking_df.drop(col, axis=1, inplace=True)

        # rename col with key.
        for col in booking_df.columns:
            booking_df.rename(columns={col: col + "-" + fyq_key}, inplace=True)

        booking_df_dict[fyq_key] = booking_df

    # merge all DFs
    first = True
    summary_df = None
    for key, df in booking_df_dict.iteritems():
        if first:
            summary_df = df
            first = False
        else:
            summary_df = summary_df.join(df)

    # summary each Q booking again.
    for key in summary_keys:
        column_list = []
        for col in summary_df.columns:
            if col.startswith(key.upper()):
                column_list.append(col)
        summary_df[key.upper()] = summary_df[column_list].sum(axis=1)

    # read threshold
    threshold_dict = getGeneralConfigurationThreshold("Booking Enigible Threshold",
                                                      ca_session.get_configuration_file())

    for key, threshold_value in threshold_dict.iteritems():
        summary_df[(key.upper() + "_ENIGIBLE")] = (summary_df[(key.upper())] < threshold_value)

    # print(summary_df)
    summary_df.to_csv(ca_session.get_booking_enigible_list_filename())  # 20-Booking-Enigible-List


def merge_SFDC_summary_with_manager(ca_session):
    '''
    calculate remaining GEO after big deal reduction.
    :param ca_session:
    :return:
    '''
    # only deal with default SFDC
    sfdc_file = ca_session.get_summarized_filtered_pivot_sfdc_file()
    sfdc_df = pd.read_csv(sfdc_file, index_col='EMPLOYEE NO')

    sales_map = ca_session.get_sales_manager_mapping_file()
    sales_map_df = pd.read_csv(sales_map, index_col='EMPLOYEE NO', dtype=object)

    sales_map_df = sales_map_df[sales_map_df['LOWESTLEVEL'] == 'TRUE']
    merged_df = sales_map_df.join(sfdc_df)

    # only get keys as summrized field header
    config_keys = getGeneralConfigurationKeys("SFDC Summary Rule", ca_session.get_configuration_file())
    # print(config_keys)
    # start to pivot big deal to manager level in order to deduct from GEO.
    merged_df.to_csv(ca_session.get_merged_SFDC_BigDeal_filename())

    pivot_mgr_df = pd.pivot_table(merged_df, index='MANAGER', values=config_keys, fill_value=0)
    pivot_mgr_df.index.names = ['EMPLOYEE NO']
    pivot_mgr_df.index = pivot_mgr_df.index.map(int)
    pivot_mgr_df.to_csv(ca_session.get_pivot_manager_SFDC_BigDeal_filename())  # 10-Pivot-MGR-SFDC-BigDeal

    cleaned_GEO_df = pd.read_csv(ca_session.get_cleaned_GEO_filename(), index_col='EMPLOYEE NO',
                                 dtype=object)
    cleaned_GEO_df.sort_index(inplace=True)

    deducted_mgr_df = cleaned_GEO_df.join(pivot_mgr_df, lsuffix='_plan', rsuffix='_bigdeal')
    deducted_mgr_df = deducted_mgr_df.fillna(0)
    for col in config_keys:
        plan_col = "%s_plan" % col
        bigdeal_col = "%s_bigdeal" % col
        deducted_mgr_df[plan_col] = deducted_mgr_df[plan_col].astype(float)
        deducted_mgr_df[col] = deducted_mgr_df[plan_col].sub(deducted_mgr_df[bigdeal_col], axis=0)
    deducted_mgr_df.to_csv(ca_session.get_merged_GEO_SFDC_BigDeal_filename())  # 15-Merged-GEO-SFDC-BigDeal


def summary_filtered_pivot_SFDC(ca_session):
    '''
    from filtered_pivot_SFDC_file, summary to ACV and PERP, depending on [SFDC Summary Rule] section.
    only select Big Deal = Yes.
    :param ca_session:
    :return:
    '''
    filtered_pivot_sfdc = ca_session.get_filtered_pivot_SFDC_filelist()
    config_dict = getGeneralConfigurationDict("SFDC Summary Rule", ca_session.get_configuration_file())
    # get summary title list.

    for filtered_pivot in filtered_pivot_sfdc:
        summarized_filtered_pivot_sfdc = ca_session.get_summarized_filtered_pivot_sfdc_filename(filtered_pivot)
        ca_session.add_summarized_filtered_pivot_SFDC(summarized_filtered_pivot_sfdc)
        filtered_df = pd.read_csv(filtered_pivot, index_col=['EMPLOYEE NO', 'BIG DEAL'])
        for key, column_list in config_dict.iteritems():
            filtered_df[key.upper()] = filtered_df[column_list].sum(axis=1)
            filtered_df = filtered_df.drop(column_list, axis=1)

        filtered_df = filtered_df.iloc[filtered_df.index.get_level_values('BIG DEAL') == 'YES']
        filtered_df.to_csv(summarized_filtered_pivot_sfdc)


def filter_booking_SFDC(ca_session):
    '''
    only keep booking and SFDC record for sales under current managers in GEO forecast.
    :param ca_session:
    :return:
    '''
    booking_files = ca_session.get_cleaned_booking_filelist()
    unique_sales_list = sorted(list(get_unique_saleslist(ca_session)))
    # print(unique_sales_list)
    for booking_file in booking_files:
        filtered_booking_file = ca_session.get_filtered_booking_filename(booking_file)
        ca_session.add_filtered_booking_file(filtered_booking_file)
        booking_df = pd.read_csv(booking_file, index_col="EMPLOYEE NO")
        filtered_booking_df = booking_df[(booking_df.index).isin(unique_sales_list)]
        filtered_booking_df.to_csv(filtered_booking_file)

    sfdc_files = ca_session.get_cleaned_SFDC_filelist()
    for sfdc_file in sfdc_files:
        filtered_sfdc_file = ca_session.get_filtered_SFDC_filename(sfdc_file)
        ca_session.add_filtered_SFDC_file(filtered_sfdc_file)
        sfdc_df = pd.read_csv(sfdc_file, index_col="OPPORTUNITY NUMBER")
        filtered_sfdc_df = sfdc_df[(sfdc_df['EMPLOYEE NO']).isin(unique_sales_list)]
        filtered_sfdc_df.to_csv(filtered_sfdc_file)

    pivot_files = ca_session.get_pivot_SFDC_filelist()
    for pivot_file in pivot_files:
        filtered_pivot_sfdc_file = ca_session.get_filtered_pivot_SFDC_filename(pivot_file)
        ca_session.add_filtered_pivot_SFDC_file(filtered_pivot_sfdc_file)
        pivot_df = pd.read_csv(pivot_file, index_col="EMPLOYEE NO")
        filtered_df = pivot_df[(pivot_df.index).isin(unique_sales_list)]
        filtered_df.to_csv(filtered_pivot_sfdc_file)


def get_unique_saleslist(ca_session):
    '''
    get all availalbe sales from current managers reporters in GEO forecast
    :param ca_session:
    :return:
    '''
    csvfile = ca_session.get_sales_manager_mapping_filename()
    df = pd.read_csv(csvfile)
    saleslist = pd.Series(df['EMPLOYEE NO']).unique()
    # print(saleslist)
    return saleslist


def build_sales_manager_map(ca_session):
    csvfile = ca_session.get_cleaned_GEO_filename()
    df = pd.read_csv(csvfile, index_col='EMPLOYEE NO', dtype=object)

    manager_list = sorted(list(df.index))  # to detect multilevel managers in single list.
    manager_list_str = map(lambda i: str(i), manager_list)
    # manager_list_str = []   # convert EMP NO from int to str
    # for manager in manager_list:
    #    manager_list_str.append(str(manager))

    mapping_df = pd.DataFrame(columns=['MANAGER', 'EMPLOYEE NO', 'LOWESTLEVEL'])
    new_index = 0
    for index, row in df.iterrows():
        manager = ca_session.get_hierarchy().get_emp_list().get(str(index), None)
        if not manager:
            raise ValueError("%s can't be found in hierarchy!" % str(index))

        if not manager.is_manager():
            raise ValueError("%s is not a sales manager in hierarchy!" % str(index))

        all_reporters = ca_session.get_hierarchy().get_all_lowest_reporters(manager)
        for reporter in all_reporters:
            # detect intersection of current manager list and this manager's reporters.
            if len(list(set(manager.get_reporters()).intersection(manager_list_str))) == 0:
                mapping_df.loc[new_index] = [str(index), reporter, 'TRUE']
            # else:
            #    mapping_df.loc[new_index] = [str(index), reporter, 'FALSE'] # this manager has low level manager

            new_index += 1
    mapping_df.to_csv(ca_session.get_sales_manager_mapping_filename(csvfile), index=False)


def clean_GEO_forecast(ca_session):
    csvfile = ca_session.get_GEO_file()
    df = pd.read_csv(csvfile, index_col='EMPLOYEE NO', dtype=object)
    new_columns = []
    for col_name in df.columns:
        new_columns.append(col_name.strip().upper())

    df.columns = new_columns  # clean columns name in case there is space.
    # print(list(df.index))

    for index, row in df.iterrows():
        manager = ca_session.get_hierarchy().get_emp_list().get(str(index), None)
        if not manager:
            raise ValueError("%s can't be found in hierarchy!" % str(index))

        if not manager.is_manager():
            raise ValueError("%s is not a sales manager in hierarchy!" % str(index))

        for col_name in df.columns:
            if not "NAME" in col_name:
                try:
                    row[col_name] = "%10.1f" % (float((row[col_name]).replace(",", "")) * 1000000.0)
                    # convert from M to float number
                except:
                    raise ValueError("Can't read forecast of %s at %s" % (col_name, index))

    df.to_csv(ca_session.get_cleaned_GEO_filename(csvfile))


def clean_SFDC_files(ca_session):
    sfdc_files = ca_session.get_SFDC_filelist()
    current_year = ca_session.get_year()
    current_quarter = ca_session.get_quarter()
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
        newfilename = ca_session.get_cleaned_SDFC_filename(sfdc_file)
        ca_session.add_cleaned_SFDC_file(newfilename)

        with open(sfdc_file, "r") as oldfile, open(newfilename, "w") as newfile:
            oldcsv = csv.reader(oldfile)
            newcsv = csv.writer(newfile)

            first_line = True
            name_index = -1
            big_deal_index = -1
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

                        if tmp_str == "BIG DEAL":
                            big_deal_index = ix

                    newcsv.writerow(header_list)
                    first_line = False
                else:
                    # if rix==1:
                    #    print(line)
                    data_list = []

                    for ix, cell in enumerate(line):
                        tmp_str = ""
                        try:
                            if ix != name_index:
                                tmp_str = cell.strip().replace(",", "")
                                if ix == big_deal_index:
                                    if not (tmp_str.upper() == "YES"):
                                        tmp_str = "NO"
                                    else:
                                        tmp_str = "YES"

                                    data_list.append(tmp_str)
                                else:
                                    if tmp_str == "-":
                                        tmp_str = "0.0"
                                    try:
                                        float(tmp_str)
                                    except:
                                        tmp_str = cell.strip()
                                    data_list.append(tmp_str)
                        except:
                            tmp_str = cell.strip()
                            data_list.append(tmp_str)

                    newcsv.writerow(data_list)


def getGeneralConfigurationDict(section, configuration_file=r'./config.ini'):
    caconfig = ConfigParser.ConfigParser()
    caconfig.read(configuration_file)
    current_config = {}

    options = caconfig.options(section)
    return_dict = {}

    for option in options:
        current_config[option] = caconfig.get(section, option)
        return_dict[option] = map(lambda x: x.strip(), current_config[option].split(","))

    return return_dict


def getGeneralConfigurationThreshold(section, configuration_file=r'./config.ini'):
    ''' read threshold value from configuration file.'''
    caconfig = ConfigParser.ConfigParser()
    caconfig.read(configuration_file)
    current_config = {}

    options = caconfig.options(section)
    return_dict = {}

    for option in options:
        current_config[option] = caconfig.get(section, option)
        return_dict[option] = convert_threshold_to_float(current_config[option])

    return return_dict


def convert_threshold_to_float(threshold_str):
    '''
    1.5M, 1M, 1 M, 2.2 m, 2.2M, 3.2K, 3.3 k, 3300, 3,300 etc.
    :param threshold_str:
    :return: float number
    '''
    new_str = None
    if threshold_str[-1] in 'MmKk':
        new_str = (threshold_str[:-2]).strip().replace(",", "")
    else:
        new_str = threshold_str.strip().replace(",", "")

    factor = 1.0
    if threshold_str[-1] in 'Mm':
        factor = 1000000.0
    elif threshold_str[-1] in 'Kk':
        factor = 1000.0

    try:
        return float(new_str) * factor
    except:
        raise ValueError("%s can't be converted!" % threshold_str)

def getGeneralConfigurationKeys(section, configuration_file=r'./config.ini'):
    caconfig = ConfigParser.ConfigParser()
    caconfig.read(configuration_file)
    current_config = {}

    options = caconfig.options(section)

    return map(lambda x: x.strip().upper(), options)


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


def pivot_SFDC_files(ca_session):
    sfdc_files = ca_session.get_cleaned_SFDC_filelist()
    section = r'General Rule'
    configuration_file = ca_session.get_configuration_file()

    config = getConfiguration(section, configuration_file)
    sfdc_load_key = config.get("sfdc_load_key", None)
    sfdc_pivot_key = config.get("sfdc_pivot_key", None)
    sfdc_pivot_header = config.get("sfdc_pivot_header", None)

    sfdc_pivot_files = []
    if sfdc_load_key is None or sfdc_pivot_key is None or sfdc_pivot_header is None or len(sfdc_pivot_header) == 0:
        print("SFDC Pivot Configuration Parameter Error!\n")
        return False, sfdc_pivot_files

    for sfdc_file in sfdc_files:
        pivot_file_name = ca_session.get_pivot_SFDC_filename(sfdc_file)
        pivot_result = pivot_one_sfdc(sfdc_file, sfdc_load_key, sfdc_pivot_key, sfdc_pivot_header, pivot_file_name)
        if pivot_result:
            ca_session.add_pivot_SFDC_file(pivot_result)
        else:
            raise ValueError("Error happened in pivot one SFDC file!")


def pivot_one_sfdc(sfdc_file, sfdc_load_key, sfdc_pivot_key, sfdc_pivot_header, pivoted_file_name):
    if sfdc_file is None or not os.path.isfile(sfdc_file) or not os.path.exists(sfdc_file):
        return None

    sfdc_dataframe = pd.read_csv(sfdc_file, index_col=sfdc_load_key)

    # generate pivot file with big deal as index
    # pivoted_file_name = os.path.join(os.path.dirname(sfdc_file), "Pivot_bigdealindexing" + os.path.basename(sfdc_file))

    index_keys = [sfdc_pivot_key, "BIG DEAL"]

    pivot_dataframe = pd.pivot_table(sfdc_dataframe, index=index_keys, values=sfdc_pivot_header, aggfunc=np.sum)

    pivot_dataframe.to_csv(pivoted_file_name)

    return pivoted_file_name
