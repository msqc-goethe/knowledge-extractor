import sys
import json
from ior_model_builder import Parameters, Summary, Result, Builder
sys.path.append(".")


"""
class Generic:
    @classmethod
    def from_dict(cls, dict):
        obj = cls()
        obj.__dict__.update(dict)
        return obj


def readLog(name):
    with open('ior.json') as json_file:
        x = json.loads(json_file.read(), object_hook=Generic.from_dict)
        print(x.tests[0].Parameters)
"""


def read_log():
    with open('ior.json') as json_file:
        json_dictionary = json.loads(json_file.read())
        # parameters = Parameters.create_from_json(json_dictionary)
        # summaries = Summary.create_from_json(json_dictionary)
        # results = Result.create_from_json(json_dictionary)
        results, summaries, parameters = Builder.create_from_json(json_dictionary)
        # print(summaries[0].operation)
        # print(summaries[1].operation)
        # print(parameters.deadlineForStonewall)
        # print(results[0].access)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    read_log()
