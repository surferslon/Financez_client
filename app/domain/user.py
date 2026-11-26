from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """A Financez user, as received from Financez."""

    username: str
    password_hash: str
    accounts: list
    currencies: list

    def account_tree(self):
        """{group: [node]}, every node being an account with its "children".

        The accounts arrive in tree order: each one followed by its subaccounts, which have a higher depth.
        """
        groups = {}
        path = []  # the current account and its parents
        for account in self.accounts:
            node = {**account, "children": []}
            del path[node["depth"] :]
            siblings = path[-1]["children"] if path else groups.setdefault(node["group"], [])
            siblings.append(node)
            path.append(node)
        return groups
