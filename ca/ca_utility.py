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


def roll_up_SFDC_GEO(ca_session):
    # after combine_SFDC_allocation, roll up all managers numbers.
    # Step 1, pickup a manager from GEO List.
    # Step 2, get all his reporters down to lowest level sales rep and sum all SFDC numbers.
    # Step 3, Done.
    # Key points: each managers will sum numbers from all reporters, including low level manager
    # and lowest level sales.
    all_managers = build_all_managers_list(ca_session)
    allocated_file = ca_session.get_combined_sfdc_allocation_filename()
    allocated_df = pd.read_csv(allocated_file, index_col='EMPLOYEE NO')
    allocated_df.drop('INACTIVE', axis=1, inplace=True)
    allocated_df.drop('ISMANAGER', axis=1, inplace=True)

    roll_up_df = pd.DataFrame(columns=allocated_df.columns)
    for manager in all_managers:
        all_reporters = ca_session.get_hierarchy().get_all_reporters_and_selfobj(manager)
        reporter_list = []
        for reporter in all_reporters:
            reporter_list.append(int(reporter.get_emp_no()))
        manager_df = allocated_df[
            allocated_df.index.get_level_values('EMPLOYEE NO').isin(reporter_list)]

        roll_up_df.loc[manager] = manager_df.sum()

    roll_up_df.index.names = ['EMPLOYEE NO']

    cleaned_geo_file = ca_session.get_cleaned_GEO_filename()
    cleaned_geo_df = pd.read_csv(cleaned_geo_file, index_col='EMPLOYEE NO')
    roll_up_df = pd.merge(roll_up_df, cleaned_geo_df, left_index=True,
                          right_index=True, suffixes=('', '_PLAN'), how='outer')
    roll_up_df.to_csv(ca_session.get_manager_rollup_filename())
    # print(roll_up_df)
    # print(all_managers)
    return


def combine_SFDC_allocation(ca_session):
    # this combination should based all available sales and manager from GEO.
    # sales manager will be traced back to top level.
    # this change is due to the reason that a manager may have opportunity in SFDC!!!
    # Step 1, get all managers and sales list
    # Step 2, merge non-bigdeal from pivot SFDC
    # Step 3, merge bigdeal from pivot SFDC
    # Step 4, merge with allocated GEO
    # Done
    csvfile = ca_session.get_sales_manager_mapping_filename()
    emp_df = pd.read_csv(csvfile, index_col='EMPLOYEE NO')
    emp_df.drop('MANAGER', axis=1, inplace=True)
    emp_df.drop('LOWESTLEVEL', axis=1, inplace=True)
    # print(emp_df)

    default_pivot_sfdc = ca_session.get_summarized_filtered_pivot_sfdc_file()
    # even it is called "filtered", indeed it includes all ales and manager and inactive sales.
    default_pivot_sfdc_df = pd.read_csv(default_pivot_sfdc, index_col=['EMPLOYEE NO', 'BIG DEAL'])
    pivot_sfdc_nonbigdeal_df = default_pivot_sfdc_df.iloc[
        default_pivot_sfdc_df.index.get_level_values('BIG DEAL') == 'NO']

    pivot_sfdc_nonbigdeal_df.reset_index(level=1, drop=True, inplace=True)

    pivot_sfdc_bigdeal_df = default_pivot_sfdc_df.iloc[
        default_pivot_sfdc_df.index.get_level_values('BIG DEAL') == 'YES']

    pivot_sfdc_bigdeal_df.reset_index(level=1, drop=True, inplace=True)

    pivot_sfdc_df = pd.merge(pivot_sfdc_nonbigdeal_df, pivot_sfdc_bigdeal_df,
                             left_index=True, right_index=True, how='outer',
                             suffixes=('_NONBIGDEAL', '_BIGDEAL'))
    pivot_sfdc_df = pd.merge(emp_df, pivot_sfdc_df,
                             left_index=True, right_index=True, how='outer')

    config_dict = getGeneralConfigurationDict("SFDC Summary Rule", ca_session.get_configuration_file())
    for key in config_dict.keys():
        key_split_file = ca_session.get_split_key_filename(key)
        key_df = pd.read_csv(key_split_file, index_col='EMPLOYEE NO')
        col_tobedeleted = []
        for col in key_df.columns:
            if not col.endswith('ALLOCATED'):
                col_tobedeleted.append(col)
        key_df = key_df.drop(col_tobedeleted, axis=1)
        key_df = key_df.round()
        pivot_sfdc_df = pd.merge(pivot_sfdc_df, key_df,
                                 left_index=True, right_index=True, how='outer')

    pivot_sfdc_df = pivot_sfdc_df.fillna(0)

    pivot_sfdc_df.to_csv(ca_session.get_combined_sfdc_allocation_filename())

    # print(pivot_sfdc_df)
    # saleslist = pd.Series(df['EMPLOYEE NO']).unique()
    # unique_sales_list = sorted(list(saleslist))  # all sales and manager and inactive sales

    # print(unique_sales_managers)

    return


