

class Rule(object):
    def __init__(self, id, name, antecedent, consequent, evaluation):
        self.id = id
        self.name = name
        self.antecedent = antecedent
        self.consequent = consequent
        self.evaluation = evaluation
