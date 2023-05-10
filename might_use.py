def return_next_index(current_index, table_shape):
    """

    :param table_shape:
    :param current_index: tuple containing two integer elements.
    :return: tuple containing two integer elements.
    """
    if current_index is None:
        return tuple([0, 0])

    current_index = list(current_index)
    if (current_index[0] == 0) and (current_index[1] % 2 == 0):
        if current_index[1] == table_shape[1] - 1:
            return 'End'
        else:
            current_index[1] += 1
    elif (current_index[1] == 0) and (current_index[0] % 2 == 1):
        if current_index[0] == table_shape[0] - 1:
            return 'End'
        else:
            current_index[0] += 1
    elif (current_index[0] % 2 == 0) and (current_index[0] > current_index[1]):
        current_index[1] += 1
    elif (current_index[0] % 2 == 1) and (current_index[0] >= current_index[1]) and (current_index[1] != 0):
        current_index[1] -= 1
    elif (current_index[1] % 2 == 0) and (current_index[0] <= current_index[1]) and (current_index[1] != 0):
        current_index[0] -= 1
    elif (current_index[1] % 2 == 1) and (current_index[0] < current_index[1]):
        current_index[0] += 1
    else:
        raise Exception('Index out of bounds: current_index = {0}'.format(current_index))

    return tuple(current_index)

########################################################################################################################
