from movable import Agent, Box
from a_star_search_simple import cross_product_heuristic as cross_product
from operator import itemgetter


def object_builder(movable, colors, _class, instance_collection,
        position_collection):
    """ Create box or agent instances.

    Keyword arguments:
    movable -- dict of either boxes or agents {(x,y): 'A'}
    colors -- None or dict of colors {'blue': ['0', 'A']}
    _class -- class' constructor (either Box or Agent)
    instance_collection -- set of Movable instances
    position_collection -- dict defining instance's position
    """
    for cell, obj in movable.items():
        for color, objs in colors.items():
            if obj in objs:
                instance = _class(obj, cell, color)
                instance_collection.add(instance)
                position_collection[cell] = instance
                break

def find_uncolored_objects(colors, boxes, agents):
    """ Return set of uncolored objects """
    b_set, a_set = set(boxes.values()), set(agents.values())
    c_set = set([i for l in colors.values() for i in l])
    # find set differences
    b_uncolored = b_set - c_set
    a_uncolored = a_set - c_set

    return b_uncolored.union(a_uncolored)

def update_colors(colors, uncolored):
    """ Update colors dict with uncolored objects """
    colored = set()
    if 'blue' in colors:
        colored = set(colors['blue'])
    colors['blue'] = list(colored.union(uncolored))

    return colors

def new_cell_from_direction(old_cell, direction):
    """ Calculate new cell from direction """
    (Y,X) = old_cell
    if direction == 'N':
        return (Y-1,X)
    elif direction == 'E':
        return (Y,X+1)
    elif direction == 'W':
        return (Y,X-1)
    elif direction == 'S':
        return (Y+1,X)

