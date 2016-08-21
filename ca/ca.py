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
    currentPath = "."
    if len(sys.argv) > 1:
        currentPath = sys.argv[1]

    ca_session = casession.CASession(currentPath)
    ca_session.get_hierarchy().validate_emp_list()
    # position = ca_session.get_hierarchy().generate_position()
    # org_illustration.illustrate(ca_session.get_hierarchy(), position, ca_session.get_img_filename())
    ca_session.clean_bookings()
    ca_session.clean_commission_plan()
    ca_session.clean_ytd_file()
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

    # allocation algorithm is: after deduction of existing SFDC, allocated by percentage of remaining
    # Non-bigdeal size.
    # if all sales rep has 0 in non-big deal numbers, it will be spread out equally.

    '''
    print("\n\nStart to allocate based on regular algorithm...")
    # ca_utility.allocate_remaining_GEO_regular(ca_session)
    ca_utility.allocate_remaining_GEO_extreme(ca_session, "regular")
    ca_utility.combine_SFDC_allocation(ca_session, "regular")
    ca_utility.roll_up_SFDC_GEO(ca_session, "regular")
    print("Done!\n\n\n")

    print("Start to allocate based on verylow algorithm...")
    ca_utility.allocate_remaining_GEO_extreme(ca_session, "verylow")
    ca_utility.combine_SFDC_allocation(ca_session, "verylow")
    ca_utility.roll_up_SFDC_GEO(ca_session, "verylow")
    print("Done!\n\n\n")

    print("Start to allocate based on lowest algorithm...")
    ca_utility.allocate_remaining_GEO_extreme(ca_session, "lowest")
    ca_utility.combine_SFDC_allocation(ca_session, "lowest")
    ca_utility.roll_up_SFDC_GEO(ca_session, "lowest")
    print("Done!\n\n\n")

    print("Start to allocate based on highest algorithm...")
    ca_utility.allocate_remaining_GEO_extreme(ca_session, "highest")
    ca_utility.combine_SFDC_allocation(ca_session, "highest")
    ca_utility.roll_up_SFDC_GEO(ca_session, "highest")
    print("Done!\n")
    '''

    print("\n\nStart to allocate based on regular algorithm...")
    ca_utility.allocate_remaining_GEO(ca_session, "regular")
    ca_utility.combine_SFDC_allocation(ca_session, "regular")
    ca_utility.calculate_booking(ca_session, "regular")
    ca_utility.roll_up_SFDC_GEO(ca_session, "regular")
    ca_utility.combine_manager_sales(ca_session, "regular")
    print("Done!\n\n\n")

    print("\n\nStart to allocate based on highest algorithm...")
    ca_utility.allocate_remaining_GEO(ca_session, "highest")
    ca_utility.combine_SFDC_allocation(ca_session, "highest")
    ca_utility.calculate_booking(ca_session, "highest")
    ca_utility.roll_up_SFDC_GEO(ca_session, "highest")
    ca_utility.combine_manager_sales(ca_session, "highest")
    print("Done!\n\n\n")

    print("\n\nStart to allocated based on best guess algorithm...")
    ca_utility.allocate_remaining_GEO(ca_session, "bestguess")
    ca_utility.combine_SFDC_allocation(ca_session, "bestguess")
    ca_utility.calculate_booking(ca_session, "bestguess")
    ca_utility.roll_up_SFDC_GEO(ca_session, "bestguess")
    ca_utility.combine_manager_sales(ca_session, "bestguess")
    print("Done!\n")


    #ca_utility.allocate_remaining_GEO(ca_session,"test")


if __name__ == "__main__":
    main()
