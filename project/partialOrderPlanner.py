from toposort import toposort_flatten, toposort

from action import Action
from precondition import Precondition

from actionSchema import action_helpers, find_applicable_actions
from utilities import MOVE, PUSH, PULL
from utilities import PRECONDITIONS, EFFECTS, START, FINISH
from utilities import AGENT_AT, BOX_AT, FREE, ADD, DEL
from utilities import calculate_next_position, create_literal_dict
from utilities import create_action_dict

DEBUG = False

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
            self.precondition_achiever[(precond, self.finish_action)] = (
                    self.find_action_from_precondition(p))
        # dict to keep track of constraints that resolve conflicts
        self.conflict_resolving_constraints = dict()


    def create(self):
        """ Will return one object that contains possible total order plans """
        while len(self.open_preconditions) > 0:
            self.successor()
        return toposort(self.create_dependency_dict())


    def successor(self):
        """ Arbitrarily picks an open precondition p on an action B and
        generates successor plan for every possible consistent way of 
        choosing an action A that achieves p
        """
        open_precond, dependent_action = self.open_preconditions.pop()
        # validate that action is still in set of actions
        if dependent_action not in self.actions:
            print("##", dependent_action.to_str(), "is no longer valid")
            return

        self.eliminate_retarded_actions(open_precond, dependent_action)

        achieving_action = self.next_achiever(open_precond, dependent_action)
        #print(open_precond.to_str(), dependent_action.to_str())

        if achieving_action is None:
            self.backtrack(dependent_action)
            input("tryk på et eller andet for at fortsætte")
            return

        achieving_action = self.create_action_from_incomplete(
                achieving_action)
        new_constraint = (achieving_action, dependent_action)
         
        #print("  ", achieving_action.to_str())

        if DEBUG:
            topo = list(toposort(self.create_dependency_dict()))
            order = print_from_partial_order(topo)
            print("current plan:", order)
            print("orderings:", [A.to_str()+"-"+B.to_str() for A,B in
                self.ordering_constraints])
            print("open preconditions:", len(self.open_preconditions))
            print("attempting to close", open_precond.to_str(), "for", dependent_action.to_str())
            print("achieving action:", achieving_action.to_str())
            print("remaining possible achievers:")
            print([ Action(action_dict['action'],
                action_dict['arguments'],None,None).to_str() for action_dict in
                self.precondition_achiever[(open_precond,dependent_action)] ])
            print()

        if (self.creates_cycle(new_constraint) or
                self.illegal_constraint(new_constraint)):
            # can't add cycles to constraints - re-add open precondition
            self.open_preconditions.add((open_precond, dependent_action))
            return 
        else:
            # check for conflicts before adding stuff
            potential_conflicts = self.check_potential_conflicts(
                    achieving_action)
            if len(potential_conflicts) > 0:
                #print("++ potential conflicts", [(a.to_str(),b.to_str()) for a,b in potential_conflicts])
                conflicts = self.validate_conflicts(achieving_action,
                        potential_conflicts)
                if len(conflicts) > 0:
                    #print("+++ conflicts", [(a.to_str(),b.to_str()) for a,b in conflicts])
                    resolved = self.resolve_conflicts(achieving_action,
                            conflicts)
                    if not resolved:
                        #print(" ++++ re-adding", open_precond.to_str())
                        self.open_preconditions.add((open_precond, 
                            dependent_action))
                        return 

            self.ordering_constraints.add(new_constraint)
            self.causal_links.add((achieving_action, open_precond, 
                dependent_action))

            for p in achieving_action.preconditions:
                # open action's preconditions
                self.open_preconditions.add((p, achieving_action))
                # find and save actions that can close precondition
                self.precondition_achiever[(p,achieving_action)] = (
                    self.find_action_from_precondition(p.get_literal_dict()))

            # if action is not already in set of actions, update stuff
            if achieving_action not in self.actions:
                self.actions.add(achieving_action)
                self.ordering_constraints.add((self.start_action,
                    achieving_action))
                self.ordering_constraints.add((achieving_action,
                    self.finish_action))


    def next_achiever(self, open_precond, dependent_action):
        if len(self.precondition_achiever[(open_precond,dependent_action)]) > 0:
            achiever = self.precondition_achiever[(open_precond,dependent_action)].pop(0)
        else:
            achiever = None
        return achiever


    def causal_links_to_discard(self, dependent):
        return {(A,p,B) for A,p,B in self.causal_links if B is dependent}


    def ordering_constraints_to_discard(self, causal_links, dependent):
        # create from causal links
        constraints_to_discard = {(A,B) for A,_,B in causal_links}
        # add start and finish constraints
        constraints_to_discard.add((self.start_action, dependent)) 
        constraints_to_discard.add((dependent, self.finish_action)) 

        return constraints_to_discard


    def find_connectors_as_dict(self, links_to_discard):
        connectors = dict()
        to_be_inspected = list(links_to_discard)

        while len(to_be_inspected) > 0:
            # next causal link to inspect
            A,_,B = to_be_inspected.pop()
            # we do not check if A is Start
            if A is not self.start_action:
                if A not in connectors:
                    connectors[A] = set()
                for C,_p,D in self.causal_links:
                    # otherwise check if D is A (and thus connected to an
                    # action we want to remove) and it is not already in the
                    # set of connectors that we have found
                    if D is A and (C,_p,D) not in connectors[A]:
                        #print("adding", C.to_str(), " ", _p.to_str(), " ",
                        #        D.to_str())
                        connectors[A].add((C,_p,D))
                        # update list to be inspected
                        # it might be connected further
                        to_be_inspected.append((C,_p,D))
        #print("found", len(connectors), "connectors")
        return connectors


    def causal_links_to_reopen(self, dependent):
        return {(A,p,B) for A,p,B in self.causal_links if A is dependent}


    def backtrack(self, dependent):
        """ Remove all constraints and causal links that include 
        the action as an achiever and open the preconditions again
        """
        #print("-- backtrack (", dependent.to_str(), ")")

        # find all causal links where `dependent` is B in (A,p,B)
        # find ordering constraints where A or B are in constraint
        removable_causal_links = self.causal_links_to_discard(dependent)
        removable_constraints = self.ordering_constraints_to_discard(
                removable_causal_links, dependent)
        # add constraints that were added because of conflicts
        if dependent in self.conflict_resolving_constraints:
            removable_constraints.union(
                    self.conflict_resolving_constraints[dependent])
            # no longer needed
            del self.conflict_resolving_constraints[dependent]

        # we will reopen preconditions from this set
        restorable_causal_links = self.causal_links_to_reopen(dependent)
        # update removable constraints
        removable_constraints.union(self.ordering_constraints_to_discard(
            restorable_causal_links, dependent))

        # from above causal links find all connected links
        connected_causal_links = self.find_connectors_as_dict(
                removable_causal_links)
        # find all ordering constraints for connectors
        for action_key in connected_causal_links:
            removable_constraints.union(self.ordering_constraints_to_discard(
                connected_causal_links[action_key], action_key))
            # also add conflict resolving constraints 
            if action_key in self.conflict_resolving_constraints:
                removable_constraints.union(
                        self.conflict_resolving_constraints[action_key])
                # no longer needed
                del self.conflict_resolving_constraints[action_key]

        # we want to remove all actions that were connected to removable causal
        # links because they are no longer valid - plus the dependent action
        removable_actions = {A for A in connected_causal_links}
        removable_actions.add(dependent)

        # update removable causal links
        removable_causal_links.union(restorable_causal_links)
        for action_key in connected_causal_links:
            removable_causal_links.union(connected_causal_links[action_key])

        # preconditions to discard
        removable_preconditions = {(p,B) for p,B in self.open_preconditions if
                B is dependent}

        print("BEFORE")
        print("CL:", len(self.causal_links), "\tOC:",
                len(self.ordering_constraints), "\tA:", len(self.actions),
                "\tOP:", len(self.open_preconditions))
        ## PERFORM GLOBAL UPDATES
        # update open preconditions for dependent action
        self.open_preconditions = self.open_preconditions.difference(
                removable_preconditions)

        # reopen precondition p for action B
        for _,p,B in restorable_causal_links:
            self.open_preconditions.add((p,B))

        self.causal_links = self.causal_links.difference(
                removable_causal_links)
        self.ordering_constraints = self.ordering_constraints.difference(
                removable_constraints)
        self.actions = self.actions.difference(removable_actions)
        print("AFTER")
        print("CL:", len(self.causal_links), "\tOC:",
                len(self.ordering_constraints), "\tA:", len(self.actions),
                "\tOP:", len(self.open_preconditions))

        #print("   discarded causal links:")
        #print([A.to_str()+" "+p.to_str()+" "+B.to_str() for A,p,B in
        #    links_to_discard])
        #[A.to_str()+" "+p.to_str()+" "+B.to_str() for A,p,B in links_to_discard]
        print("   discarded ordering constraints:")
        print([A.to_str() + ", " + B.to_str() for A,B in constraints_to_discard])
        #[A.to_str() + ", " + B.to_str() for A,B in constraints_to_discard]

        print("   discarded connecting causal links:")
        print([A.to_str()+" "+p.to_str()+" "+B.to_str() for A,p,B in
            connecting_links_to_clean])
        #[A.to_str()+" "+p.to_str()+" "+B.to_str() for A,p,B in 
        #        connecting_links_to_clean]

        print("   discarded connecting ordering constraints:")
        print([A.to_str() + ", " + B.to_str() for A,B in
            connecting_constraints_to_discard])
        #[A.to_str() + ", " + B.to_str() for A,B in
        #        connecting_constraints_to_discard]

        print("   discarded actions:")
        print([A.to_str() for A in actions])
        #[A.to_str() for A in actions]

        print("   will re-open preconditions:")
        print([p.to_str()+" for "+B.to_str() for _,p,B in links_to_add])
        #[p.to_str()+" for "+B.to_str() for _,p,B in links_to_add]

        print("   will discard preconditions:")
        print([p.to_str()+" for "+B.to_str() for p,B in
            preconditions_to_discard])
        #[p.to_str()+" for "+B.to_str() for p,B in preconditions_to_discard]

        print("actions:", len(self.actions))
        print("links:", len(self.causal_links))
        print("constraints:", len(self.ordering_constraints))
        print("preconditions:",len(self.open_preconditions))

        print()


    def eliminate_retarded_actions(self, precondition, dependent):
        """ Eliminate actions that make zero sense.
        TODO rename function...
        """
        for idx, action in enumerate(
                self.precondition_achiever[(precondition,dependent)]):
            action = self.create_action_from_incomplete(action)
            for p in action.preconditions:
                if p.get_literal_dict() in (dependent.effects[0] +
                        dependent.effects[1]):
                    #print("-- removing", action.to_str(), "with",
                    #        p.to_str(), "for", dependent.to_str())
                    del self.precondition_achiever[(precondition,dependent)][idx]
                    break


    def create_dependency_dict(self):
        """ Construct dependency chain """
        dependencies = dict()
        for (achiever, dependent) in self.ordering_constraints:
            if dependent in dependencies:
                dependencies[dependent].add(achiever)
            else:
                dependencies[dependent] = {achiever}
        return dependencies


    def resolve_conflicts(self, C, conflicts):
        """ Attempt to resolve conflicts. If not possible, return false.
        Otherwise return true.
        """
        added_constraints = set()
        for A, B in conflicts:
            if (not self.creates_cycle((C,A)) 
                    and not self.illegal_constraint((C,A))):
                self.ordering_constraints.add((C,A))
                added_constraints.add((C,A))
            elif (not self.creates_cycle((B,C))
                    and not self.illegal_constraint((B,C))):
                self.ordering_constraints.add((B,C))
                added_constraints.add((B,C))
            else:
                # if not possible to resolve conflict
                # undo added constraints and return false
                [self.ordering_constraints.discard((x,y)) for x,y in
                        added_constraints]
                return False
        # update dictionary of added constraints for future use
        if C in self.conflict_resolving_constraints:
            self.conflict_resolving_constraints[C].union(added_constraints)
        else:
            self.conflict_resolving_constraints[C] = added_constraints
        return True


    def validate_conflicts(self, C, potentials):
        """ Validate the list of potential conflicts and return it """
        return {(A,B) for A, B in potentials if 
                (A,C) in self.ordering_constraints or 
                (C,B) in self.ordering_constraints}


    def check_potential_conflicts(self, action):
        """ Find potential conflicts and return them """
        neg_effects = action.effects[1]
        potential_conflicts = set()
        for effect in neg_effects:
            for A, p, B in self.causal_links:
                if p.get_literal_dict() == effect:
                    potential_conflicts.add((A,B))
        return potential_conflicts            


    def illegal_constraint(self, ordering_constraint):
        """ Validate that constraint is not illegal """
        illegal = False
        if self.start_action is ordering_constraint[1]:
            illegal = True
        elif self.finish_action is ordering_constraint[0]:
            illegal = True
        elif ordering_constraint[1] is ordering_constraint[0]:
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


    def find_action_from_precondition(self, precondition):
        """ Find possible and achievable actions that fulfils precondition.
        Will search for existing actions that can close precondition and prepend to
        list.
        """
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

        # check if start action already has desired effects
        existing_achiever = list()
        if precondition in self.start_action.effects[0]:
            existing_achiever.append(self.start_action.get_action_dict())

        return existing_achiever + possible_actions


