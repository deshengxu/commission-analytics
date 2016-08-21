import operator

'''
provide algorithem for different allocation strategy
'''


def verylow_cost_negative(existing_dict, rest, total):
    sorted_x = sorted(existing_dict.items(), key=operator.itemgetter(1))
    # print(sorted_x)
    allocated = [0.0] * total

    if total == 1:
        allocated[0] += rest
        new_dict = {}
        new_dict[sorted_x[0][0]] = allocated[0]
        return new_dict

    current_rest = rest
    index = total - 1
    while index > 0 and current_rest < -0.00001:
        gap = sorted_x[index - 1][1] - (sorted_x[total - 1][1] + allocated[total - 1])

        if gap * float(total - index) > current_rest:
            for x_index in range(index, total):
                allocated[x_index] += gap
            current_rest -= gap * float(total - index)
        else:
            gap = current_rest / (float(total - index))
            for x_index in range(index, total):
                allocated[x_index] += gap
            current_rest = 0.0
        index -= 1
    if current_rest < 0.00001:
        gap = current_rest / (float(total))
        for x_index in range(total):
            allocated[x_index] += gap

    new_dict = {}
    for x_index in range(total):
        new_dict[sorted_x[x_index][0]] = allocated[x_index]

    return new_dict


def verylow_cost_positive(existing_dict, rest, total):
    sorted_x = sorted(existing_dict.items(), key=operator.itemgetter(1))
    allocated = [0.0] * total

    if total == 1:
        allocated[0] += rest
        new_dict = {}
        new_dict[sorted_x[0][0]] = allocated[0]
        return new_dict

    current_rest = rest
    index = 1
    while index < total and current_rest > 0.00001:
        gap = sorted_x[index][1] - (sorted_x[0][1] + allocated[0])

        if gap * float(index) <= current_rest:
            for x_index in range(index):
                allocated[x_index] += gap
            current_rest -= gap * float(index)
        else:
            gap = current_rest / (float(index))
            for x_index in range(index):
                allocated[x_index] += gap
            current_rest = 0.0
        index += 1
    if current_rest > 0.00001:
        gap = current_rest / (float(total))
        for x_index in range(total):
            allocated[x_index] += gap

    new_dict = {}
    for x_index in range(total):
        new_dict[sorted_x[x_index][0]] = allocated[x_index]

    return new_dict


def verylow_cost(existing_dict, rest):
    '''
    allocate rest numbers to all salesman from low to high
    :param existing_dict: it's a dictionary { salesID: current_number, }, assume not None or empty
    :param rest: it's a floating number
    :return: a modified dict {salesID: modified number}
    '''
    if not existing_dict:
        raise ValueError("Input Dict should not be empty in minimal_cost()!")

    total = len(existing_dict)
    if total == 0:
        raise ValueError("Input Dict doesn't have any data in it in minimal_cost()!")

    if rest > 0.0:
        return verylow_cost_positive(existing_dict, rest, total)
    else:
        return verylow_cost_negative(existing_dict, rest, total)


def lowest_cost(existing_dict, rest):
    '''
    try to average everybody in order to get a flat and lowest cost.
    :param existing_dict:
    :param rest:
    :return:
    '''
    if not existing_dict:
        raise ValueError("Input Dict should not be empty in lowest_cost()!")

    total = len(existing_dict)
    if total == 0:
        raise ValueError("Input Dict doesn't have any data in it in lowest_cost()!")

    sorted_x = sorted(existing_dict.items(), key=operator.itemgetter(1))
    allocated = [0.0] * total

    if total == 1:
        allocated[0] += rest
        new_dict = {}
        new_dict[sorted_x[0][0]] = allocated[0]
        return new_dict

    summary = 0.0
    for index in range(total):
        summary += sorted_x[index][1]

    average = (summary + rest) / float(total)
    new_dict = {}
    for index in range(total):
        allocated[index] = average - sorted_x[index][1]
        new_dict[sorted_x[index][0]] = allocated[index]

    return new_dict


def regular_cost(existing_dict, rest):
    if not existing_dict:
        raise ValueError("Input Dict should not be empty in regular_cost()!")

    total = len(existing_dict)
    if total == 0:
        raise ValueError("Input Dict doesn't have any data in it in regular_cost()!")

    sorted_x = sorted(existing_dict.items(), key=operator.itemgetter(1))
    allocated = [0.0] * total

    if total == 1:
        allocated[0] += rest
        new_dict = {}
        new_dict[sorted_x[0][0]] = allocated[0]
        return new_dict

    summary = 0.0
    for index in range(total):
        summary += sorted_x[index][1]

    new_dict = {}
    if summary < 0.00001:
        for index in range(total):
            allocated[index] = (summary + rest) / (float(total))
            new_dict[sorted_x[index][0]] = allocated[index]
    else:
        for index in range(total):
            allocated[index] = rest * sorted_x[index][1] / summary
            new_dict[sorted_x[index][0]] = allocated[index]

    return new_dict

