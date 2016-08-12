#!/usr/bin/env python
import sys
import os
import pandas as pd

sys.path.append(".")

try:
    from . import salesman
    from . import hierarchy
    from . import bezier
    from . import casession
    from . import ca_utility
    from . import org_illustration
except:
    import salesman
    import hierarchy
    import bezier
    import casession
    import ca_utility
    import org_illustration


def calculate_distribution(ca_session, booking_summary, geo_mapped_file, keys):
    '''
    based sales-manager in geo-mapped_file mapping to calculate sales result
    distribution from booking file list.
    :param ca_session:
    :param booking_summary:
    :param geo_mapped_file:
    :param keys: ACV, PERB etc.
    :return:
    '''

    # print(booking_summary)
    # print(geo_mapped_file)
    # print(keys)
    cols_dict = build_range_columns()
    booking_value_col_list = []
    for key, col_name in cols_dict.iteritems():
        booking_value_col_list.append("Booking " + col_name)

    print(booking_value_col_list)

    data_col_list = list(cols_dict.values()) + ['TOTAL']
    index_col_list = ['KEY', 'MANAGER', 'QUARTER']

    mapped_manager_df = pd.read_csv(geo_mapped_file, index_col='EMPLOYEE NO')
    mapped_manager_df = mapped_manager_df[mapped_manager_df['LOWESTLEVEL'] == True]
    mapped_manager_df = mapped_manager_df[mapped_manager_df['ISMANAGER'] == False]

    manager_list = sorted(list(pd.Series(mapped_manager_df['MANAGER']).unique()))

    booking_summary_df = pd.read_csv(booking_summary, index_col='EMPLOYEE NO')

    booking_manager_df = booking_summary_df.join(mapped_manager_df)

    summary_df = pd.DataFrame(columns=(data_col_list + index_col_list + booking_value_col_list))
    summary_df.set_index(index_col_list, inplace=True)
    # summary_df.loc[('TEST_KEY','TEST_01018','FY16Q3'),'TOTAL'] = 3
    # print(summary_df)
    # for manager in manager_list:
    #    manager_detail_booking_df = booking_manager_df[booking_manager_df['MANAGER'] == manager]
    for key in keys:
        for q_index in range(ca_session.get_quarter() - 1):
            data_col = "%s-FY%2dQ%d" % (key.upper(), ca_session.get_year(), q_index + 1)
            quarter_header = 'FY%2dQ%d' % (ca_session.get_year(), q_index + 1)
            print(data_col)

            for manager in manager_list:
                manager_detail_booking_df = booking_manager_df[booking_manager_df['MANAGER'] == manager]
                manager_detail_series = pd.Series(manager_detail_booking_df[data_col])
                # print(manager_detail_series)

                analysis_result = analysis_serials(manager_detail_series, cols_dict)
                # print(analysis_result)
                for summary_col in summary_df.columns:
                    summary_df.loc[(key.upper(), manager, quarter_header), summary_col] = \
                        analysis_result.get(summary_col, 0)

                    # print(manager)
                    # print(manager_detail_booking_df)
    print(cols_dict)
    print(summary_df)
    summary_df.to_csv(os.path.join(ca_session.get_processing_folder(), "50-Test.csv"))
    # print(manager_list)


def analysis_serials(data_serial, cols_dict):
    '''
    analysis one data serial and categorize them into different bias to average.
    :param data_serial:
    :return:
    '''
    summary_dict = {}
    serial_size = data_serial.size
    if serial_size == 0:
        return summary_dict

    if serial_size == 1:
        col_name = cols_dict.get(0, "-5 - 5")
        summary_dict[col_name] = 1
        summary_dict['TOTAL'] = 1
        return summary_dict

    series_total = data_serial.sum()
    series_average = series_total / serial_size

    if abs(series_total) < 0.001:
        return summary_dict

    for index_key, data_value in data_serial.iteritems():
        data_gap = int((data_value - series_average) * 100.0 / series_average)
        data_gap_index = int((data_gap + 5) / 10)

        if 15 > data_gap_index > 10:
            data_gap_index = 10
        elif 30 > data_gap_index >= 15:
            data_gap_index = 11
        elif data_gap_index >= 30:
            data_gap_index = 12
        elif data_gap_index < -10:
            data_gap_index = -10

        col_name = cols_dict.get(data_gap_index, None)
        if not col_name:
            raise ValueError("Can't find right col title for %d" % data_gap_index)

        current_value = summary_dict.get(col_name, 0)
        summary_dict[col_name] = current_value + 1

        # added to calculate real booking value in each segment
        booking_col = "Booking " + col_name
        booking_value = summary_dict.get(booking_col, 0)
        summary_dict[booking_col] = booking_value + data_value

        #

        total_value = summary_dict.get('TOTAL', 0)
        summary_dict['TOTAL'] = total_value + 1

    return summary_dict


def build_range_columns():
    cols_dict = {}

    for index in range(10):
        if index == 0:
            cols_dict[0] = "(-5 - 5)"
        else:
            cols_dict[index] = "(%d - %d)" % ((index - 1) * 10 + 5, index * 10 + 5)
            cols_dict[-1 * index] = "(-%d - -%d)" % (index * 10 + 5, (index - 1) * 10 + 5)
    cols_dict[10] = "(95 - 145)"
    cols_dict[11] = "(145 - 300)"
    cols_dict[12] = "(300- )"
    cols_dict[-10] = "( - -95)"
    return cols_dict


def main():
    currentPath = "."
    if len(sys.argv) > 1:
        currentPath = sys.argv[1]

    ca_session = casession.CASession(currentPath)
    ca_session.get_hierarchy().validate_emp_list()

    '''
    # build booking list
    booking_list = []

    booking_folder = ca_session.get_booking_folder()
    for q_index in range(ca_session.get_quarter()-1):
        booking_filename = "Refined-FY%2dQ%d-Booking.csv" % (ca_session.get_year(), q_index+1)
        full_booking_filename = os.path.join(booking_folder,booking_filename)
        if not os.path.isfile(full_booking_filename):
            raise ValueError("%s doesn't exist yet!" % full_booking_filename)
        booking_list.append(full_booking_filename)
    '''
    booking_summary_file = ca_session.get_booking_eligible_list_filename()
    full_booking_summary_file = os.path.join(ca_session.get_processing_folder(),
                                             booking_summary_file)
    if not os.path.isfile(full_booking_summary_file):
        raise ValueError("%s can't be found!" % full_booking_summary_file)

    # build sales and manager mapping file
    mapped_filename = "Mapped-FY%dQ%d-GEOForecast.csv" % \
                      (ca_session.get_year(), ca_session.get_quarter())
    full_mapped_filename = os.path.join(ca_session.get_GEO_folder(), mapped_filename)
    if not os.path.isfile(full_mapped_filename):
        raise ValueError("%s doesn't exist yet!" % full_mapped_filename)

    config_dict = ca_utility.getGeneralConfigurationDict("SFDC Summary Rule", ca_session.get_configuration_file())

    calculate_distribution(ca_session, full_booking_summary_file,
                           full_mapped_filename, config_dict.keys())


if __name__ == "__main__":
    main()
