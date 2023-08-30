def find_element_order(cayley_table):
    """

    :return:
    """
    if cayley_table.cayley_table_actions is None:
        raise Exception(
            "Generate Cayley table using self.generateCayleyTable(parameters) before finding element orders.")

    if cayley_table.identity_info is None:
        raise Exception("Find identities using self.checkInverse() before finding element orders.")

    # Check if identity element exists.
    if len(cayley_table.identity_info['identities']) == 0:
        element_order_info = "No identity, therefore cannot calculate element orders."

    element_order_info = {}  # Structure: { a_1 : (order n, order_search), a_2 : (float('inf'), order_search, (cycle_start, cycle_length)) }
    # The maximum order an element can have, if it has a finite order, is the number of elements in the algebra.    # TODO: is this true ?
    max_order = len(cayley_table.cayley_table_actions.index)
    for a in cayley_table.cayley_table_actions.index:
        for e in cayley_table.identity_info['identities']:
            n = 1
            order_search = [a]

            # If an element is an identity element, then it has an order of 1.
            if a == e:
                element_order_info[a] = (n, order_search)
                continue

            a_outcome = a
            while True:
                n += 1

                a_outcome = cayley_table.find_outcome_cayley(left_action=a, right_action=a_outcome)

                # If the element a_outcome is an identity element, then element a has an order of n.
                if a_outcome == e:
                    element_order_info[a] = (n, order_search)
                    order_search.append(a_outcome)
                    break

                # If the element order search for element a returns to an element seen before without reaching an
                # identity, then the search for the order of a has hit a cycle and so a has infinite order.
                if a_outcome in order_search:
                    cycle_start = a_outcome
                    cycle_length = order_search[::-1].index(a_outcome) + 1
                    element_order_info[a] = (float('inf'), order_search, (cycle_start, cycle_length))
                    break

                order_search.append(a_outcome)

                # CHECK.
                if n > max_order:
                    element_order_info[a] = ('$infty', 'max_order')
                    raise Exception(f"Max element order ({max_order}) reached. ({a}, {order_search})")


    return element_order_info