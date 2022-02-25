import sys
import json
from ior_model_builder import Builder, PerformanceModel, Summary
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
        pm = Builder.create_from_json(json_dictionary)
        return pm


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


def generate_tables(con):
    sql_create_performances = "CREATE TABLE performances ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, cmd TEXT, ts TEXT, te TEXT, testID INTEGER , refnum INTEGER, api TEXT, platform TEXT," \
                              " testFileName TEXT, deadlineForStonewall INTEGER, stoneWallingWearOut INTEGER, maxTimeDuration INTEGER, outlierThreshold INTEGER, options TEXT, " \
                              "dryRun INTEGER, nodes INTEGER, memoryPerTask INTEGER, memoryPerNode INTEGER, tasksPerNode INTEGER, repetitions INTEGER, " \
                              "multiFile INTEGER, interTestDelay INTEGER, fsync INTEGER, fsyncperwrite INTEGER, useExistingTestFile INTEGER, uniqueDir INTEGER, " \
                              "singleXferAttempt INTEGER, readFile INTEGER, writeFile INTEGER, filePerProc INTEGER, reorderTasks INTEGER, reorderTasksRandom INTEGER, reorderTasksRandomSeed INTEGER," \
                              "randomOffset INTEGER, checkWrite INTEGER, checkRead INTEGER, dataPacketType INTEGER, keepFile INTEGER, keepFileWithError INTEGER, warningAsErrors INTEGER," \
                              "verbose INTEGER,collective INTEGER,segmentCount INTEGER,transferSize INTEGER,blockSize INTEGER );"
    sql_create_summaries = "CREATE TABLE summaries ( id INTEGER PRIMARY KEY AUTOINCREMENT, performace_id INTEGER NOT NULL,  operation TEXT, API TEXT, TestID INTEGER, ReferenceNumber INTEGER, " \
                           "segmentCount INTEGER, blockSize INTEGER, transferSize INTEGER, numTasks INTEGER, tasksPerNode INTEGER, repetitions INTEGER , filePerProc INTEGER, reorderTasks INTEGER, " \
                           "taskPerNodeOffset INTEGER, reorderTasksRandom INTEGER , reorderTasksRandomSeed INTEGER , bwMaxMIB REAL, bwMinMIB REAL, bwMeanMIB REAL, bwStdMIB REAL, OPsMax REAL, " \
                           "OPsMin REAL, OPsMean REAL, OPsSD REAL, MeanTime REAL, xsizeMiB REAL, CONSTRAINT summaries_FK, FOREIGN KEY (id) REFERENCES performances(id));"
    sql_create_results = "CREATE TABLE results ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, summary_id INTEGER NOT NULL, access TEXT, " \
                         "bwMiB REAL, blockKiB REAL,xferKiB REAL,iops REAL,latency REAL,openTime REAL,wrRdTime REAL,closeTime REAL,totalTime REAL, " \
                         "CONSTRAINT results_FK FOREIGN KEY (id) REFERENCES summaries(id));"
    print(con.cursor().execute(sql_create_performances))
    print(con.cursor().execute(sql_create_summaries))
    print(con.cursor().execute(sql_create_results))


def delete_tables(con):
    print(con.cursor().execute("DROP TABLE performances"))
    print(con.cursor().execute("DROP TABLE summaries"))
    print(con.cursor().execute("DROP TABLE results"))


