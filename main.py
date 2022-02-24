import sys
import json
from ior_model_builder import Parameters, Summary, Result, Builder
import sqlite3
from sqlite3 import Error
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


def read_log(path):
    with open(path) as json_file:
        json_dictionary = json.loads(json_file.read())
        results, summaries, parameters, cmd = Builder.create_from_json(json_dictionary)


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def test_output():
    for path in ['ior_sample_mpi.json', 'ior.json']:
        with open(path) as json_file:
            json_dictionary = json.loads(json_file.read())
            results, summaries, parameters, cmd = Builder.create_from_json(json_dictionary)
            print(summaries[0].operation)
            print(summaries[1].operation)
            print(parameters.deadlineForStonewall)
            print(results[0].access)
            print(cmd)


if __name__ == '__main__':
    test_output()
    """
    con = create_connection(r"pythonsqlite.db")
    # sql = "CREATE TABLE personen (vorname VARCHAR(20), nachname VARCHAR(30), geburtstag DATE)"
    sql = 'DROP TABLE personen'
    print(con.cursor().execute(sql))
    """
