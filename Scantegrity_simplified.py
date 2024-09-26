import random
import string

class Ballot:
    def __init__(self, ballot_id, questions):
        self.ballot_id = ballot_id
        self.questions = questions
        self.codes = {q: {o: self.generate_code() for o in options} for q, options in questions.items()}
        self.marked_options = {}
        self.status = "Not Cast"  # Can be "Not Cast", "Cast", "Audited", or "Spoiled"

    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    def mark(self, question, option):
        self.marked_options[question] = option

    def get_code(self, question):
        return self.codes[question][self.marked_options[question]] if question in self.marked_options else None

class ElectionSystem:
    def __init__(self, num_voters, questions):
        self.num_voters = num_voters
        self.questions = questions
        self.ballots = [Ballot(f"{i+1:04d}", questions) for i in range(num_voters)]
        self.table_q = self.create_table_q()
        self.table_s = self.create_table_s()
        self.tables_r = [self.create_table_r() for _ in range(10)]  # 40 R tables as per Takoma Park example
        self.cast_votes = []
        self.audited_ballots = []
        self.spoiled_ballots = []

    def create_table_q(self):
        table_q = {}
        for ballot in self.ballots:
            for question, options in self.questions.items():
                codes = list(ballot.codes[question].values())
                random.shuffle(codes)
                table_q.setdefault(ballot.ballot_id, {})[question] = codes
        return table_q

    def create_table_s(self):
        return {q: {o: set() for o in options} for q, options in self.questions.items()}

    def create_table_r(self):
        table_r = []
        for ballot in self.ballots:
            for question, options in self.questions.items():
                for i, code in enumerate(self.table_q[ballot.ballot_id][question]):
                    q_pointer = (ballot.ballot_id, question, i)
                    s_pointer = (question, list(options)[i % len(options)])
                    table_r.append({"flag": False, "q_pointer": q_pointer, "s_pointer": s_pointer})
        random.shuffle(table_r)
        return table_r

    def cast_vote(self, ballot, choices):
        if ballot.status == "Not Cast":
            for question, option in choices.items():
                ballot.mark(question, option)
            ballot.status = "Cast"
            for question, option in choices.items():
                code = ballot.get_code(question)
                self.cast_votes.append((ballot.ballot_id, question, code))

                # Update Tables R and S
                for table_r in self.tables_r:
                    for entry in table_r:
                        if (entry["q_pointer"][0] == ballot.ballot_id and
                            entry["q_pointer"][1] == question and
                            self.table_q[ballot.ballot_id][question][entry["q_pointer"][2]] == code):
                            entry["flag"] = True
                            self.table_s[question][option].add(code)
                            break
        else:
            raise ValueError("Ballot has already been cast, audited, or spoiled")

    def audit_ballot(self, ballot):
        if ballot.status == "Not Cast":
            ballot.status = "Audited"
            self.audited_ballots.append(ballot)
        else:
            raise ValueError("Ballot has already been cast, audited, or spoiled")

    def spoil_ballot(self, ballot):
        if ballot.status == "Not Cast":
            ballot.status = "Spoiled"
            self.spoiled_ballots.append(ballot)
            # Reveal all information for this ballot in all R tables
            for table_r in self.tables_r:
                for entry in table_r:
                    if entry["q_pointer"][0] == ballot.ballot_id:
                        entry["flag"] = True
        else:
            raise ValueError("Ballot has already been cast, audited, or spoiled")

    def get_tally(self):
        return {q: {o: len(codes) for o, codes in options.items()} for q, options in self.table_s.items()}

def print_tables(election_system):
    print("Table Q:")
    for ballot_id, questions in election_system.table_q.items():
        print(f"{ballot_id}:")
        for question, codes in questions.items():
            print(f"  {question}: {codes}")
    print()

    print("Table S:")
    for question, options in election_system.table_s.items():
        print(f"{question}:")
        for option, codes in options.items():
            print(f"  {option}: {codes}")
    print()

    print("Tables R (showing only the first table):")
    for entry in election_system.tables_r[0]:
        print(f"Flag: {entry['flag']}, Q-Pointer: {entry['q_pointer']}, S-Pointer: {entry['s_pointer']}")
    print()

def print_results(election_system):
    tally = election_system.get_tally()
    print("Election Results:")
    for question, options in tally.items():
        print(f"{question}:")
        for option, votes in options.items():
            print(f"  {option}: {votes} votes")

    print("\nCast Votes (Ballot ID, Question, Code):")
    for vote in election_system.cast_votes:
        print(f"{vote[0]}, {vote[1]}: {vote[2]}")

    print("\nAudited Ballots:")
    for ballot in election_system.audited_ballots:
        print(ballot.ballot_id)

    print("\nSpoiled Ballots:")
    for ballot in election_system.spoiled_ballots:
        print(ballot.ballot_id)

def main():
    num_voters = 5
    questions = {
        "Mayor": ["Alice", "Bob", "Carol"],
        "City Council": ["Dan", "Eve", "Frank", "Grace"]
    }
    election_system = ElectionSystem(num_voters, questions)

    print("Initial state of tables:")
    print_tables(election_system)

    for ballot in election_system.ballots:
        print(f"Ballot ID: {ballot.ballot_id}")
        print(f"Status: {ballot.status}")
        for question, options in ballot.codes.items():
            print(f"{question}:")
            for option, code in options.items():
                print(f"  {option}: {code}")
        print()

        action = input("Choose an action (vote/audit/spoil/skip): ").lower()
        if action == "vote":
            choices = {}
            for question in questions:
                option = input(f"Enter your choice for {question}: ")
                if option in questions[question]:
                    choices[question] = option
                else:
                    print("Invalid option. Skipping this question.")
            try:
                election_system.cast_vote(ballot, choices)
                print("Vote cast successfully")
            except ValueError as e:
                print(f"Error: {e}")
        elif action == "audit":
            election_system.audit_ballot(ballot)
            print("Ballot audited")
        elif action == "spoil":
            election_system.spoil_ballot(ballot)
            print("Ballot spoiled")
        elif action == "skip":
            print("Skipping this ballot")
        else:
            print("Invalid action. Skipping this ballot.")

        print()

    print("Final state of tables:")
    print_tables(election_system)
    print_results(election_system)

if __name__ == "__main__":
    main()