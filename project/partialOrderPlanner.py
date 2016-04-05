from actionSchema import ActionSchema
from causalLink import CausalLink
from utilities import MOVE, PUSH, PULL
from utilities import AGENT_AT, BOX_AT, FREE
from utilities import ADD, DEL
from utilities import calculate_next_position, create_literal_dict, create_action_dict

import copy

class PartialOrderPlanner:

    def __init__(self, initial_state, goal_state):
        initial_plan = PartialPlan(initial_state, goal_state)
        self.plans = [ initial_plan ]


    def create(self):
        """ Construct partial plan """
        plan = self.get_best_plan()
        while plan and plan.has_open_preconditions() or plan.start_has_no_children():
            # TODO is this exhaustive?
            # if plan has no open preconditions and it is not connected tot start then it is invalid
            if plan.start_has_no_children() and not plan.has_open_preconditions():
                print("-- plan was incomplete")
                plan = self.get_best_plan()
                continue

            new_plans = self.step(plan)

            # TODO: validate if any conflicts arise
            self.plans += new_plans

            # TODO topologically sort plan

            print("PLANS ", len(self.plans))
            # next plan
            plan = self.get_best_plan()
        # TODO return best plan
        return plan

    def step(self, plan):
        #while True:
        # first open precondition
        node_idx, open_node, to_be_achieved = plan.get_open_precondition()
        print("++", to_be_achieved, "for", open_node.action)

        # check if we have node in plan that achieves precondition
        achiever_idx, achieving_node = plan.find_achiever(open_node, to_be_achieved)

        plans = []
        if achieving_node is not None:
            #print("FOUND ACHIEVING NODE: {0}".format(achieving_node.action))
            # add parent and child
            new_plan = copy.deepcopy(plan)
            achiever = copy.deepcopy(achieving_node)
            dependent = copy.deepcopy(open_node)
            new_plan.connect_achiever(achiever, dependent, achiever_idx, node_idx)
            # must not have loops
            loop = False
            for p in achiever.parents:
                for c in achiever.parents:
                    if p.action == c.action and p.arguments == c.arguments:
                        loop = True
            if not loop:
                plans.append(new_plan)
        else:
            #print("SEARCHING FOR APPLICABLE ACTIONS TO FULFIL PRECONDITION")
            # otherwise, find action that fulfils precondition
            possible_actions = find_action_from_precondition(to_be_achieved)
            # if list is empty we simply continue to next plan and discard current
            #print("POSSIBLE ACTIONS: {0}".format(possible_actions))
            #print("{0} POSSIBLE ACTIONS FOR {1}({2}) {3}".format(len(possible_actions), to_be_achieved['literal'], to_be_achieved['arguments'], possible_actions))
            for action in possible_actions:
                dependent = copy.deepcopy(open_node)
                # TODO: this could probably be done more efficiently instead of copying
                # create new copy of plan
                #print("COPYING CURRENT PLAN")
                new_plan = copy.deepcopy(plan)
                #print("ADDING {0} to {1}".format(action, open_node.action))
                new_plan.add(action, dependent, node_idx)
                plans.append(new_plan)
        return plans


    def have_plans(self):
        return len(self.plans) > 0


    def get_best_plan(self):
        """ Return best plan first

        TODO: Fix this
        """
        return self.plans.pop()


class PartialPlan:

    def __init__(self, initial_state, goal_state):
        # create initial nodes
        start  = CausalLink("Start", None, initial_state=initial_state)
        finish = CausalLink("Finish", None, open_preconditions=goal_state)
        # do not change order of these two
        self.plan = [ start, finish ]


    def introduced_conflicts(self, node):
        """ check if new node has introduced any conflicts """
        delete_list = node.list_action_effects(add_only=False, del_only=True)

        for child in node.children:
            while child.children and len(child.children) > 0:


    def start_has_no_children(self):
        return len(self.plan[0].children) == 0


    def connect_achiever(self, achiever, dependent, a_idx, d_idx):
        """ Connect achieving node to a dependent node and update plan with updated nodes """
        dependent.add_parent(achiever)
        achiever.add_child(dependent)

        self.plan[d_idx] = dependent
        self.plan[a_idx] = achiever
        #print("ADDED ACHIEVER {0} to {1}".format(achiever.action, dependent.action))
        #print("OPEN PRECOND: ", dependent.open_preconditions)


    def add(self, action, dependent, d_idx):
        """ Create a causal link and connect it to dependent node and add to plan """
        #print("CONSTRUCTING NEW NODE")
        achieving_node = CausalLink(action['action'], action['arguments'])
        #print("ADDING PARENT")
        dependent.add_parent(achieving_node)
        #print("ADDING CHILD")
        achieving_node.add_child(dependent)

        #print("ADDING NODE TO PLAN")
        self.plan.append(achieving_node)

        self.plan[d_idx] = dependent


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
        for idx, node in enumerate(self.plan):
            # cannot achieve precondition by myself
            if node is dependent:
                continue

            x = node.list_action_effects()
            for p in x:
                if precondition == p:
                    return idx, node
        return None, None


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
    plan = PartialPlan(initial_state, goal_state)

    #p1 = planner.step(plan)
    #print("# FIRST ROUND")
    #p1[0].print()
    #print()

    #p2 = planner.step(p1[0])
    #print("# SECOND ROUND")
    #for p in p2:
    #    p.print()
    #    print()

    #p3 = planner.step(p2[0])
    #print("# THIRD ROUND")
    #for p in p3:
    #    p.print()
    #    print()

    #p4 = planner.step(p3[0])
    #print("# FOURTH ROUND")
    #for p in p4:
    #    p.print()
    #    print()

    p = planner.create()
    print("## PRINTING PLAN ##")
    # TODO nodes do not have correct parents and children
    p.print()

