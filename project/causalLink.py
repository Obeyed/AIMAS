from actionSchema import ActionSchema
from utilities import MOVE, PUSH, PULL

class CausalLink:

  def __init__(self, action, arguments, outgoing=None, incoming=None, open_preconditions=None, initial_state=None):
    """ Note to self: Had some trouble with setting defaults to empty list """

    #print("action: {0}\t args: {1}\t parents: {2}\t childs: {3}".format(action, arguments, incoming, outgoing))

    self.action    = action     # the action's literal
    self.arguments = arguments  # the action's arguments
    self.parents   = incoming or []
    self.children  = outgoing or []

    # assume to be formatted correctly with utilities' create_literal_dict()
    self.initial_state = initial_state
    # if preconditions is given use them
    # otherwise find them
    if action == "Start":
      self.open_preconditions = []
    else:
      self.open_preconditions = open_preconditions or self.find_open_preconditions()

    if bool(outgoing):
      [out.add_parent(self) for out in outgoing]


  def add_parent(self, incoming):
    """ Add parent to instance """
    #print("adding parent {0} to {1}".format(incoming, self))
    self.parents.append(incoming)
    # check if any of the open preconditions have been achieved
    self.open_preconditions = self.find_open_preconditions()
    #self.print(False)
    #print("parents {0}".format(self.parents))


  def add_child(self, outgoing):
    """ Add child to instance """
    #print("adding child {0} to {1}".format(outgoing, self))
    self.children.append(outgoing)


  def has_open_precondition(self):
    return len(self.open_preconditions) > 0


  def find_open_preconditions(self):
    """ Find which preconditions are open """
    #print("FINDING OPEN PRECONDITIONS")
    if self.action in ['Start', 'Finish']:
      preconditions = self.open_preconditions
    else:
      preconditions = self.list_action_preconditions()

    parent_effects = self.list_parents_effects()

    #print(self.action)
    #print("pre: {0}".format(preconditions))
    #print("eff: {0}".format(parent_effects))

    unsatisfied = []
    #print("CHECKING PRECONDITIONS: ", preconditions)
    for precondition in preconditions:
      satisfied = False
      #print("comparing ", precondition)
      for effect in parent_effects:
        #print("--> ", effect)
        # compare objects' values
        if precondition == effect:
          #print("equal!")
          satisfied = True
          break
      if not satisfied:
        #print("adding ", precondition, " to unsatisfied")
        unsatisfied.append(precondition)

    #print("UNSATISFIED: ", unsatisfied)
    return unsatisfied

  def list_parents_effects(self):
    """ Return parents' effects """
    #print("SEARCHING FOR PARENT EFFECTS")
    return [ literal for parent in self.parents
                     for literal in parent.list_action_effects() ] 


  def list_action_preconditions(self):
    """ Return action's preconditions """
    #print("SEARCHING FOR ACTION'S PRECONDITIONS")
    preconditions = []
    if self.action == MOVE:
      preconditions = ActionSchema.move_preconditions(*self.arguments)
    elif self.action == PUSH:
      preconditions = ActionSchema.push_preconditions(*self.arguments)
    elif self.action == PULL:
      preconditions = ActionSchema.pull_preconditions(*self.arguments)

    return preconditions


  def list_action_effects(self, add_only=True, del_only=False):
    """ Return action's effects lists (both add and delete list) i
    
    Keyword arguments:
    add_only -- return only add list
    del_only -- return only delete list
    """
    #print("list action effects")
    #print("{0} has following effects".format(self.action))
    effects = None
    if self.action == MOVE:
      effects = ActionSchema.move_effects(*self.arguments)
    elif self.action == PUSH:
      effects = ActionSchema.push_effects(*self.arguments)
    elif self.action == PULL:
      effects = ActionSchema.pull_effects(*self.arguments)
  
    #print("first: ", effects)
    # if initial state is set then we want it
    if self.initial_state:
      effects = self.initial_state
    elif add_only and effects:
      #print(effects)
      effects = effects[0]
    elif del_only and effects:
      #print(effects)
      effects = effects[1]
    #print("second: ", effects)

    return effects or []


  def print(self, simple=True):
    print("{0}({1}) {2}".format(self.action, self.arguments, self))
    if not simple:
      print("+--open conds: {0}".format(self.open_preconditions))
      print("+--parent: {0}".format([(parent.action, parent) for parent in self.parents]))
      print("+--children: {0}".format([(child.action, child) for child in self.children]))


if __name__ == '__main__':
    from agent import Agent
    from utilities import create_literal_dict
    from utilities import AGENT_AT, BOX_AT

    agent = Agent('mr. robot', (2,2))
    finish = CausalLink("Finish", None, open_preconditions=[create_literal_dict(AGENT_AT, [(2,1)])])
    print("SHOULD HAVE ONE OPEN: {0}".format(finish.open_preconditions))

    start = CausalLink("Start", 
                       None,
                       initial_state=[ create_literal_dict(AGENT_AT, [(2,3)]), 
                                       create_literal_dict(BOX_AT, [(3,3)]) ])

    move = CausalLink("Move", 
                      [agent.position, "W"], 
                      [finish])
    print("SHOULD BE EMPTY: {0}".format(finish.open_preconditions))
    print("SHOULD HAVE TWO OPEN: {0}".format(move.open_preconditions))

    print("SHOULD BE EMPTY: {0}".format(start.open_preconditions))
    print("SHOULD NOT HAVE PARENT: {0}".format(start.parents))

    a = CausalLink("Test", None)
    b = CausalLink("Test1", None)
    c = CausalLink("Test2", None)
    print(a, b, c)


    finish.print(False)
    move.print(False)
    start.print(False)

    print(start.list_action_effects())