def build_all_managers_list(ca_session):
    '''
    get all unique sales list and check their up level managers until top's level recursively.
    :param ca_session:
    :return:
    '''
    unique_sales_list = sorted(list(get_unique_saleslist(ca_session)))
    # print(unique_sales_list)
    # need to consider to include inactive sales in list.
    all_managers = ca_session.build_all_managers_list(unique_sales_list)

    return all_managers

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

    #print(ca_session.get_default_pivot_SFDC_file())

    allocation_step1_sfdc = ca_session.get_allocation_step1_filename()

    filtered_pivot = ca_session.get_default_filterd_pivot_SFDC_file()
    # get default filtered_pivot_SFDC, not file list.
    filtered_df = pd.read_csv(filtered_pivot, index_col=['EMPLOYEE NO', 'BIG DEAL'])
    filtered_df = filtered_df[filtered_df.index.get_level_values('BIG DEAL') == 'NO']
    unique_sales_list = sorted(list(get_unique_saleslist(ca_session)))
    filtered_df = filtered_df[filtered_df.index.get_level_values('EMPLOYEE NO').isin(unique_sales_list)]

    for key, column_list in config_dict.iteritems():
        filtered_df[(key.upper() + "_NONBIGDEAL")] = filtered_df[column_list].sum(axis=1)
        filtered_df = filtered_df.drop(column_list, axis=1)

    for col in filtered_df.columns:
        if "TOTAL" in col:
            filtered_df.drop(col, axis=1, inplace=True)

    # 20160731 added to filter only active sales
    filtered_df.reset_index(level=1, drop=True, inplace=True)
    # till now, only 3 columns left, EMPLOYEE NO, ACV-NONBIGDEAL_NONBIGDEAL, PERB-NONBIGDEAL_NONBIGDEAL
    # print(filtered_df)

    merged_sfdc_sum_manager_df = pd.read_csv(ca_session.get_05_merged_SFDC_sum_file(),
                                             index_col=["EMPLOYEE NO"])
    merged_sfdc_sum_manager_df = merged_sfdc_sum_manager_df[
        merged_sfdc_sum_manager_df['BIG DEAL'] != 'YES'
        ]
    # print(merged_sfdc_sum_manager_df)
    allowed_columns = []
    # for key in config_dict.keys():
    #    allowed_columns.append(key.upper()) # add ACV, PERB
    allowed_columns.append("MANAGER")

    for col in merged_sfdc_sum_manager_df.columns:
        if not col in allowed_columns:
            merged_sfdc_sum_manager_df.drop(col, axis=1, inplace=True)

    merged_sfdc_sum_manager_df.sort_index(inplace=True)
    merged_sfdc_sum_manager_df = merged_sfdc_sum_manager_df.fillna(0)
    # print(merged_sfdc_sum_manager_df)
    # filtered_df = filtered_df.join(merged_sfdc_sum_manager_df)
    filtered_df = pd.merge(filtered_df, merged_sfdc_sum_manager_df,
                           left_index=True, right_index=True)
    # print(filtered_df)
    # merge with eligible list
    eligible_df = pd.read_csv(ca_session.get_20_booking_eligible_list_file(), index_col="EMPLOYEE NO")
    eligible_df.sort_index(inplace=True)

    filtered_df = filtered_df.join(eligible_df, lsuffix="", rsuffix="_BOOKINGTOTAL", how='left')
    allowed_keys = []
    for key in config_dict.keys():
        allowed_keys.append(key.upper())  # only ACV, PERB etc.

    # read GEO forecast (deducted all existing) for allocation
    rest_geo_df = pd.read_csv(ca_session.get_15_merged_GEO_SFDC_sum_file(), index_col="EMPLOYEE NO")
    rest_geo_dict = {}
    for key in allowed_keys:
        rest_key_df = rest_geo_df.copy()
        for col in rest_key_df.columns:
            if col != key.upper():
                rest_key_df.drop(col, axis=1, inplace=True)

        # only keep numbers > 0
        rest_key_df[key + "_REST"] = rest_key_df[key.upper()].map(lambda x: 0 if x < 0 else x)
        rest_key_df.drop(key.upper(), axis=1, inplace=True)
        rest_geo_dict[key] = rest_key_df
        # print(rest_key_df)

    for key in allowed_keys:
        key_df = filtered_df.copy()
        for col in key_df.columns:
            if (not col == "MANAGER") and (not col.startswith(key)):
                key_df.drop(col, axis=1, inplace=True)
        eligible_key = key + "_ELIGIBLE"
        key_df = key_df[key_df[eligible_key] != False]
        # need one more step to remove inactive sales from this list after big deal calculation.

        nonbigdeal_key = key + "_NONBIGDEAL"
        key_mgr_series = key_df.groupby('MANAGER')[nonbigdeal_key].sum()
        nonbigdeal_sum_key = nonbigdeal_key + "_SUM"
        key_mgr_series.name = nonbigdeal_sum_key

        nonbigdeal_ratio_key = nonbigdeal_key + "_PER"
        key_mgr_df = key_mgr_series.to_frame()

        # key_mgr_df = pd.pivot_table(key_df, index='MANAGER', values=[nonbigdeal_key], fill_value=0)

        key_df = pd.merge(key_df, key_mgr_df, left_on="MANAGER", suffixes=('', '_MGR'), right_index=True)
        key_df[nonbigdeal_ratio_key] = key_df[nonbigdeal_key] / key_df[nonbigdeal_sum_key]

        zero_key_df = key_df[key_df[nonbigdeal_sum_key] == 0.0]
        zero_mgr_df = zero_key_df.groupby('MANAGER')[nonbigdeal_sum_key].agg(['count'])
        # print(zero_mgr_df)
        for index, row in zero_mgr_df.iterrows():
            print index, row['count']
            key_df.loc[key_df['MANAGER'] == index, nonbigdeal_ratio_key] = 1.0 / (float(row['count']))
        # print(zero_mgr_df.columns)
        # combine rest of GEO
        rest_geo_df = rest_geo_dict.get(key.upper(), None)
        key_df = pd.merge(key_df, rest_geo_df, left_on="MANAGER", right_index=True)
        # calculate allocation
        rest_geo_key = key + "_REST"
        allocated_key = key + "_ALLOCATED"
        key_df[allocated_key] = key_df[rest_geo_key] * key_df[nonbigdeal_ratio_key]

        # step2_total_key = key+"_STEP2TOTAL"
        # key_df[step2_total_key] = key_df[allocated_key] + key_df[nonbigdeal_key]

        key_file = ca_session.get_split_key_filename(key)
        key_df.to_csv(key_file)

    #print(eligible_df)

    filtered_df.to_csv(allocation_step1_sfdc)


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
            summary_df = summary_df.join(df, how='outer')  # to be check to have max join from both sides.
            summary_df = summary_df.fillna(0)

    # summary each Q booking again.
    for key in summary_keys:
        column_list = []
        for col in summary_df.columns:
            if col.startswith(key.upper()):
                column_list.append(col)
        summary_df[key.upper()] = summary_df[column_list].sum(axis=1)

    # read threshold
    threshold_dict = getGeneralConfigurationThreshold("Booking Eligible Threshold",
                                                      ca_session.get_configuration_file())

    for key, threshold_value in threshold_dict.iteritems():
        summary_df[(key.upper() + "_ELIGIBLE")] = (summary_df[(key.upper())] < threshold_value)

    # print(summary_df)
    summary_df.to_csv(ca_session.get_booking_eligible_list_filename())  # 20-Booking-Eligible-List


