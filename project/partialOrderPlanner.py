from actionSchema import action_helpers, find_applicable_actions
from utilities import MOVE, PUSH, PULL
from utilities import PRECONDITIONS, EFFECTS, START, FINISH
from utilities import AGENT_AT, BOX_AT, FREE, ADD, DEL
from utilities import calculate_next_position, create_literal_dict
from utilities import create_action_dict

class Action:

    def __init__(self, action, arguments, preconditions, effects):
        """ Action container for hashing purposes

        action_dict has the following structure
        { 'action': 'Move',
          'arguments': [(1,3), 'W', 'W'],
          'effects': [],
          'preconditions': [] }

        Keyword arguments:
        action -- action's name
        arguments -- list of action's arguments
        preconditions -- list of dict
        effects -- tuple of positive and negative effects
        """
        self.action = action
        self.arguments = arguments or []
        self.preconditions = ( [Precondition(p) for p in preconditions]
            if preconditions is not None else [] )
        self.effects = effects or ([],[])

    def get_formatted_preconditions(self):
        """ List of formatted literal dicts """
        return [p.get_literal_dict() for p in self.preconditions]

    def to_str(self):
        return (str(self.action) + "(" + ",".join([str(x) 
            for x in self.arguments]) + ")")

class Precondition:

    def __init__(self, literal_dict):
        """ Precondition container for hashing purposes 
        
        literal_dict has the following structure
        { 'literal': 'agentAt',
          'arguments': [(1,3)] }
        """
        self.literal = literal_dict['literal']
        self.arguments = literal_dict['arguments']


    def get_literal_dict(self):
        """ Format precondition as plain dict """
        return create_literal_dict(self.literal, self.arguments)


