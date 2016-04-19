from actionSchema import ActionSchema
from causalLink import CausalLink
from utilities import MOVE, PUSH, PULL
from utilities import AGENT_AT, BOX_AT, FREE
from utilities import ADD, DEL
from utilities import calculate_next_position, create_literal_dict

class PartialOrderPlanner:

    def __init__(self, initial_state, goal_state):
        initial_plan = PartialPlan(initial_state, goal_state)
        self.plans = [ initial_plan ]


    def create(self):
        """ Construct partial plan """
        while self.have_plans():
            plan = get_best_plan()
            while plan.has_open_preconditions():
                # first open precondition
                open_node = plan.find_node_with_open_precondition()
                to_be_achieved = open_node.find_open_preconditions()[0]

                # check if we have node in plan that achieves precondition
                achieving_node = plan.find_achiever(open_node, to_be_achieved)
                if achieving_node is not None:
                    open_node.add_parent(achieving_node)
                    continue
                # otherwise, find action that fulfils precondition
                possible_actions = find_action_from_precondition(to_be_achieved)

                # update plan with new action


            print("##")
        print("####")

    def have_plans(self):
        return len(self.plans) > 0


    def get_best_plan(self):
        """ Return best plan first 
        
        TODO: Fix this
        """
        return self.plans[0]


    def find_action_from_precondition(precondition):
        """ Find possible and achievable actions that fulfils precondition """
        possible_actions = []

        # for each possible action
        # go through each possible permutation
        # check if it is achievable and add it to possible actions

        # will only consider add lists (the first element of the tuples)
        if precondition in [ atom['literal'] for atom in ActionSchema.move_effects()[0] ]:
            possible_actions.append(MOVE)
        if precondition in [ atom['literal'] for atom in ActionSchema.push_effects()[0] ]:
            possible_actions.append(PUSH)
        if precondition in [ atom['literal'] for atom in ActionSchema.pull_effects()[0] ]:
            possible_actions.append(PULL)

        return possible_actions

    def update_open_preconditions_from_action(action):
        """ Update open preconditions with action's preconditions that must be fulfilled """


class PartialPlan:
    
    def __init__(self, initial_state, goal_state):
        # create initial nodes
        start  = CausalLink("Start", None, initial_state=[initial_state])
        finish = CausalLink("Finish", None, open_preconditions=[goal_state])
        self.plan = [ start, finish ]


    def add(self, atom, dependent):
        action = CausalLink(atom['literal'], atom['arguments'], dependent
        self.plan.append(action)


    def has_open_preconditions(self):
        """ Does the current plan have open preconditions? """
        for node in self.plan:
            if node.has_open_precondition:
                return True
        return False


    def find_node_with_open_precondition(self):
        """ Find node with open precondition """
        for node in self.plan:
            if node.has_open_precondition:
                return node


    def find_achiever(self, dependent, precondition):
        """ Attempt to find node already in plan that achieves precondition """
        for node in self.plan:
            # cannot achieve precondition by myself
            if node is dependent:
                continue
            x = node.list_action_effects()
            print("comparing {0} with {1}".format(precondition, x))
            for p in x:
                if precondition == p:
                    return node

        return None


    def print(self):
        for node in self.plan:
            node.print()