def insert_performance(con, pm):
    print(pm.ts)
    sql_insert_performance = '''INSERT INTO performances (cmd, ts, te, testID, refnum, api, platform, testFileName, 
        deadlineForStonewall, stoneWallingWearOut, maxTimeDuration, outlierThreshold, \"options\", 
        dryRun, nodes, memoryPerTask, memoryPerNode, tasksPerNode, repetitions, multiFile, interTestDelay, 
        fsync, fsyncperwrite, useExistingTestFile, uniqueDir, singleXferAttempt, readFile, writeFile, filePerProc,
         reorderTasks, reorderTasksRandom, reorderTasksRandomSeed, randomOffset, checkWrite, checkRead, dataPacketType,
          keepFile, keepFileWithError, warningAsErrors, verbose, collective, 
          segmentCount, transferSize, blockSize) VALUES(?, ?,?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    print(sql_insert_performance)
    cursor = con.cursor()
    cursor.execute(sql_insert_performance, (pm.cmd, pm.ts, pm.te, pm.parameters.testID, pm.parameters.refnum, pm.parameters.api
                                            , pm.parameters.platform, pm.parameters.testFileName,
                                            pm.parameters.deadlineForStonewall,
                                            pm.parameters.stoneWallingWearOut, pm.parameters.maxTimeDuration,
                                            pm.parameters.outlierThreshold, pm.parameters.options,
                                            pm.parameters.dryRun, pm.parameters.nodes, pm.parameters.memoryPerTask,
                                            pm.parameters.memoryPerNode, pm.parameters.tasksPerNode,
                                            pm.parameters.repetitions,
                                            pm.parameters.multiFile, pm.parameters.interTestDelay, pm.parameters.fsync,
                                            pm.parameters.fsyncperwrite, pm.parameters.useExistingTestFile,
                                            pm.parameters.uniqueDir, pm.parameters.singleXferAttempt,
                                            pm.parameters.readFile, pm.parameters.writeFile, pm.parameters.filePerProc,
                                            pm.parameters.reorderTasks, pm.parameters.reorderTasksRandom,
                                            pm.parameters.reorderTasksRandomSeed, pm.parameters.randomOffset,
                                            pm.parameters.checkWrite,
                                            pm.parameters.checkRead, pm.parameters.dataPacketType,
                                            pm.parameters.keepFile, pm.parameters.keepFileWithError,
                                            pm.parameters.warningAsErrors,
                                            pm.parameters.verbose, pm.parameters.collective, pm.parameters.segmentCount,
                                            pm.parameters.transferSize, pm.parameters.blockSize))
    con.commit()
    if cursor.lastrowid > 0:
        insert_summary(con, pm.summaries)
        return 1


def insert_summary(con, summaries):
    sql_insert_summary = '''INSERT INTO summaries (performace_id, operation, API, TestID, ReferenceNumber, segmentCount, 
    blockSize, transferSize, numTasks, tasksPerNode, repetitions, filePerProc, reorderTasks, taskPerNodeOffset, 
    reorderTasksRandom, reorderTasksRandomSeed, bwMaxMIB, bwMinMIB, bwMeanMIB, bwStdMIB, OPsMax, OPsMin, OPsMean, OPsSD, MeanTime, xsizeMiB) 
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    # print(sql_insert_summary)
    cursor = con.cursor()
    for summary in summaries:
        cursor.execute(sql_insert_summary, (
        pm.id, summary.operation, summary.API, summary.TestID, summary.ReferenceNumber, summary.segmentCount,
        summary.blockSize, summary.transferSize, summary.numTasks, summary.tasksPerNode, summary.repetitions,
        summary.filePerProc, summary.reorderTasks, summary.taskPerNodeOffset, summary.reorderTasksRandom,
        summary.reorderTasksRandomSeed, summary.bwMaxMIB, summary.bwMinMIB, summary.bwMeanMIB, summary.bwStdMIB,
        summary.OPsMax, summary.OPsMin, summary.OPsMean, summary.OPsSD, summary.MeanTime, summary.xsizeMiB))
        con.commit()
        insert_result(con, cursor.lastrowid, summary.operation, pm.results)


def insert_result(con, summary_id, operation, results):
    for result in results:
        if result.access == operation:
            sql_insert_result = '''INSERT INTO results (summary_id, access, bwMiB, blockKiB, xferKiB, iops, latency, openTime, wrRdTime, closeTime, totalTime) 
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
            cursor = con.cursor()
            cursor.execute(sql_insert_result, (
            summary_id, result.access, result.bwMiB, result.blockKiB, result.xferKiB, result.iops, result.latency,
            result.openTime, result.wrRdTime, result.closeTime, result.totalTime))
            con.commit()

if __name__ == '__main__':
    pm = read_log('ior_sample_i4.json')
    con = create_connection(r"pythonsqlite.db")
    if 0:
        delete_tables(con)
    else:
        generate_tables(con)
        insert_performance(con, pm)
