import re
from src import config as cfg


class ValidateString:
    def __init__(self):
        self.terms = [term.lower() for term in getattr(cfg, "list_of_particulars", [])]

    def validate(self, string):
        text = re.sub(r"\s+", " ", str(string).strip().lower())
        if not text:
            return "no"

        if any(ch.isdigit() for ch in text):
            return "no"

        if any(term in text for term in self.terms):
            return "yes"

        return "no"


if __name__ == "__main__":
    cls = ValidateString()
    response = cls.validate("shareholders' equity")
    print(response)
