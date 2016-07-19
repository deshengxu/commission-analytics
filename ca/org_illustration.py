import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
import matplotlib.lines as lines

sys.path.append(".")

try:
    from . import salesman
    from . import hierarchy
    from . import bezier
    from . import casession
    from . import ca_utility
except:
    import salesman
    import hierarchy
    import bezier
    import casession
    import ca_utility


def illustrate(new_hierarchy, position):
    _, block_width, _, _, block_height, _ = new_hierarchy.get_base_position()

    max_x = 0.0
    max_y = 0.0

    fig, ax = plt.subplots()
    fig.set_size_inches(29.7, 21.1)
    for emp_no, emp_positions in position.iteritems():
        strx, stry = emp_positions.split(",")
        cx = float(strx)
        cy = float(stry)

        if cx > max_x:
            max_x = cx
        if cy > max_y:
            max_y = cy

        new_rec = mpatch.Rectangle((cx, cy), block_width, block_height)
        # ax.add_artist(new_rec)
        ax.add_patch(new_rec)
        position[emp_no] = new_rec  # not good practice to modify original data in this way.

    # start to draw connection line.
    top_emp_no = new_hierarchy.get_top_emp()
    if not top_emp_no:
        raise ValueError("Can't find top emp no in illustrate()")

    top_emp = new_hierarchy.get_emp_list().get(top_emp_no, None)
    if not top_emp:
        raise ValueError("Can't find top emp object in illustrate()")

    top_rec = position.get(top_emp_no, None)
    if not top_rec:
        raise ValueError("Can't find rectangle for top boss in illustrate()")

    draw_line(top_emp_no, top_emp, top_rec, new_hierarchy, position, fig, ax)

    max_x += block_width + 0.2
    max_y += block_height + 0.2
    # ax.set_xlim((0, max_x))
    # ax.set_ylim((0, max_y))
    ax.set_xlim((0, 21.1 * 2))
    ax.set_ylim((0, 29.7 * 3))
    ax.set_aspect('equal')

    # fig.savefig("../Sample/hierarchy.png", dpi=300)
    # fig.set_size_inches(max_x,max_y)
    fig.savefig("../Sample/hierarchy.svg", transparent=True, bbox_inches='tight', pad_inches=0)
    fig.savefig('../Sample/hierarchy.eps', format='eps', dpi=1000)
    #plt.show()


def draw_emp_no_name(emp_no, emp, new_rec, ax):
    rx, ry = new_rec.get_xy()
    cx = rx + new_rec.get_width() / 2.0
    cy = ry + new_rec.get_height() * 3.0 / 4.0
    ctext_y = ry + new_rec.get_height() / 4.0
    emp_name = emp.get_name()
    # print(emp_no, rx, ry)
    ax.annotate(emp_no, (cx, cy), color='w', fontsize=8, ha='center', va='center')
    ax.annotate(emp_name, (cx, ctext_y), color='w', fontsize=5, ha='center', va='center')


def draw_line(parent_emp_no, parent_emp, parent_rec, new_h, position, fig, ax):
    draw_emp_no_name(parent_emp_no, parent_emp, parent_rec, ax)

    reporters = parent_emp.get_reporters()
    # print(parent_emp_no, "-->", reporters)
    if len(reporters) == 0:
        return

    for child_emp_no in reporters:
        child_rec = position.get(child_emp_no, None)
        if not child_rec:
            raise ValueError("Can't child rec in draw_line()")
        start_x, start_y = parent_rec.get_xy()
        start_x += parent_rec.get_width()
        start_y += parent_rec.get_height() / 2.0

        end_x, end_y = child_rec.get_xy()
        end_y += child_rec.get_height() / 2.0

        # print(parent_emp_no,child_emp_no,start_x,start_y, end_x, end_y)
        # draw from start to end.

        # connect_line = [(start_x, start_y), (end_x, end_y)]
        p0 = [start_x, start_y]
        p3 = [end_x, end_y]
        connect_line = bezier.generate_bezier3(p0, p3, direction=0)
        (line_x, line_y) = zip(*connect_line)

        ax.add_line(lines.Line2D(line_x, line_y, linewidth=1, color='red'))
        # draw end
        child_salesman = new_h.get_emp_list().get(child_emp_no, None)
        if not child_salesman:
            raise ValueError("Can't child salesman in draw_line()")

        draw_line(child_emp_no, child_salesman, child_rec, new_h, position, fig, ax)

    return


def main():
    # new_h = build_hierarchy_from_sample()
    # new_h = hierarchy.build_hierarchy_from_csv('../Sample/FY16Q3/FY16Q3-Hierarchy.csv')

    # width, depth = new_h.get_depth_width()
    # print("Width:%d, \tDepth:%d\n" % (width, depth))

    test_str1 = r"/Users/desheng/builds/commission-analytics/Sample/FY16Q3"

    ca_session = casession.CASession(test_str1)
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
    ca_utility.summary_filtered_pivot_SFDC(ca_session)
    ca_utility.merge_SFDC_summary_with_manager(ca_session)

    # position = ca_session.get_hierarchy().generate_position()
    # print(position)
    #illustrate(ca_session.get_hierarchy(), position)


if __name__ == "__main__":
    main()