def merge_SFDC_summary_with_manager(ca_session):
    '''
    calculate remaining GEO after big deal reduction.
    :param ca_session:
    :return:
    '''
    # only deal with default SFDC
    sfdc_file = ca_session.get_summarized_filtered_pivot_sfdc_file()    # 01-
    sfdc_df = pd.read_csv(sfdc_file, index_col='EMPLOYEE NO')

    sales_map = ca_session.get_sales_manager_mapping_file()
    sales_map_df = pd.read_csv(sales_map, index_col='EMPLOYEE NO', dtype=object)

    sales_map_df = sales_map_df[sales_map_df['LOWESTLEVEL'] == 'TRUE']
    merged_df = sales_map_df.join(sfdc_df)
    merged_df.to_csv(ca_session.get_merged_SFDC_sum_filename())  # 05-Merged-SFDC-BigDeal-Manager

    # only get keys as summrized field header
    config_keys = getGeneralConfigurationKeys("SFDC Summary Rule", ca_session.get_configuration_file())
    # print(config_keys)
    # start to pivot big deal to manager level in order to deduct from GEO.

    pivot_mgr_df = merged_df.groupby(['MANAGER']).sum()
    pivot_mgr_df = pivot_mgr_df.fillna(0)
    # print(pivot_mgr_df)
    #pivot_mgr_df = pd.pivot_table(merged_df, index='MANAGER', values=config_keys, fill_value=0)
    pivot_mgr_df.index = pivot_mgr_df.index.map(int)
    pivot_mgr_df.index.names = ['EMPLOYEE NO']

    pivot_mgr_df.to_csv(ca_session.get_pivot_manager_SFDC_sum_filename())  # 10-Pivot-MGR-SFDC-BigDeal

    cleaned_GEO_df = pd.read_csv(ca_session.get_cleaned_GEO_filename(), index_col='EMPLOYEE NO',
                                 dtype=object)
    cleaned_GEO_df.sort_index(inplace=True)

    # deducted_mgr_df = cleaned_GEO_df.join(pivot_mgr_df, lsuffix='_plan', rsuffix='_bigdeal')
    deducted_mgr_df = cleaned_GEO_df.join(pivot_mgr_df, lsuffix='_plan', rsuffix='_sfdc')
    deducted_mgr_df = deducted_mgr_df.fillna(0)
    #print(deducted_mgr_df)
    for col in config_keys:
        plan_col = "%s_plan" % col
        # bigdeal_col = "%s_bigdeal" % col
        sfdc_col = "%s_sfdc" % col
        deducted_mgr_df[plan_col] = deducted_mgr_df[plan_col].astype(float)
        # deducted_mgr_df[col] = deducted_mgr_df[plan_col].sub(deducted_mgr_df[bigdeal_col], axis=0)
        deducted_mgr_df[col] = deducted_mgr_df[plan_col].sub(deducted_mgr_df[sfdc_col], axis=0)
    deducted_mgr_df.to_csv(ca_session.get_merged_GEO_SFDC_sum_filename())  # 15-Merged-GEO-SFDC-sum


