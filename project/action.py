from utilities import create_action_dict
from precondition import Precondition

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

    def get_action_dict(self):
        """ Format action as plain dict """
        return create_action_dict(self.action, self.arguments)

    def to_str(self):
        return (str(self.action) + "(" + ",".join([str(x) 
            for x in self.arguments]) + ")")