class SimpleGrid:

    def __init__(self, walls, goals, boxes, agents, colors, free):
        """ Simple grid representation.

        Keyword arguments:
        walls -- set of tuples (representing cells/positions)
        goals -- dict of {(x,y): 'a', ..}
        boxes -- dict of {(x,y): 'A', ..}
        agents -- dict of {(x,y): '0', ..}
        colors -- dict of {'green': ['0', 'A', 'a'], ..}
            If agent or box is not in colors, they will default to 'blue'
        free -- set of tuples (representing cells/positions)
        """
        uncolored = find_uncolored_objects(colors, boxes, agents)
        if len(uncolored) > 0:
            colors = update_colors(colors, uncolored)

        self.walls = walls      # {(0,0), (1,0), ..}
        self.goals = goals      # {(x,y): 'a', ..}

        self.colors = colors # {'green': ['0', 'A', 'a'], ..}
        self.free = free

        # sets of instances of movable objects
        self.boxes, self.agents = set(), set()
        # dicts of instances' positions { cell: instance }
        self.box_position, self.agent_position = dict(), dict()
        # populate ojects
        self.build_boxes(boxes, colors)   # {(x,y): 'A', ..}
        self.build_agents(agents, colors) # {(x,y): '0', ..}

        self.agent_info = dict() # which boxes can agent move (dict of sets)
        self.populate_agent_info(agents, boxes, colors)

        # NOTE: there must be a better way to check the entire grid?
        self.complete_grid = ( walls.union(free).union(set(goals))
            .union(set(boxes)).union(set(agents)) )

        self.unpassable = walls.union(set(boxes)).union(set(agents))

    def build_boxes(self, boxes, colors):
        object_builder(boxes, colors, Box, self.boxes, self.box_position)

    def build_agents(self, agents, colors):
        object_builder(agents, colors, Agent, self.agents, self.agent_position)

    def populate_agent_info(self, agents, boxes, colors):
        """ Find agents that can move boxes.
        Creates dict of agents and a set of boxes they can move.
        """
        self.agent_info = {agent: set() for agent in self.agents}
        boxes = set(boxes.values())
        for box in boxes:
            for agent in self.agent_info:
                for objs in colors.values():
                    if agent.name in objs and box in objs:
                        self.agent_info[agent].add(box)

    def in_bounds(self, cell):
        return cell in self.complete_grid

    def passable(self, cell):
        return cell not in self.unpassable

    def neighbours(self, cell, with_box=False, with_agent=False, diagonals=False):
        """ find neighbours of cell

        Keyword arguments:
        cell -- cell to find neighbours of
        with_box -- (optional) whether or not to include boxes
        with_agent -- (optional) whether or not to include agents
        """
        (x,y) = cell
        results = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        if diagonals : results += [(x+1,y+1),(x-1,y+1),(x+1,y-1),(x-1,y-1)]

        results = [r for r in results if self.in_bounds(r)]

        box_pos = ( [c for c in results if c in self.box_position]
                if with_box else [] )
        agent_pos = ( [c for c in results if c in self.agent_position]
                if with_agent else [] )
        results = [r for r in results if self.passable(r)]
        results += box_pos + agent_pos

        return results

    def swapable(self, box_cell, agent_cell, next_cell, agent_origin):
        """ Given box and agent position and we want to move towards next_cell,
        is it possible to perform a Pull and Push?

        Return first cell where the agent can Pull towards and Push from.
        If no swap is possible, return None.
        If box and agent are not neighbouring cells then return None.
        If agent and next cell are not neighbouring cells then return None.

        Keyword arguments:
        box_cell -- box's position
        agent_cell -- agent's position
        next_cell -- next cell to move towards
        agent_origin -- where did agent originate from
            grid thinks agent's start position is blocked.
        """
        # if box and agent or agent and next are not neighbours, return
        if cross_product(box_cell, agent_cell) is not 1: return None
        if cross_product(agent_cell, next_cell) is not 1: return None

        results = self.neighbours(agent_cell)
        if agent_cell != agent_origin and cross_product(agent_cell,
                agent_origin) is 1:
            results = [agent_origin] + results
        results = [c for c in results if c != box_cell and c != next_cell]
        return results[0] if len(results) > 0 else None

    def get_free_from_list(self, path):
        """ Return set difference of free cells and cells in path """
        return self.free - set(path)

    def get_goal_priorities(self, open_goals):
        """ Sort open goals to avoid blockage """

        cell_refs = sorted(list(open_goals), key=itemgetter(1))
        cell_refs = sorted(list(cell_refs), key=itemgetter(0))
        """VERTICAL SORT??"""
        g_rows = [0] * len(open_goals)
        g_matrix = [cell_refs] + [g_rows[:] for _ in range(len(open_goals))]

        for row in range(len(g_matrix)):
            for column,cell in enumerate(g_matrix[row]):
                if row == 0:
                    continue;

                g_cell = g_matrix[0][column]
                n_cells = self.neighbours(g_cell,diagonals=True, with_agent=True)
                prev_prev_score = None

                if column>0 :
                    prev_prev_score= g_matrix[row-1][column-1]

                max_score = max(g_matrix[row-1])

                if row == 1:
                    start_score = 0
                    for n_cell in n_cells:
                        if n_cell in self.goals:
                            start_score += 1
                        elif n_cell in self.free:
                            start_score += 2

                    g_matrix[row][column] = start_score

                elif column<len(g_matrix[row])-1:
                    prev_score = g_matrix[row-1][column]
                    prev_next_score = g_matrix[row-1][column+1]
                    if prev_score == prev_next_score and g_matrix[0][column+1] in n_cells:
                        if prev_prev_score and prev_prev_score < prev_score:
                            g_matrix[row][column] = prev_score
                        else:
                            g_matrix[row][column] = prev_score+1
                    elif prev_prev_score and prev_prev_score == prev_score and g_matrix[0][column-1] in n_cells:
                        if prev_score > prev_next_score:
                            g_matrix[row][column] = prev_score
                        else:
                            g_matrix[row][column] = prev_score+1
                    elif prev_score == max_score:
                        g_matrix[row][column] = prev_score+1
                    else:
                        g_matrix[row][column] = prev_score
                else:
                    prev_score = g_matrix[row-1][column]
                    if prev_score == max_score:
                        g_matrix[row][column] = prev_score+1
                    else:
                        g_matrix[row][column] = prev_score

        sorted_goals = list()
        for i, cell in enumerate(g_matrix[0]):
            sorted_goals.append((g_matrix[-1][i], cell, open_goals[cell]))

        sorted_goals = sorted(list(sorted_goals), key=itemgetter(0))
        sorted_goals = [(i[1], i[2]) for i in sorted_goals]

        return sorted_goals

    def get_open_goals(self):
        """ find goals that are unsolved and return dict of cell and letter """
        open_goals = dict()
        boxes = {box.position: box.name for box in self.boxes}
        for g_cell, g_letter in self.goals.items():
            if g_cell not in boxes:
                open_goals[g_cell] = g_letter
            elif g_cell in boxes:
                b_letter = boxes[g_cell]
                if b_letter != g_letter.upper():
                    open_goals[g_cell] = g_letter
        return open_goals

    def move(self, agent, step):
        """ Update grid with new info about movable objects.

        Keyword arguments:
        agent - the agent's number
        step - Move(E),... etc.
        """
        # Parsing input
        move_type = step[:4]
        if move_type == 'NoOp': return

        dirs = step[5:-1].split(",")
        first_dir = dirs[0]
        second_dir = dirs[1] if len(dirs) > 1 else None

        # update agent position
        old_pos_agent = agent.position
        new_pos_agent = new_cell_from_direction(old_pos_agent, first_dir)
        agent.move(new_pos_agent)
        del self.agent_position[old_pos_agent]
        self.agent_position[new_pos_agent] = agent

        if move_type == 'Move':
            box = None
            new_free, new_unpassable = old_pos_agent, new_pos_agent
        elif move_type == 'Push':
            old_pos_box = new_pos_agent
            new_pos_box = new_cell_from_direction(old_pos_box, second_dir)
            box = self.box_position[old_pos_box]
            new_free, new_unpassable = old_pos_agent, new_pos_box
        else:
            new_pos_box = old_pos_agent
            old_pos_box = new_cell_from_direction(old_pos_agent, second_dir)
            box = self.box_position[old_pos_box]
            new_free, new_unpassable = old_pos_box, new_pos_agent

        if box is not None:
            box.move(new_pos_box)
            del self.box_position[old_pos_box]
            self.box_position[new_pos_box] = box

        # update grid
        self.free.discard(new_unpassable)
        self.free.add(new_free)
        self.unpassable.discard(new_free)
        self.unpassable.add(new_unpassable)


if __name__ == '__main__':
    walls = {(1,0), (1,1), (1,3), (2,2)}
    free  = {(0,0), (0,1), (0,2), (0,3), (1,2)}
    goals = {(1, 10): 'b', (2, 10): 'a'}
    agents = {(1, 1): '0', (2, 1): '1', (3,1): '2'}
    boxes = {(1, 9): 'A', (2, 9): 'B', (9,9): 'C', (10,10): 'C'}
    colors = {'green': ['A','0'], 'red' : ['B', '1'], 'blue': ['3']}
    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)

    print(grid.agents)
    print(grid.boxes)
    print(grid.colors)

    box_cell, agent_cell, next_cell = (0,1), (0,2), (0,3)
    result = grid.swapable(box_cell, agent_cell, next_cell)
    print(result)

    print(grid.agent_position)
    print(grid.box_position)
    grid.move((1,9), (1,10))
    print(grid.box_position)