def summary_filtered_pivot_SFDC(ca_session):
    '''
    from filtered_pivot_SFDC_file, summary to ACV and PERP, depending on [SFDC Summary Rule] section.
    include all data: non-bigdeal and big deal and inactive data.
    :param ca_session:
    :return:
    '''
    filtered_pivot_sfdc = ca_session.get_filtered_pivot_SFDC_filelist()
    config_dict = getGeneralConfigurationDict("SFDC Summary Rule", ca_session.get_configuration_file())
    # get summary title list.

    inactive_list = sorted(list(get_unique_inactive_saleslist(ca_session)))

    for filtered_pivot in filtered_pivot_sfdc:
        summarized_filtered_pivot_sfdc = ca_session.get_summarized_filtered_pivot_sfdc_filename(filtered_pivot)
        ca_session.add_summarized_filtered_pivot_SFDC(summarized_filtered_pivot_sfdc)
        filtered_df = pd.read_csv(filtered_pivot, index_col=['EMPLOYEE NO', 'BIG DEAL'])
        #filtered_df = pd.read_csv(filtered_pivot, index_col=['EMPLOYEE NO'])
        key_list = []
        for key, column_list in config_dict.iteritems():
            filtered_df[key.upper()] = filtered_df[column_list].sum(axis=1)
            key_list.append(key.upper())
            # filtered_df = filtered_df.drop(column_list, axis=1)
        drop_col_list = []
        for col in filtered_df.columns:
            if not col in key_list:
                drop_col_list.append(col)
        filtered_df = filtered_df.drop(drop_col_list, axis=1)

        '''
        inactive_df = filtered_df.iloc[filtered_df.index.get_level_values('EMPLOYEE NO').isin(inactive_list)]
        grouped_df = inactive_df.groupby(level = 0).sum()
        grouped_df['BIG DEAL'] = 'INACTIVE'
        #print(grouped_df)
        filtered_df = filtered_df.iloc[filtered_df.index.get_level_values('EMPLOYEE NO').isin(inactive_list)==False]
        filtered_df = filtered_df.iloc[filtered_df.index.get_level_values('BIG DEAL') == 'YES']
        filtered_df.reset_index(['BIG DEAL'], inplace=True)
        filtered_df = pd.concat([filtered_df, grouped_df])
        #filtered_df = filtered_df[filtered_df['BIG DEAL'] == 'YES']'''

        # what should be deducted from GEO first? it should be total numbers of all managers and sales.
        # not only: inactive numbers + big deal
        filtered_df.to_csv(summarized_filtered_pivot_sfdc)  # 01-Summarized-Filtered-Pivot-FY16Q?-SFDC