class PartialOrderPlanner:

    def __init__(self, initial_state, goal_state):
        """ construct planner """
        self.start_action  = Action(START, None, None, (initial_state, []))
        self.finish_action = Action(FINISH, None, goal_state, None)
        # keep track of which actions have been created
        # NOTE should we allow same actions? maybe they do occur..
        self.created_actions = { 
                self.start_action.to_str(): self.start_action, 
                self.finish_action.to_str(): self.finish_action }
        # initial plan contains start and finish
        self.actions = { self.start_action, self.finish_action }
        # initially we only have start before finish
        self.ordering_constraints = { (self.start_action, self.finish_action) }
        # initially we have no causal links
        self.causal_links = set()
        # dict of achieving actions for given precondition
        # where precondition is key and list of achievers is value
        # will have incomplete action (only action and arguments)
        # will be plain action_dict
        self.precondition_achiever = dict()
        # add goal state to open preconditions
        self.open_preconditions = set()
        for p in self.finish_action.get_formatted_preconditions():
            precond = Precondition(p)
            # add open preconditions as tuple (precondition, action)
            self.open_preconditions.add((precond, self.finish_action))
            # use plain precondition dict to find achieving actions
            self.precondition_achiever[precond] = find_action_from_precondition(p)


    def create(self):
        print("create")
        while len(self.open_preconditions) > 0:
            print("successor")
            self.successor()

        # TODO topologically sort plan and return

    def successor(self):
        """ arbitrarily picks an open precondition p on an action B and
        generates successor plan for every possible consistent way of 
        choosing an action A that achieves p
        """
        print([a.to_str() for a in self.actions])
        open_precond, dependent_action = self.open_preconditions.pop()
        achieving_action = self.create_action_from_incomplete(
                self.precondition_achiever[open_precond].pop())
        new_constraint = (achieving_action, dependent_action)

        if (self.creates_cycle(new_constraint) 
        or self.illegal_constraint(new_constraint)):
            # cannot add cycles to set of constraints
            # re-add open precondition and return
            self.open_preconditions.add((open_precond, dependent_action))
            return 
        else:
            # otherwise we can add constraint
            self.ordering_constraints.add(new_constraint)
            self.causal_links.add((achieving_action, open_precond, 
                dependent_action))
            for p in achieving_action.preconditions:
                self.open_preconditions.add((p, achieving_action))
                self.precondition_achiever[p] = find_action_from_precondition(
                        p.get_literal_dict())

            if achieving_action not in self.actions:
                self.actions.add(achieving_action)
                self.ordering_constraints.add((self.start_action,
                    achieving_action))
                self.ordering_constraints.add((achieving_action,
                    self.finish_action))

            potential_conflicts = self.check_potential_conflicts(
                    achieving_action)
            if len(potential_conflicts) > 0:
                conflicts = self.validate_conflicts(achieving_action,
                        potential_conflicts)
                if len(conflicts) > 0:
                    resolved = self.resolve_conflicts(achieving_action,
                            conflicts)
                    if not resolved:
                        self.backtrack(achieving_action, dependent_action)


    def backtrack(self, achiever, dependent):
        """ Remove all constraints and causal links that include 
        the action as an achiever and open the preconditions again

        TODO:
        do we miss any constraints that were added to resolve conflicts?
        """
        causal_links_to_discard = {(A, p, B) for A,p,B in self.causal_links
                if A is achiever or A is dependent or B is dependent}

        for (A,p,B) in causal_links_to_discard:
            self.causal_links.discard((A,p,B))
            self.ordering_constraints.discard((A,B))
            if A is dependent:
                # re-add precondition
                self.open_preconditions.add(p)
            elif B is self.finish_action:
                self.open_preconditions.add(p)
            else:
                # we cannot remove finish action
                self.actions.discard(B)
                del self.created_actions[B.to_str()]
            self.actions.discard(A)
            del self.created_actions[A.to_str()]


    def resolve_conflicts(self, C, conflicts):
        """ Attempt to resolve conflicts. If not possible, return false.
        Otherwise return true.
        """
        for A, B in conflicts:
            if (not self.creates_cycle((C,A)) 
            and not self.illegal_constraint((C,A))):
                self.ordering_constraints.add((C,A))
            elif (not self.creates_cycle((B,C))
            and not self.illegal_constraint((B,C))):
                self.ordering_constraints.add((B,C))
            else:
                # if not possible to resolve conflict
                return False
        return True


    def validate_conflicts(self, C, potentials):
        """ Validate the list of potential conflicts and return it """
        return [(A,B) for A, B in potentials if 
                (A,C) in self.ordering_constraints and 
                (C,B) in self.ordering_constraints]


    def check_potential_conflicts(self, action):
        """ Find potential conflicts and return them """
        neg_effects = action.effects[1]
        potential_conflicts = []
        for effect in neg_effects:
            for A, p, B in self.causal_links:
                if p.get_literal_dict() == effect:
                    potential_conflicts.append((A,B))
        return potential_conflicts            


    def illegal_constraint(self, ordering_constraint):
        """ Validate that constraint is not illegal """
        illegal = False
        if self.start_action is ordering_constraint[1]:
            illegal = True
        elif self.finish_action is ordering_constraint[0]:
            illegal = True
        return illegal


    def creates_cycle(self, ordering_constraint):
        """ Validate that ordering constraint will not create a cycle """
        return ((ordering_constraint[1], ordering_constraint[0]) 
                in self.ordering_constraints)


    def create_action_from_incomplete(self, action_dict):
        """ Complete action's fields and return an action instance.
        If action exists in set of created actions, it will be reused.

        Returns complete action instance
        """
        act = action_dict['action']
        args = action_dict['arguments']
        action_descriptor = Action(act, args, None, None).to_str()
        # if action's already been created use it
        # otherwise create new and add to list of created
        if action_descriptor in self.created_actions:
            action = self.created_actions[action_descriptor]
        else:
            preconditions = action_helpers[act][PRECONDITIONS](*args)
            effects = action_helpers[act][EFFECTS](*args)
            action = Action(act, args, preconditions, effects) 
            # update list
            self.created_actions[action_descriptor] = action
        return action


def find_action_from_precondition(precondition):
    """ Find possible and achievable actions that fulfils precondition """
    wanted_actions = []
    literal = precondition['literal']

    # will only consider add lists (the first element of the tuples)
    # for each possible action
    if (literal in [ atom['literal'] for atom in
    action_helpers[MOVE][EFFECTS]()[0] ]):
        wanted_actions.append(MOVE)
    if (literal in [ atom['literal'] for atom in
    action_helpers[PUSH][EFFECTS]()[0] ]):
        wanted_actions.append(PUSH)
    if (literal in [ atom['literal'] for atom in
    action_helpers[PULL][EFFECTS]()[0] ]):
        wanted_actions.append(PULL)

    # go through each possible permutation
    # check if it is achievable and add it to possible actions
    possible_actions = find_applicable_actions(wanted_actions, precondition)

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

    planner.create()
    print([act.to_str() for act in planner.actions])