def print_from_partial_order(pop):
    """ Return list with total order plans """
    top = list()
    for s in pop:
        new_s = set()
        for act in s:
            new_s.add(act.to_str())
        top.append(new_s)
    return top


if __name__ == '__main__':
    from agent import Agent
    from utilities import create_literal_dict

    import builtins
    #  ++++++
    #  +aA 0+
    #  ++++++
    builtins.walls = { (0,0): "+", (0,1): "+", (0,2): "+", (0,3): "+", (0,4): "+", (0,5): "+", (0,6): "+", (0,7): "+", (0,8): "+",
                       (1,0): "+",                                                                                     (1,8): "+",
                       (2,0): "+", (2,1): "+", (2,2): "+", (2,3): "+", (2,4): "+", (2,5): "+", (2,6): "+", (2,7): "+", (2,8): "+"}
    builtins.goals = { (1,1): 'a' }
    builtins.boxes = { (1,3): 'A' }
    agent = Agent('mr. robot', (1,7))
    level = "++++++\n+aA 0+\n++++++"
    print("level:")
    print(level)
    initial_state = [ create_literal_dict(AGENT_AT, [(1,7)]),
                      create_literal_dict(BOX_AT, [(1,3)]),
                      create_literal_dict(FREE, [(1,1)]),
                      create_literal_dict(FREE, [(1,4)]),
                      create_literal_dict(FREE, [(1,5)]),
                      create_literal_dict(FREE, [(1,6)]),
                      create_literal_dict(FREE, [(1,2)])]
    goal_state = [ create_literal_dict(BOX_AT, [(1,1)]) ]
    planner = PartialOrderPlanner(initial_state, goal_state)
    DEBUG = False
    plan = planner.create()
    print("## final total order plan:\n", print_from_partial_order(plan))