def highest_cost(existing_dict, rest):
    if not existing_dict:
        raise ValueError("Input Dict should not be empty in highest_cost()!")

    total = len(existing_dict)
    if total == 0:
        raise ValueError("Input Dict doesn't have any data in it in highest_cost()!")

    sorted_x = sorted(existing_dict.items(), key=operator.itemgetter(1))
    allocated = [0.0] * total

    if total == 1:
        allocated[0] += rest
        new_dict = {}
        new_dict[sorted_x[0][0]] = allocated[0]
        return new_dict

    if rest >= 0:
        allocated[total - 1] = rest
    else:
        current_rest = rest
        index = 0
        while current_rest < -0.00001 and index < total:
            if abs(current_rest) < sorted_x[index][1]:
                allocated[index] = current_rest
                current_rest = 0.0
            else:
                allocated[index] = -1.0 * sorted_x[index][1]
                current_rest += sorted_x[index][1]
            index += 1

        if current_rest < -0.00001:
            ''' has to average in order to get highest for negative total'''
            summary = 0.0
            for index in range(total):
                summary += sorted_x[index][1]

            average = (rest + summary) / (float(total))
            for index in range(total):
                allocated[index] = average - sorted_x[index][1]
                # allocated[index] += current_rest/(float(total))

    new_dict = {}
    for index in range(total):
        new_dict[sorted_x[index][0]] = allocated[index]

    return new_dict


def regular_bestguess(nonbigdeal_dict, rest, bigdeal_dict, plan_number, ca_session):
    if not bigdeal_dict:
        raise ValueError("Big Deal data should be included in best guess!")

    total_sales = len(nonbigdeal_dict)
    if total_sales == 0:
        raise ValueError("nonbigdeal_dict doesn't have any sales data in it in regular_bestguess()!")

    total_dict = {}
    for key, value in nonbigdeal_dict.iteritems():
        bigdeal_value = bigdeal_dict.get(key, 0)
        total_dict[key] = value + bigdeal_value


    sorted_x = sorted(total_dict.items(), key=operator.itemgetter(1))
    allocated = [0.0] * total_sales

    new_dict = {}
    if total_sales == 1:
        allocated[0] += rest
        new_dict[sorted_x[0][0]] = allocated[0]
        # return new_dict
    elif total_sales == 2:
        # when only two sales, then:
        # lowest sales non big deal number will be cut to 0
        # rest + lowest non big deal number will be assigned to highest person.
        allocated[0] = (-1) * (nonbigdeal_dict.get(sorted_x[0][0], 0.0))
        allocated[1] = rest - allocated[0]
        new_dict[sorted_x[0][0]] = allocated[0]
        new_dict[sorted_x[1][0]] = allocated[1]
    elif total_sales == 3:
        # when only 3 sales, then:
        # lowest sales non big deal number will be cut to 0
        # rest + lowest non big deal number will be assigned to highest person.
        # middle person will be kept
        allocated[0] = (-1) * (nonbigdeal_dict.get(sorted_x[0][0], 0.0))
        allocated[2] = rest - allocated[0]
        new_dict[sorted_x[0][0]] = allocated[0]
        new_dict[sorted_x[1][0]] = allocated[1]  # 0.0
        new_dict[sorted_x[2][0]] = allocated[2]
    elif total_sales == 4:
        # when only 4 sales, then:
        # 2 lowest sales non big deal number will be cut to 0
        # rest + 2 lowest non big deal number will be assigned to highest person.
        # middle person will be kept
        allocated[0] = (-1) * (nonbigdeal_dict.get(sorted_x[0][0], 0.0))
        allocated[1] = (-1) * (nonbigdeal_dict.get(sorted_x[1][0], 0.0))
        allocated[3] = rest - allocated[0] - allocated[1]
        new_dict[sorted_x[0][0]] = allocated[0]
        new_dict[sorted_x[1][0]] = allocated[1]
        new_dict[sorted_x[2][0]] = allocated[2]  # 0.0
        new_dict[sorted_x[3][0]] = allocated[3]
    elif total_sales == 5:
        # when only 5 sales, then:
        # 3 lowest sales non big deal number will be cut to 0
        # rest + 3 lowest non big deal number will be assigned to highest person.
        # middle person will be kept
        allocated[0] = (-1) * (nonbigdeal_dict.get(sorted_x[0][0], 0.0))
        allocated[1] = (-1) * (nonbigdeal_dict.get(sorted_x[1][0], 0.0))
        allocated[2] = (-1) * (nonbigdeal_dict.get(sorted_x[2][0], 0.0))

        allocated[4] = rest - allocated[0] - allocated[1] - allocated[2]
        new_dict[sorted_x[0][0]] = allocated[0]
        new_dict[sorted_x[1][0]] = allocated[1]
        new_dict[sorted_x[2][0]] = allocated[2]  # 0.0
        new_dict[sorted_x[3][0]] = allocated[3]  # 0.0
        new_dict[sorted_x[4][0]] = allocated[4]
    elif 15 >= total_sales > 5:
        p_sales, p_booking = ca_session.get_band_way1()

        new_dict = allocate_by_segment(sorted_x, p_sales, p_booking, total_sales,
                                       plan_number)

    else:
        p_sales, p_booking = ca_session.get_band_way2()

        new_dict = allocate_by_segment(sorted_x, p_sales, p_booking, total_sales,
                                       plan_number)

    return new_dict


