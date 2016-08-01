import sys

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


def main():
    # new_h = build_hierarchy_from_sample()
    # new_h = hierarchy.build_hierarchy_from_csv('../Sample/FY16Q3/FY16Q3-Hierarchy.csv')

    # width, depth = new_h.get_depth_width()
    # print("Width:%d, \tDepth:%d\n" % (width, depth))

    # test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q4"

    # ca_session = casession.CASession(test_str1)
    # print(sys.argv)
    # print("Length:%d" % len(sys.argv))
    currentPath = "."
    if len(sys.argv) > 1:
        currentPath = sys.argv[1]

    ca_session = casession.CASession(currentPath)
    ca_session.get_hierarchy().validate_emp_list()
    position = ca_session.get_hierarchy().generate_position()
    # print(position)
    org_illustration.illustrate(ca_session.get_hierarchy(), position, ca_session.get_img_filename())
    # print(ca_session.get_hierarchy())
    ca_session.clean_bookings()
    ca_utility.clean_SFDC_files(ca_session)
    # print(ca_session.get_cleaned_SFDC_filelist())

    ca_utility.pivot_SFDC_files(ca_session)
    # print(ca_session.get_pivot_SFDC_filelist())

    ca_utility.clean_GEO_forecast(ca_session)
    ca_utility.build_sales_manager_map(ca_session)
    # print(ca_utility.get_unique_saleslist(ca_session))
    ca_utility.filter_booking_SFDC(ca_session)
    ca_utility.summary_filtered_pivot_SFDC(ca_session)  # 01-
    ca_utility.merge_SFDC_summary_with_manager(ca_session)  # 05, 10, 15
    ca_utility.merge_summary_filtered_booking(ca_session)  # 20
    ca_utility.allocate_remaining_GEO(ca_session)

    # combine allocated ACV/PERB with original SFDC data to sales level
    # be careful, this will not be a filtered SFDC based on unique sales list
    # since we have to consider that a manager may have direct sales opportunity associated.
    ca_utility.combine_SFDC_allocation(ca_session)
    ca_utility.roll_up_SFDC_GEO(ca_session)
    '''

    #print(ca_session.get_hierarchy().get_emp_list())

    '''


if __name__ == "__main__":
    main()