def filter_booking_SFDC(ca_session):
    '''
    only keep booking and SFDC record for sales under current managers in GEO forecast.
    :param ca_session:
    :return:
    '''
    booking_files = ca_session.get_cleaned_booking_filelist()
    # get all available sales list from reporters of all managers who has GEO numbers.

    csvfile = ca_session.get_sales_manager_mapping_filename()
    df = pd.read_csv(csvfile)

    saleslist = pd.Series(df['EMPLOYEE NO']).unique()

    unique_sales_list = sorted(list(saleslist))

    # when filter SFDC, all managers and inactive record will be kept.
    # filter SFDC opporunity based on unique sales list.
    sfdc_files = ca_session.get_cleaned_SFDC_filelist()
    for sfdc_file in sfdc_files:
        filtered_sfdc_file = ca_session.get_filtered_SFDC_filename(sfdc_file)
        ca_session.add_filtered_SFDC_file(filtered_sfdc_file)
        sfdc_df = pd.read_csv(sfdc_file, index_col="OPPORTUNITY NUMBER")
        filtered_sfdc_df = sfdc_df[(sfdc_df['EMPLOYEE NO']).isin(unique_sales_list)]
        filtered_sfdc_df.to_csv(filtered_sfdc_file)

    # filter pivot SFDC file based on unique sales list
    pivot_files = ca_session.get_pivot_SFDC_filelist()
    for pivot_file in pivot_files:
        filtered_pivot_sfdc_file = ca_session.get_filtered_pivot_SFDC_filename(pivot_file)
        ca_session.add_filtered_pivot_SFDC_file(filtered_pivot_sfdc_file)
        pivot_df = pd.read_csv(pivot_file, index_col="EMPLOYEE NO")
        filtered_df = pivot_df[(pivot_df.index).isin(unique_sales_list)]
        filtered_df.to_csv(filtered_pivot_sfdc_file)

    df = df[df['LOWESTLEVEL'] == True]
    df = df[df['INACTIVE'] == False]
    df = df[df['ISMANAGER'] == False]
    saleslist = pd.Series(df['EMPLOYEE NO']).unique()

    unique_sales_list = sorted(list(saleslist))

    # when filter bookings, only active sales will be kept.
    # filter booking file based on unique sales list
    for booking_file in booking_files:
        filtered_booking_file = ca_session.get_filtered_booking_filename(booking_file)
        ca_session.add_filtered_booking_file(filtered_booking_file)
        booking_df = pd.read_csv(booking_file, index_col="EMPLOYEE NO")
        filtered_booking_df = booking_df[(booking_df.index).isin(unique_sales_list)]
        filtered_booking_df.to_csv(filtered_booking_file)