def allocate_by_segment(sorted_dict, p_sales, p_booking, total_sales, plan_number):
    segments = len(p_sales)  # how many segments way1 now is 3, way2 now is 4

    range_segments = [0] * (segments + 1)
    for index in range(1, segments + 1):
        range_segments[index] = range_segments[index - 1] + int(round(p_sales[index - 1] * total_sales, 0))

    # avoid round error
    round_error = range_segments[segments] - total_sales
    if round_error > 0:
        for index in range(1, segments + 1):
            range_segments[index] -= round_error

    allocated = [0.0] * total_sales
    for seg_index in range(segments):
        sub_total = 0.0
        for index in range(range_segments[seg_index], range_segments[seg_index + 1]):
            # assume all SFDC record is positive value
            if sorted_dict[index][1] < 0.0:
                raise ValueError("%d has negative SFDC value:%0.2f" % (sorted_dict[index][0], sorted_dict[index][1]))
            sub_total += sorted_dict[index][1]
        gap = plan_number * p_booking[seg_index] - sub_total

        # assume sfdc numbers are not negative
        segment_sales = range_segments[seg_index + 1] - range_segments[seg_index]
        if segment_sales <= 0:
            raise ValueError("Sales segment at:%d has %d sales!" % (seg_index + 1, segment_sales))

        if sub_total < 0.001:
            for index in range(range_segments[seg_index], range_segments[seg_index + 1]):
                allocated[index] = gap / float(segment_sales)
        else:
            for index in range(range_segments[seg_index], range_segments[seg_index + 1]):
                allocated[index] = gap * sorted_dict[index][1] / sub_total

    new_dict = {}
    for index in range(total_sales):
        new_dict[sorted_dict[index][0]] = allocated[index]

    return new_dict


def allocation(existing_dic, rest, key, bigdeal_dict=None, plan_number=0.0, ca_session=None):
    if key.upper() == "VERYLOW":
        return verylow_cost(existing_dic, rest)
    elif key.upper() == "LOWEST":
        return lowest_cost(existing_dic, rest)
    elif key.upper() == "HIGHEST":
        return highest_cost(existing_dic, rest)
    elif key.upper() == "REGULAR":
        return regular_cost(existing_dic, rest)
    elif key.upper() == "BESTGUESS":
        return regular_bestguess(existing_dic, rest, bigdeal_dict, plan_number, ca_session)
    else:
        raise ValueError("A wrong key %s has been provided in allocation()!" % key)


def main():
    dict = {111: 0.00, 222: 10.0, 333: 89.0, 444: 32}
    # dict = {111: 0.00, 222: 0.02, 333: 0.0, 444: 0}
    rest = 100.0
    # dict = {111: 0.01}
    # dict = {}

    # new_dict = verylow_cost(dict, 100.0)
    # new_dict = lowest_cost(dict, -100.0)
    # new_dict = highest_cost(dict, -1000.0)

    new_dict = allocation(dict, rest, "regular")

    print(dict)
    print(new_dict)
    for key, value in dict.iteritems():
        print("Key:%d->%10.2f+%10.2f=%10.2f" % (key, value, new_dict[key], value + new_dict[key]))


if __name__ == "__main__":
    main()
