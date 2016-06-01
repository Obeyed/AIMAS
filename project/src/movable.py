
class Movable:

  def __init__(self, name, position, color=None):
    self.name = name
    self.position = position
    self.color = color

  def position(self):
    return self.position

  def move(self, position):
    self.position = position


class Agent(Movable):

  def __init__(self, name, position, color=None):
    super(Agent, self).__init__(name, position, color)


class Box(Movable):

  def __init__(self, name, position, color=None):
    super(Box, self).__init__(name, position, color)
