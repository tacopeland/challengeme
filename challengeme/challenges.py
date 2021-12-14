class Challenge():
    def __init__(self, chall_id, set_id, description, notes,
                 language_constraints, date_started, date_finished,
                 language_used):
        self.id = chall_id
        self.set_id = set_id
        self.description = description
        self.notes = notes
        self.language_constraints = language_constraints
        self.date_started = date_started
        self.date_finished = date_finished
        self.language_used = language_used
