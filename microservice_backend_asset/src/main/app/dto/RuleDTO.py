

class Rule(object):
    def __init__(self, id, name, antecedent, consequent, evaluation, last_true, last_false):
        self.id = id
        self.name = name
        self.antecedent = antecedent
        self.consequent = consequent
        self.evaluation = evaluation
        self.last_true = last_true
        self.last_false = last_false
