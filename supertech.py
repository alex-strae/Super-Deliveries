# Code by Alex Stråe, Sweden, AKA Dr-Wojtek @ GitHub

from math import inf
from heapq import heappop, heappush

class Supertrip:
    def __init__(self, start_pos, map, all_delivery_orders):
        self.start = start_pos
        self.map = map
        self.ADO = all_delivery_orders

        for address in map:
            self.sort_direction(self.start, address)

    def sort_direction(self, start, address):
        if address == start:
            address.direction = 'A (N)'
        elif address.pos[0] > start.pos[0]:
            if abs(address.pos[0] - start.pos[0]) >= 2:
                if address.pos[1] < start.pos[1]:
                    address.direction = 'B (NE)'
                elif address.pos[1] == start.pos[1]:
                    address.direction = 'C (E)'
                elif abs(address.pos[1] - start.pos[1]) == 1:
                    address.direction = 'C (E)'
                elif abs(address.pos[1] - start.pos[1]) == 2:
                    address.direction = 'D (SE)'
            elif abs(address.pos[0] - start.pos[0]) >= 1:
                if address.pos[1] < start.pos[1]:
                    address.direction = 'A (N)'
                elif address.pos[1] == start.pos[1]:
                    address.direction = 'C (E)'
                else:
                    address.direction = 'E (S)'
            else:
                if address.pos[1] > start.pos[1]:
                    address.direction = 'E (S)'
                else:
                    address.direction = 'A (N)'
        else:
            if abs(address.pos[0] - start.pos[0]) >= 2:
                if address.pos[1] < start.pos[1]:
                    address.direction = 'H (NW)'
                elif address.pos[1] == start.pos[1]:
                    address.direction = 'G (W)'
                else:
                    if abs(address.pos[1] - start.pos[1]) == 1:
                        address.direction = 'G (W)'
                    else:
                        address.direction = 'F (SW)'
            else:
                if address.pos[1] > start.pos[1]:
                    address.direction = 'E (S)'
                elif address.pos[1] == start.pos[1]:
                    address.direction = 'G (W)'
                else:
                    address.direction = 'A (N)'

    # implementation of 'The Knapsack Problem' using dynamic programming and mods
    def drivers_dynamic_knapsack(self, limiting_factor, limiting_factor_cap):
        ado = self.ADO
        rows = len(ado) + 1
        cols = limiting_factor_cap + 1
        # setup 2d-array to withhold orders. Rows are for orders.
        # Columns are for the limiting factor, most likely weight. One column for each total unit of limiting factor,
        # so a higher cap means more units can be considered (for example, weight).
        matrix = [[] for i in range(rows)]
        for i in range(rows):
            matrix[i] = [-1 for j in range(cols)]
            # populate colums for each order. First row and column are filled of 0, because when running
            # the first round of each item, we always want to include, not exclude.
            for j in range(cols):
                if i == 0 or j == 0:
                    matrix[i][j] = []
                    matrix[i][j].append(0)
                # If current order is within our limiting factor requirement, we might want to include it:
                elif ado[i-1][limiting_factor] <= j:
                    include_order = []
                    exclude_order = []
                    # the core of the algo: Get current order's value and add to it value from earlier most valuable config
                    # that won't make us exceed our limiting factor.
                    # matrix[i-1][j-ado[i-1][limiting_factor]][0] = last row, at column with config with factor = (factor cap - this objects factor)
                    include_order.append(ado[i-1]['value'] + matrix[i-1][j-ado[i-1][limiting_factor]][0])
                    # and get the name so we know where the value comes from! Useless algo if we don't do this.
                    include_order.append(ado[i-1]['name'])
                    # above grabbed the name from current order, but we also need the names from the last most valuable
                    # config if it turns out this is the new most valuable config.
                    if len(matrix[i-1][j-ado[i-1][limiting_factor]]) > 1:
                        for x in range(1, len(matrix[i-1][j-ado[i-1][limiting_factor]])):
                            include_order.append(matrix[i-1][j-ado[i-1][limiting_factor]][x])
                    # and now we look if we already found a combination with this limiting factor worth more:
                    for orders in matrix[i-1][j]:
                        exclude_order.append(orders)
                    matrix[i][j] = []
                    # Which was more valuable, this new combination or the last?:
                    if include_order[0] > exclude_order[0]:
                        for order in include_order:
                            matrix[i][j].append(order)
                    else:
                        for order in exclude_order:
                            matrix[i][j].append(order)
                # And if the object is too heavy, it cannot be included, so we skip it
                # by copying last rows most valuable config.
                else:
                    matrix[i][j] = []
                    for order in matrix[i-1][j]:
                        matrix[i][j].append(order)
        return matrix[rows-1][limiting_factor_cap]

 # RECURSIVE KNAPSACK. OBSOLETE, Intel 8850H CPU could not return objects under 15 sec if +11 objects added
    def drivers_knapsack(self, weight_cap, i):
        ado = self.ADO
        # base condition: no more room left (cap = 0) or i = 0 (no more items to see): return value from this config; 0
        if weight_cap == 0 or i == 0:
            return 0, ""
        # or if weight we're looking at is too heavy, lets skip it and run next round:
        elif ado[i-1].get('weight') > weight_cap:
            return self.drivers_knapsack(weight_cap, i -1)
        # if none of the above, consider adding item by calculating value of doing so:
        else:
            take_item = [0, [""]]
            take_item[0] = ado[i-1].get('value') + self.drivers_knapsack(weight_cap - ado[i-1].get('weight'), i - 1)[0]
            take_item[1] = ado[i-1].get('name') + ', ' + self.drivers_knapsack(weight_cap-ado[i-1].get('weight'), i -1)[1]
            leave_item = [0, [""]]
            leave_item[0] = self.drivers_knapsack(weight_cap, i - 1)[0]
            leave_item[1] = self.drivers_knapsack(weight_cap, i -1)[1]
            if take_item[0] > leave_item[0]:
                return take_item[0], take_item[1]
            else:
                return leave_item[0], leave_item[1]

    # for A *: calculate distance "as the bird flies" from current loc (c) to target (t)
    def heuristic(self, c, t):
        x_dist = abs(c.pos[0] - t.pos[0])
        y_dist = abs(c.pos[0] - t.pos[0])
        return x_dist + y_dist

    # A* search algorithm. s = starting location. t = target location
    def a_star(self, map, s, t):
        paths_and_distances = {}
        # add all addresses in map to dict, with corresponding distance to start loc (which is unknown, therefor inf)
        for address in map:
            paths_and_distances[address] = [inf, [s.name]]
        # distance to start, from start, is zero.
        paths_and_distances[s][0] = 0
        # create heap for calculation, starting with start location
        addresses_to_calculate = [(0, s)]
        while addresses_to_calculate and paths_and_distances[t][0] is inf:
            # get room to calc from heap, which becomes current room, and current distance to there
            c_distance, c_loc = heappop(addresses_to_calculate)
            # get distance to adjacent location (adj)
            for adj, extra_distance in map[c_loc]:
                # and add to it the dist to target, so we know whether we are moving in the right direction
                new_distance = c_distance + extra_distance + self.heuristic(adj, t)
                # This might be part of the final path. We need to know how we got here.
                new_path = paths_and_distances[c_loc][1] + [c_loc.name]
                # If this is the shorter way to target from start loc, update current known distance and path
                if new_distance < paths_and_distances[adj][0]:
                    paths_and_distances[adj][0] = new_distance
                    paths_and_distances[adj][1] = new_path
                    # push new room to calculate onto heap
                    heappush(addresses_to_calculate, (new_distance, adj))

        return t.name, paths_and_distances[t][0], paths_and_distances[t][1]