def get_unique_inactive_saleslist(ca_session):
    '''
    get all inactive sales from current managers reporters in GEO forecast
    :param ca_session:
    :return:
    '''
    csvfile = ca_session.get_sales_manager_mapping_filename()
    df = pd.read_csv(csvfile)
    # filter all inactive sales and manager postions.

    # df = df[df['LOWESTLEVEL']==True]
    df = df[df['INACTIVE'] == True]
    # df = df[df['ISMANAGER']== False]
    # print(df)
    saleslist = pd.Series(df['EMPLOYEE NO']).unique()
    # print(saleslist)
    return saleslist

def get_unique_saleslist(ca_session):
    '''
    get all availalbe sales from current managers reporters in GEO forecast
    :param ca_session:
    :return:
    '''
    csvfile = ca_session.get_sales_manager_mapping_filename()
    df = pd.read_csv(csvfile)
    # filter all inactive sales and manager postions.

    df = df[df['LOWESTLEVEL'] == True]
    df = df[df['INACTIVE'] == False]
    df = df[df['ISMANAGER']== False]
    #print(df)
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

    mapping_df = pd.DataFrame(columns=['MANAGER', 'EMPLOYEE NO', 'LOWESTLEVEL', 'INACTIVE', 'ISMANAGER'])
    new_index = 0
    for index, row in df.iterrows():
        manager = ca_session.get_hierarchy().get_emp_list().get(str(index), None)
        if not manager:
            raise ValueError("%s can't be found in hierarchy!" % str(index))

        if not manager.is_manager():
            raise ValueError("%s is not a sales manager in hierarchy!" % str(index))

        # all_reporters = ca_session.get_hierarchy().get_all_lowest_reporters(manager)
        all_reporters = ca_session.get_hierarchy().get_all_reporters_and_self(manager)
        # 20160731 changed from pure lowest level sales to all low lever sales/manager and himeself
        # in order to deal with the case that sales manager has SFDC opportunity.
        for reporter in all_reporters:
            # detect intersection of current manager list and this manager's reporters.
            intersec_list = list(set(manager.get_reporters()).intersection(manager_list_str))
            active_status = reporter.is_termed()
            is_manager_status = reporter.is_manager()
            if len(intersec_list) == 0 or intersec_list[0] == str(index):
                # current manager doesn't have lower manager in GEO list or only himself.
                mapping_df.loc[new_index] = [str(index), reporter.get_emp_no(), 'TRUE', active_status,
                                             is_manager_status]
            else:
                mapping_df.loc[new_index] = [str(index), reporter.get_emp_no(), 'FALSE', active_status,
                                             is_manager_status]
                # this manager has low level manager in GEO forecast

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
                    # row[col_name] = "%10.1f" % (float((row[col_name]).replace(",", "")) * 1000000.0)
                    row[col_name] = "%10.1f" % (float((row[col_name]).replace(",", "")) * 1.0)
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
        raise ValueError("SFDC Pivot Configuration Parameter Error!\n")

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

    index_keys = [sfdc_pivot_key, "BIG DEAL"]

    # pivot_dataframe = pd.pivot_table(sfdc_dataframe, index=index_keys, values=sfdc_pivot_header, aggfunc=np.sum)
    pivot_dataframe = sfdc_dataframe.groupby(index_keys)[sfdc_pivot_header].sum()
    pivot_dataframe = pivot_dataframe.fillna(0)
    pivot_dataframe.to_csv(pivoted_file_name)

    return pivoted_file_name
