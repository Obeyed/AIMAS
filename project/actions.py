
class Action:

  def __init__(self, name):
    self.name = name

  def update(self, name):
    self.name = name

  def print_name(self):
    print(self.name)
