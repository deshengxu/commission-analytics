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


def allocation(existing_dic, rest, key):
    if key.upper() == "VERYLOW":
        return verylow_cost(existing_dic, rest)
    elif key.upper() == "LOWEST":
        return lowest_cost(existing_dic, rest)
    elif key.upper() == "HIGHEST":
        return highest_cost(existing_dic, rest)
    else:
        raise ValueError("A wrong key %s has been provided in allocation()!" % key)


def main():
    dict = {111: 0.01, 222: 10.0, 333: 89.0, 444: 32}
    # dict = {111: 0.01}
    # dict = {}

    new_dict = verylow_cost(dict, 100.0)
    # new_dict = lowest_cost(dict, -100.0)
    # new_dict = highest_cost(dict, -1000.0)

    print(dict)
    print(new_dict)
    for key, value in dict.iteritems():
        print("Key:%d->%10.2f+%10.2f=%10.2f" % (key, value, new_dict[key], value + new_dict[key]))


if __name__ == "__main__":
    main()
