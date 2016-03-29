
class Agent:

  def __init__(self, name, position, color=None):
    self.name = name
    self.position = position
    self.color = color

  def position(self):
    return self.position

  def move(self, position):
    self.position = position
