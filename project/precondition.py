from utilities import create_literal_dict

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

    def to_str(self):
        """ Return human readable string """
        return (str(self.literal) + "(" + ",".join([str(x) 
            for x in self.arguments]) + ")")


