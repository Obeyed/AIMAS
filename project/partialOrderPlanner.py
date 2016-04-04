from actionSchema import ActionSchema
from causalLink import CausalLink
from utilities import MOVE, PUSH, PULL
from utilities import AGENT_AT, BOX_AT, FREE
from utilities import ADD, DEL
from utilities import calculate_next_position, create_literal_dict

import copy

class PartialOrderPlanner:

    def __init__(self, initial_state, goal_state):
        initial_plan = PartialPlan(initial_state, goal_state)
        self.plans = [ initial_plan ]


    def create(self):
        """ Construct partial plan """
        plan = self.get_best_plan()
        while plan and plan.has_open_preconditions():
            # first open precondition
            node_idx, open_node, to_be_achieved = plan.get_open_precondition()

            # check if we have node in plan that achieves precondition
            achieving_node = plan.find_achiever(open_node, to_be_achieved)
            if achieving_node is not None:
                #print("FOUND ACHIEVING NODE: {0}".format(achieving_node))
                # add parent and child
                open_node.add_parent(achieving_node)
                achieving_node.add_child(open_node)
                # TODO validate if any conflicts arise
                self.plans.append(plan)
            else:
                #print("SEARCHING FOR APPLICABLE ACTIONS TO FULFIL PRECONDITION")
                # otherwise, find action that fulfils precondition
                possible_actions = find_action_from_precondition(to_be_achieved)
                # if list is empty we simply continue to next plan and discard current
                #print("POSSIBLE ACTIONS: {0}".format(possible_actions))
                for action in possible_actions:
                    # TODO: this could probably be done more efficiently instead of copying
                    # create new copy of plan
                    #print("COPYING CURRENT PLAN")
                    new_plan = copy.deepcopy(plan)
                    #print("ADDING {0} to {1}".format(action, open_node.action))
                    new_plan.add(action, open_node, node_idx)
                    # TODO: validate if any conflicts arise
                    self.plans.append(new_plan)
            # pick best plan to continue
            plan = self.get_best_plan()
            # TODO topologically sort plan
        # TODO return best plan
        return plan


    def have_plans(self):
        return len(self.plans) > 0


    def get_best_plan(self):
        """ Return best plan first 
        
        TODO: Fix this
        """
        return self.plans.pop(0)


class PartialPlan:
    
    def __init__(self, initial_state, goal_state):
        # create initial nodes
        start  = CausalLink("Start", None, initial_state=initial_state)
        finish = CausalLink("Finish", None, open_preconditions=goal_state)
        self.plan = [ start, finish ]


    def add(self, action, dependent, dependent_idx=None):
        """ Create a causal link and connect it to dependent node and add to plan """
        #print("CONSTRUCTING NEW NODE")
        achieving_node = CausalLink(action['action'], action['arguments'])
        #print("ADDING PARENT")
        dependent.add_parent(achieving_node)
        #print("ADDING CHILD")
        achieving_node.add_child(dependent)

        #print("ADDING NODE TO PLAN")
        self.plan.append(achieving_node)

        if dependent_idx is not None:
            self.plan[dependent_idx] = dependent


    def has_open_preconditions(self):
        """ Does the current plan have open preconditions? """
        #print("SEARCHING FOR OPEN PRECONDITIONS")
        for node in self.plan:
            #node.print(False)
            if node.has_open_precondition():
                return True
        return False

    def get_open_precondition(self):
        node_idx, node = self.find_node_with_open_precondition()
        #print("## NODE WITH OPEN PRECONDITION: {0}".format(node.action))
        open_precond = node.find_open_preconditions()[0]
        #print("## TO BE ACHIEVED: {0}".format(open_precond))
        return node_idx, node, open_precond


    def find_node_with_open_precondition(self):
        """ Find node with open precondition """
        for idx, node in enumerate(self.plan):
            if node.has_open_precondition():
                return idx, node


    def find_achiever(self, dependent, precondition):
        """ Attempt to find node already in plan that achieves precondition """
        for node in self.plan:
            # cannot achieve precondition by myself
            if node is dependent:
                continue
            x = node.list_action_effects()
            for p in x:
                if precondition == p:
                    return node
        return None


    def print(self):
        for node in self.plan:
            node.print(False)



def find_action_from_precondition(precondition):
    """ Find possible and achievable actions that fulfils precondition """
    wanted_actions = []
    literal = precondition['literal']

    # will only consider add lists (the first element of the tuples)
    # for each possible action
    if literal in [ atom['literal'] for atom in ActionSchema.move_effects()[0] ]:
        wanted_actions.append(MOVE)
    if literal in [ atom['literal'] for atom in ActionSchema.push_effects()[0] ]:
        wanted_actions.append(PUSH)
    if literal in [ atom['literal'] for atom in ActionSchema.pull_effects()[0] ]:
        wanted_actions.append(PULL)

    # go through each possible permutation
    # check if it is achievable and add it to possible actions
    possible_actions = ActionSchema.find_applicable_actions(wanted_actions, precondition)

    return possible_actions


if __name__ == '__main__':
    from agent import Agent
    from utilities import create_literal_dict

    import builtins
    #  ++++++
    #  +aA 0+
    #  ++++++
    builtins.walls = { (0,0): "+", (0,1): "+", (0,2): "+", (0,3): "+", (0,4): "+", (0,5): "+", 
                       (1,0): "+",                                                 (1,5): "+", 
                       (2,0): "+", (2,1): "+", (2,2): "+", (2,3): "+", (2,4): "+", (2,5): "+" }
    builtins.goals = { (1,1): 'a' }
    builtins.boxes = { (1,2): 'A' }
    agent = Agent('mr. robot', (1,4))

    print(agent.position, agent)
    print(walls)
    print(boxes)
    print(goals)

    initial_state = [ create_literal_dict(AGENT_AT, [(1,4)]),
                      create_literal_dict(BOX_AT, [(1,2)]),
                      create_literal_dict(FREE, [(1,3)]) ]
    goal_state = [ create_literal_dict(BOX_AT, [(1,1)]) ]

    planner = PartialOrderPlanner(initial_state, goal_state)

    p = planner.create()
    print("## PRINTING PLAN ##")
    # TODO nodes do not have correct parents and children
    p.print()

