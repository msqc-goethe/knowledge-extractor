import sys
import os
import json
import argparse
import darshan

from ior_model_builder import Builder, Beegfs, FilesystemModel, IO500, Run, Testcase, Score
from ior_options_model import I0500OptionsModel, IO500ResultsModel
from sysinfo import *

import sqlite3
from sqlite3 import Error

sys.path.append(".")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# connect to the SQlite databases
def openConnection(pathToSqliteDb):
    connection = sqlite3.connect(pathToSqliteDb)
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    return connection, cursor


def getAllRecordsInTable(table_name, pathToSqliteDb):
    conn, curs = openConnection(pathToSqliteDb)
    conn.row_factory = dict_factory
    curs.execute("SELECT * FROM '{}' ".format(table_name))
    # fetchall as result
    results = curs.fetchall()
    # close connection
    conn.close()
    return json.dumps(results)


def sqliteToJson(pathToSqliteDb):
    connection, cursor = openConnection(pathToSqliteDb)
    # select all the tables from the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    # for each of the tables , select all the records from the table
    for table_name in tables:
        # Get the records in table
        results = getAllRecordsInTable(table_name['name'], pathToSqliteDb)

        # generate and save JSON files with the table name for each of the database tables and save in results folder
        with open('./json_results/' + table_name['name'] + '.json', 'w') as the_file:
            the_file.write(results)
    # close connection
    connection.close()


def read_log(path, fs):
    with open(path) as json_file:
        json_dictionary = json.loads(json_file.read())
        pm = Builder.create_from_json(json_dictionary, fs)
        return pm


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def read_io500(path = "2022.06.16-13.32.58/"):
    ts, te = "", ""
    run = Run.__new__(Run)
    score = Score.__new__(Score)
    testcases = []
    rPath = path + "result.txt"
    with open(rPath, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            line = lines[i].rstrip()
            if line == '[run]':
                run.__init__(lines[i + 1].rstrip().split('=',1)[1], lines[i + 2].rstrip().split('=')[1],
                             lines[i + 3].rstrip().split('=',1)[1], lines[i + 4].rstrip().split('=',1)[1], lines[i + 5].rstrip().split('=')[1])
            elif line.startswith('[mdtest') or line.startswith('[ior'):
                if line.startswith('[ior'):
                    if line.find("write") != -1:
                        o, r = get_options_results(line.strip("[]\n"), 1, path)
                        tc = Testcase(line.strip("[]\n"),
                                      lines[i + 1].rstrip().split('=', 1)[1],
                                      lines[i + 2].rstrip().split('=', 1)[1],
                                      lines[i + 4].rstrip().split('=', 1)[1],
                                      lines[i + 5].rstrip().split('=', 1)[1],
                                      lines[i + 6].rstrip().split('=', 1)[1],
                                      lines[i + 3].rstrip().split('=', 1)[1], o, r)
                        testcases.append(tc)
                    else:
                        o, r = get_options_results(line.strip("[]\n"), 0, path)
                        tc = Testcase(line.strip("[]\n"),
                                      lines[i + 1].rstrip().split('=',1)[1],
                                      lines[i + 2].rstrip().split('=',1)[1],
                                      lines[i + 3].rstrip().split('=',1)[1],
                                      lines[i + 4].rstrip().split('=',1)[1],
                                      lines[i + 5].rstrip().split('=',1)[1],
                                      -1,o,r)
                        testcases.append(tc)
                else:
                    if line.find("write") != -1:
                        tc = Testcase(line.strip("[]\n"),
                                      lines[i + 1].rstrip().split('=',1)[1],
                                      lines[i + 2].rstrip().split('=',1)[1],
                                      lines[i + 4].rstrip().split('=',1)[1],
                                      lines[i + 5].rstrip().split('=',1)[1],
                                      lines[i + 6].rstrip().split('=',1)[1],
                                      lines[i + 3].rstrip().split('=',1)[1])
                        testcases.append(tc)
                    else:
                        tc = Testcase(line.strip("[]\n"),
                                      lines[i + 1].rstrip().split('=',1)[1],
                                      lines[i + 2].rstrip().split('=',1)[1],
                                      lines[i + 3].rstrip().split('=',1)[1],
                                      lines[i + 4].rstrip().split('=',1)[1],
                                      lines[i + 5].rstrip().split('=',1)[1],
                                      -1)
                        testcases.append(tc)

            elif line.startswith('[find'):
                pass
            elif line.startswith('[SCO'):
                score.__init__(lines[i + 1].rstrip().split('=',1)[1],
                               lines[i + 2].rstrip().split('=',1)[1],
                               lines[i + 3].rstrip().split('=',1)[1],
                               lines[i + 4].rstrip().split('=',1)[1])
            elif line.startswith('; START'):
                ts = line.split('T ')[1]
            elif line.startswith('; END'):
                te= line.split('D ')[1]

        return IO500(run,testcases,score,ts, te, get_sys_info())


def get_options_results(testcase, isWrite, folderPath = "2022.06.16-13.32.58/"):
    options = I0500OptionsModel.__new__(I0500OptionsModel)
    result = IO500ResultsModel.__new__(IO500ResultsModel)
    path = folderPath + testcase + ".txt"
    print(path)
    with open(path, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            line = lines[i].rstrip()
            if line.startswith('Options'):
                if isWrite:
                    options.__init__(lines[i + 1].rstrip().split(':',1)[1],
                                  lines[i + 2].rstrip().split(':',1)[1],
                                  lines[i + 3].rstrip().split(':',1)[1],
                                  lines[i + 4].rstrip().split(':',1)[1],
                                  lines[i + 5].rstrip().split(':',1)[1],
                                     lines[i + 6].rstrip().split(':',1)[1],
                                     lines[i + 7].rstrip().split(':',1)[1],
                                     lines[i + 8].rstrip().split(':',1)[1],
                                     lines[i + 9].rstrip().split(':',1)[1],
                                     lines[i + 10].rstrip().split(':',1)[1],
                                     lines[i + 11].rstrip().split(':',1)[1],
                                     lines[i + 12].rstrip().split(':',1)[1],
                                     lines[i + 13].rstrip().split(':',1)[1],
                                     lines[i + 14].rstrip().split(':',1)[1],
                                     lines[i + 15].rstrip().split(':',1)[1],
                                     lines[i + 16].rstrip().split(':',1)[1],
                                     lines[i + 17].rstrip().split(':',1)[1],
                                     lines[i + 18].rstrip().split(':',1)[1]
                                     )
                else:
                    options.__init__(lines[i + 1].rstrip().split(':',1)[1],
                                  lines[i + 2].rstrip().split(':',1)[1],
                                  lines[i + 3].rstrip().split(':',1)[1],
                                  lines[i + 4].rstrip().split(':',1)[1],
                                  lines[i + 5].rstrip().split(':',1)[1],
                                     lines[i + 6].rstrip().split(':',1)[1],
                                     lines[i + 7].rstrip().split(':',1)[1],
                                     lines[i + 8].rstrip().split(':',1)[1],
                                     lines[i + 9].rstrip().split(':',1)[1],
                                     lines[i + 10].rstrip().split(':',1)[1],
                                     lines[i + 11].rstrip().split(':',1)[1],
                                     lines[i + 12].rstrip().split(':',1)[1],
                                     lines[i + 13].rstrip().split(':',1)[1],
                                     lines[i + 14].rstrip().split(':',1)[1],
                                     lines[i + 15].rstrip().split(':',1)[1],
                                     lines[i + 16].rstrip().split(':',1)[1]
                                     )
            elif line.startswith("Results"):
                for j in range(len(lines) - i):
                    if lines[i+j].startswith('write') or lines[i+j].startswith('read'):
                        r= lines[i+j].split()
                        print(lines[i+j].split())
                        result.__init__(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10])
    return options, result


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


def read_haccio(con, path='hacc-logs/'):
    arr = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            fp = os.path.join(subdir, file)
            if '.git' not in fp:
                with open(fp, "r") as f:
                    ob = []
                    lines = f.readlines()
                    for i in range(0, len(lines)):
                        line = lines[i].lstrip().rstrip()
                        if line.startswith('READ') or line.startswith('WRITE'):
                            ob.append({'operation': line.split(':')[0], 'bw': line.split(':')[1].split()[0:2:1],
                                       'size': line.split(':')[1].split()[2:4:1], 'time': line.split(':')[1].split()[4:6:1]})
                    cu = {'name_app': 'Haccio', 'type': 'Benchmark', 'summary': json.dumps(ob)}
                    print(get_fs_settings())
                    print(get_sys_info())
                    dummy_fs = "{\"entryType\":\"directory\\n\",\"entryID\":\"694-62447785-1\\n\",\"metadataNode\":\"mds01[ID:1]\\n\",\"StripePatternType\":\"RAID0\\n\",\"StripePatternChunkSize\":\"1M\\n\",\"StripePatternStoragePool\":\"desired:4\\n\"}"
                    dummy_sy = "{\"procs\":40,\"name\":\"fuchs.cm.cluster-nv\",\"kernel_version\":\"3.10.0-1160.53.1.el7.x86_64\",\"processor_architecture\":\"x86_64\",\"processor_model\":\"IntelXeonE5-2670v2\",\"processor_frequency\":\"02.50GHz\",\"processor_threads\":2,\"processor_vendor\":\"GenuineIntel\",\"processor_L2\":\"256K\",\"processor_L3\":\"25600K\",\"processor_coresPerSocket\":10,\"distribution\":\"scientific\",\"distribution_version\":\"7.9\",\"memory_capacity\":\"131932792KiB\"}"
                    insert_custom(con, cu, dummy_fs, dummy_sy)
    print(arr)


def generate_tables(con):
    cur = con.cursor()
    tns = ["performances", "summaries", "results", "filesystems", "sysinfos", "IOFHs", "IOFHsRuns","IOFHsScores", "IOFHsTestcases","IOFHsOptions", "IOFHsResults", "DarshanSummaries", "Custom"]
    for name in tns:
        sql = "SELECT name FROM sqlite_master WHERE type=\"table\" AND name=(?)"
        # print(sql, name)
        cur.execute(sql, (name,))
        rows = cur.fetchall()
        if len(rows) != 1:
            if name == "performances":
                sql_create_performances = "CREATE TABLE performances ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, cmd TEXT, ts TEXT, te TEXT, testID INTEGER , refnum INTEGER, api TEXT, platform TEXT," \
                                          " testFileName TEXT, hintsFileName TEXT, deadlineForStonewall INTEGER, stoneWallingWearOut INTEGER, maxTimeDuration INTEGER, outlierThreshold INTEGER, options TEXT, " \
                                          "dryRun INTEGER, nodes INTEGER, memoryPerTask INTEGER, memoryPerNode INTEGER, tasksPerNode INTEGER, repetitions INTEGER, " \
                                          "multiFile INTEGER, interTestDelay INTEGER, fsync INTEGER, fsyncperwrite INTEGER, useExistingTestFile INTEGER, showHints INTEGER, uniqueDir INTEGER, individualDataSets INTEGER," \
                                          "singleXferAttempt INTEGER, readFile INTEGER, writeFile INTEGER, filePerProc INTEGER, reorderTasks INTEGER, reorderTasksRandom INTEGER, reorderTasksRandomSeed INTEGER," \
                                          "randomOffset INTEGER, checkWrite INTEGER, checkRead INTEGER, preallocate INTEGER, useFileView INTEGER, setAlignment INTEGER, " \
                                          "storeFileOffset INTEGER, useSharedFilePointer INTEGER, useStridedDatatype INTEGER, keepFile INTEGER, keepFileWithError INTEGER," \
                                          "verbose INTEGER,collective INTEGER,segmentCount INTEGER,transferSize INTEGER,blockSize INTEGER, warningAsErrors INTEGER);"
                # print(sql_create_performances)
                con.cursor().execute(sql_create_performances)
            elif name == "summaries":
                sql_create_summaries = "CREATE TABLE summaries ( id INTEGER PRIMARY KEY AUTOINCREMENT, performance_id INTEGER NOT NULL,  operation TEXT, API TEXT, TestID INTEGER, ReferenceNumber INTEGER, " \
                                       "segmentCount INTEGER, blockSize INTEGER, transferSize INTEGER, numTasks INTEGER, tasksPerNode INTEGER, repetitions INTEGER , filePerProc INTEGER, reorderTasks INTEGER, " \
                                       "taskPerNodeOffset INTEGER, reorderTasksRandom INTEGER , reorderTasksRandomSeed INTEGER , bwMaxMIB REAL, bwMinMIB REAL, bwMeanMIB REAL, bwStdMIB REAL, OPsMax REAL, " \
                                       "OPsMin REAL, OPsMean REAL, OPsSD REAL, MeanTime REAL, xsizeMiB REAL, CONSTRAINT summaries_FK, FOREIGN KEY (performance_id) REFERENCES performances(id));"
                con.cursor().execute(sql_create_summaries)
            elif name == "results":
                sql_create_results = "CREATE TABLE results ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, summary_id INTEGER NOT NULL, access TEXT, " \
                                     "bwMiB REAL, blockKiB REAL,xferKiB REAL,iops REAL,latency REAL,openTime REAL,wrRdTime REAL,closeTime REAL,totalTime REAL, " \
                                     "CONSTRAINT results_FK FOREIGN KEY (summary_id) REFERENCES summaries(id));"
                con.cursor().execute(sql_create_results)
            elif name == "filesystems":
                sql_create_filesystems = "CREATE TABLE filesystems ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, performance_id INTEGER NOT NULL, type TEXT, " \
                                         "settings REAL, " \
                                         "CONSTRAINT filesystems_FK FOREIGN KEY (performance_id) REFERENCES performances(id));"
                con.cursor().execute(sql_create_filesystems)


            elif name == "sysinfos":
                sql_create_sysinfos = "CREATE TABLE sysinfos ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, IOFH_id INTEGER NOT NULL, name TEXT, " \
                                         "kernel_version TEXT,processor_architecture TEXT,processor_model TEXT,processor_frequency TEXT,processor_threads INTEGER,processor_vendor TEXT," \
                                         "processor_L2 TEXT, processor_L3 TEXT, processor_coresPerSocket INTEGER " \
                                      ",distribution TEXT ,distribution_version TEXT ,memory_capacity TEXT, CONSTRAINT sysinfos_FK FOREIGN KEY (IOFH_id) REFERENCES IOFHs(id));"
                con.cursor().execute(sql_create_sysinfos)
            elif name == "IOFHs":
                sql_create_IOFHs = "CREATE TABLE IOFHs ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, start TEXT, end TEXT);"
                con.cursor().execute(sql_create_IOFHs)
            elif name == "IOFHsRuns":
                sql_create_IOFHsRuns = "CREATE TABLE IOFHsRuns ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, IOFH_id INTEGER NOT NULL, procs INTEGER NOT NULL, version TEXT, " \
                                         "config_hash TEXT, result_dir TEXT, mode TEXT," \
                                         "CONSTRAINT IOFHsRuns_FK FOREIGN KEY (IOFH_id) REFERENCES IOFHs(id));"
                con.cursor().execute(sql_create_IOFHsRuns)
            elif name == "IOFHsScores":
                sql_create_IOFHsScores = "CREATE TABLE IOFHsScores ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, IOFH_id INTEGER NOT NULL, MD REAL, BW REAL, " \
                                       "SCORE REAL, CONSTRAINT IOFHsScores_FK FOREIGN KEY (IOFH_id) REFERENCES IOFHs(id));"
                con.cursor().execute(sql_create_IOFHsScores)
            elif name == "IOFHsTestcases":
                sql_create_IOFHsTestcases = "CREATE TABLE IOFHsTestcases ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, IOFHsRun_id INTEGER NOT NULL, name TEXT, t_start TEXT, " \
                                       "exe TEXT, stonewall REAL, score REAL, t_delta REAL, t_end TEXT, CONSTRAINT IOFHsTestcases_FK FOREIGN KEY (IOFHsRun_id) REFERENCES IOFHsRuns(id));"
                con.cursor().execute(sql_create_IOFHsTestcases)
            elif name == "IOFHsOptions":
                sql_create_IOFHsOptions = "CREATE TABLE IOFHsOptions ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, IOFHsTestcase_id INTEGER NOT NULL, api TEXT, apiVersion TEXT, " \
                                       "testFileName TEXT, access TEXT, type TEXT, segments INTEGER ,orderingInaFile TEXT, orderingInterFile TEXT, taskOffset INTEGER , nodes INTEGER " \
                                          ",tasks INTEGER , clientsPerNode INTEGER , repetitions INTEGER , xfersize REAL, blocksize REAL, aggregateFilesize REAL, stonewallingTime INTEGER " \
                                          ", stoneWallingWearOut INTEGER, CONSTRAINT IOFHsOptions_FK FOREIGN KEY (IOFHsTestcase_id) REFERENCES IOFHsTestcases(id));"
                con.cursor().execute(sql_create_IOFHsOptions)
            elif name == "IOFHsResults":
                sql_create_IOFHsResults = "CREATE TABLE IOFHsResults ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, IOFHsTestcase_id INTEGER NOT NULL, access TEXT, bwMiB REAL, " \
                                       "iops REAL, latency REAL, blockKiB REAL, xferKiB REAL ,openTime REAL, wrRdTime REAL, closeTime REAL , totalTime REAL " \
                                          ",iter INTEGER, CONSTRAINT IOFHsOptions_FK FOREIGN KEY (IOFHsTestcase_id) REFERENCES IOFHsTestcases(id));"
                con.cursor().execute(sql_create_IOFHsResults)
            elif name == "DarshanSummaries":
                sql_create_DarshanSummaries= "CREATE TABLE DarshanSummaries ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, meta TEXT, summary TEXT, mounts TEXT, writtenFiles TEXT);"
                con.cursor().execute(sql_create_DarshanSummaries)
            elif name == "Custom":
                sql_create_Custom = "CREATE TABLE Custom ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name_app TEXT, type TEXT, summary TEXT, sysinfo TEXT, fs TEXT);"
                con.cursor().execute(sql_create_Custom)
          #  elif name == "DarshanSummariesExtended":
           #     sql_create_DarshanSummariesExtended= "CREATE TABLE DarshanSummariesExtended ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, meta TEXT, summary TEXT, mounts TEXT, writtenFiles TEXT);"
            #    con.cursor().execute(sql_create_DarshanSummariesExtended)



def delete_tables(con):
    print(con.cursor().execute("DROP TABLE performances"))
    print(con.cursor().execute("DROP TABLE summaries"))
    print(con.cursor().execute("DROP TABLE results"))
    print(con.cursor().execute("DROP TABLE filesystems"))

    print(con.cursor().execute("DROP TABLE IOFHsResults"))
    print(con.cursor().execute("DROP TABLE IOFHsOptions"))
    print(con.cursor().execute("DROP TABLE IOFHsTestcases"))
    print(con.cursor().execute("DROP TABLE IOFHsScores"))
    print(con.cursor().execute("DROP TABLE IOFHsRuns"))
    print(con.cursor().execute("DROP TABLE IOFHs"))
    print(con.cursor().execute("DROP TABLE sysinfos"))

    print(con.cursor().execute("DROP TABLE DarshanSummaries"))
   #print(con.cursor().execute("DROP TABLE DarshanSummariesExtended"))
    print(con.cursor().execute("DROP TABLE Custom"))


def insert_custom(con, cu, fs, sy):
    sql_insert_result = '''INSERT INTO Custom
(name_app, "type", summary, sysinfo, fs)
VALUES(?, ?, ?, ?, ?);
'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (cu['name_app'], cu['type'], cu['summary'], sy, fs))
    con.commit()


def insert_IOFHs(con, iof):
    sql_insert_result = '''INSERT INTO IOFHs ("start", "end") VALUES(?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (iof.start, iof.end))
    con.commit()
    if cursor.lastrowid > 0:
        iofid = cursor.lastrowid
        insert_IOFHsRuns(con, iofid, iof)
        insert_IOFHsScores(con, iofid, iof)
        insert_sysinfos(con,iofid,iof)
        return 1


def insert_sysinfos(con, iofid, iof):
    sql_insert_result = '''INSERT INTO sysinfos (IOFH_id, name, kernel_version, processor_architecture, processor_model, processor_frequency, 
    processor_threads, processor_vendor, processor_L2, processor_L3, processor_coresPerSocket, distribution, distribution_version, memory_capacity) VALUES(
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (iofid, iof.sysinfo.name, iof.sysinfo.kernel_version, iof.sysinfo.processor_architecture, iof.sysinfo.processor_model,
                                       iof.sysinfo.processor_frequency, iof.sysinfo.processor_threads, iof.sysinfo.processor_vendor, iof.sysinfo.processor_L2,
                                       iof.sysinfo.processor_L3, iof.sysinfo.processor_coresPerSocket, iof.sysinfo.distribution, iof.sysinfo.distribution_version, iof.sysinfo.memory_capacity))
    con.commit()


def insert_IOFHsRuns(con, iofid, iof):
    sql_insert_result = '''INSERT INTO IOFHsRuns (IOFH_id, procs, version, config_hash, result_dir, mode) VALUES(?, ?, ?, ?, ?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (iofid, iof.run.procs, iof.run.version, iof.run.config_hash, iof.run.result_dir, iof.run.mode))
    con.commit()
    if cursor.lastrowid > 0:
        iofrid = cursor.lastrowid
        insert_IOFHsTestcases(con, iofrid, iof)
        return 1


def insert_IOFHsScores(con, iofid, iof):
    sql_insert_result = '''INSERT INTO IOFHsScores (IOFH_id, MD, BW, SCORE) VALUES(?,?,?,?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (iofid, iof.score.MD, iof.score.BW, iof.score.SCORE))
    con.commit()


def insert_IOFHsTestcases(con, iofrid, iof):
    for testcase in iof.testcases:
        sql_insert_result = '''INSERT INTO IOFHsTestcases (IOFHsRun_id, name, t_start, exe, stonewall, score, t_delta, t_end) VALUES(?,?,?,?,?,?,?,?);'''
        cursor = con.cursor()
        cursor.execute(sql_insert_result, (iofrid, testcase.name, testcase.t_start, testcase.exe, testcase.stonewall, testcase.score, testcase.t_delta, testcase.t_end))
        con.commit()
        if testcase.results != -1 and cursor.lastrowid > 0:
            ioftid = cursor.lastrowid
            insert_IOFHsResults(con, ioftid, testcase.results)
            insert_IOFHsOptions(con, ioftid, testcase.options)


def insert_IOFHsResults(con, ioftid, results):
    sql_insert_result = '''INSERT INTO IOFHsResults (IOFHsTestcase_id, access, bwMiB, iops, latency, blockKiB, xferKiB, openTime, wrRdTime, closeTime, totalTime, iter) 
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (ioftid, results.access, results.bwMiB, results.iops, results.latency, results.blockKiB, results.xferKiB, results.openTime, results.wrRdTime, results.closeTime, results.totalTime, results.iter))
    con.commit()


def insert_IOFHsOptions(con, ioftid, options):
    sql_insert_result = '''INSERT INTO IOFHsOptions (IOFHsTestcase_id, api, apiVersion, testFileName, access, "type", segments, orderingInaFile, orderingInterFile, taskOffset, 
    nodes, tasks, clientsPerNode, repetitions, xfersize, blocksize, aggregateFilesize, stonewallingTime, stoneWallingWearOut) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (ioftid, options.api, options.apiVersion, options.testFileName, options.access, options.type, options.segments, options.orderingInaFile, options.orderingInterFile,
                                       options.taskOffset, options.nodes, options.tasks, options.clientsPerNode, options.repetitions,options.xfersize,
                                       options.blocksize, options.aggregateFilesize, options.stonewallingTime, options.stoneWallingWearOut))
    con.commit()


def insert_filesystem(con, pm):
    sql_insert_result = '''INSERT INTO filesystems (performance_id, type, settings) VALUES(?, ?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (pm.id, pm.fs.type, pm.fs.settings))
    con.commit()

#changed Darshan
def insert_DarshanSummaries(con, meta, sum):
    sql_insert_result = '''INSERT INTO DarshanSummaries (meta, summary, mounts, writtenFiles) VALUES(?, ?, ?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (meta, sum))
    con.commit()

#def insert_DarshanSummariesExtended(con, meta, sum, mounts, writtenFiles):
 #   sql_insert_result = '''INSERT INTO DarshanSummariesExtended (meta, summary, mounts, writtenFiles) VALUES(?, ?, ?, ?);'''
  #  cursor = con.cursor()
   # cursor.execute(sql_insert_result, (meta, sum, mounts, writtenFiles))
    #con.commit()


def insert_performance(con, pm):
    sql_insert_performance = '''INSERT INTO performances (cmd, ts, te, testID, refnum, api, platform, testFileName, hintsFileName,
        deadlineForStonewall, stoneWallingWearOut, maxTimeDuration, outlierThreshold, \"options\", 
        dryRun, nodes, memoryPerTask, memoryPerNode, tasksPerNode, repetitions, multiFile, interTestDelay, 
        fsync, fsyncperwrite, useExistingTestFile, showHints,  uniqueDir, individualDataSets, singleXferAttempt, readFile, writeFile, filePerProc,
         reorderTasks, reorderTasksRandom, reorderTasksRandomSeed, randomOffset, checkWrite, checkRead, preallocate, useFileView, setAlignment, storeFileOffset, useSharedFilePointer, useStridedDatatype,
          keepFile, keepFileWithError, verbose, collective, 
          segmentCount, transferSize, blockSize, warningAsErrors) VALUES(?, ?,?,?,? ,?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    # print(sql_insert_performance)
    cursor = con.cursor()
    cursor.execute(sql_insert_performance,
                   (pm.cmd, pm.ts, pm.te, pm.parameters.testID, pm.parameters.refnum, pm.parameters.api
                    , pm.parameters.platform, pm.parameters.testFileName, pm.parameters.hintsFileName,
                    pm.parameters.deadlineForStonewall,
                    pm.parameters.stoneWallingWearOut, pm.parameters.maxTimeDuration,
                    pm.parameters.outlierThreshold, pm.parameters.options,
                    pm.parameters.dryRun, pm.parameters.nodes, pm.parameters.memoryPerTask,
                    pm.parameters.memoryPerNode, pm.parameters.tasksPerNode,
                    pm.parameters.repetitions,
                    pm.parameters.multiFile, pm.parameters.interTestDelay, pm.parameters.fsync,
                    pm.parameters.fsyncperwrite, pm.parameters.useExistingTestFile, pm.parameters.showHints,
                    pm.parameters.uniqueDir, pm.parameters.individualDataSets, pm.parameters.singleXferAttempt,
                    pm.parameters.readFile, pm.parameters.writeFile, pm.parameters.filePerProc,
                    pm.parameters.reorderTasks, pm.parameters.reorderTasksRandom,
                    pm.parameters.reorderTasksRandomSeed, pm.parameters.randomOffset,
                    pm.parameters.checkWrite,
                    pm.parameters.checkRead, pm.parameters.preallocate, pm.parameters.useFileView,
                    pm.parameters.setAlignment,
                    pm.parameters.storeFileOffset, pm.parameters.useSharedFilePointer, pm.parameters.useStridedDatatype,
                    pm.parameters.keepFile, pm.parameters.keepFileWithError,
                    pm.parameters.verbose, pm.parameters.collective, pm.parameters.segmentCount,
                    pm.parameters.transferSize, pm.parameters.blockSize, pm.parameters.warningAsErrors))
    con.commit()
    if cursor.lastrowid > 0:
        pm.id = cursor.lastrowid
        insert_summary(con, pm)
        return 1


def insert_summary(con, pm):
    sql_insert_summary = '''INSERT INTO summaries (performance_id, operation, API, TestID, ReferenceNumber, segmentCount, 
    blockSize, transferSize, numTasks, tasksPerNode, repetitions, filePerProc, reorderTasks, taskPerNodeOffset, 
    reorderTasksRandom, reorderTasksRandomSeed, bwMaxMIB, bwMinMIB, bwMeanMIB, bwStdMIB, OPsMax, OPsMin, OPsMean, OPsSD, MeanTime, xsizeMiB) 
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    # print(sql_insert_summary)
    cursor = con.cursor()
    for summary in pm.summaries:
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


def get_fs_settings():
    fs = FilesystemModel()
    with os.popen('df -T .') as stream:
        for i, line in enumerate(stream):
            if i == 1:
                if line.split()[1] == '9p':
                    pass
                elif line.split()[1] == 'beegfs':
                    bfs = get_beegfs_settings()
                    fs.name = "beegfs"
                    fs.settings = json.dumps(bfs.__dict__)
    return fs


def get_darshan(con):
    #test = 'darshan-logs/zhuz_hacc_io_id55036-55036_7-24-60888-9661464804670403708_3123.darshan'
    #report = darshan.DarshanReport(test, read_all=True)
    # report.mod_read_all_records('POSIX')
    # report.mod_read_all_records('MPI-IO')
    # or fetch all
    #report.read_all_generic_records()

    # Generate summaries for currently loaded data
    # Note: aggregations are still experimental and have to be activated:
    #darshan.enable_experimental()
    #report.summarize()
    #i = 8

    for subdir, dirs, files in os.walk("darshan-logs/"):
        for file in files:
            if file.endswith(".darshan"):
                report = darshan.DarshanReport(os.path.join(subdir, file), read_all=True)
                # report.mod_read_all_records('POSIX')
                # report.mod_read_all_records('MPI-IO')
                # or fetch all
                report.read_all_generic_records()

                # Generate summaries for currently loaded data
                # Note: aggregations are still experimental and have to be activated:
                darshan.enable_experimental()
                report.summarize()
                print(report.report)
                
                #change mounts and writtenFile path
                insert_DarshanSummaries(con=con, meta=json.dumps(report.metadata), sum=json.dumps(report.summary), mounts=json.dumps(report.mounts), writtenFiles=json.dumps(report.paths))


#def get_darshanExtended(con):
 #   for subdir, dirs, files in os.walk("darshan-logs/"):
  #      for file in files:
   #         if file.endswith(".darshan"):
    #            report = darshan.DarshanReport(os.path.join(subdir, file), read_all=True)
     #           # report.mod_read_all_records('POSIX')
      #          # report.mod_read_all_records('MPI-IO')
       #         # or fetch all
        #        report.read_all_generic_records()
#
                # Generate summaries for currently loaded data
 #               # Note: aggregations are still experimental and have to be activated:
  #              darshan.enable_experimental()
   #             report.summarize()
    #            print(report.report)
     #           i=8
      #          #need to find right path from result to mounts and paths
       #         insert_DarshanSummariesExtended(con=con, meta=json.dumps(report.metadata), sum=json.dumps(report.summary), mounts=json.dumps(report.mounts), writtenFiles=json.dumps(report.paths))



def get_beegfs_settings():
    settings = []
    with os.popen('beegfs-ctl --getentryinfo .') as stream:
        for i, line in enumerate(stream):
            if len(line.split(': ', 1)) > 1:
                settings.append(line.split(': ', 1)[1])
    print(settings[0], '\n', settings[1], '\n', settings[2], settings[3], settings[4], settings[5])
    return Beegfs(settings[0], settings[1], settings[2], settings[3], settings[4], settings[5])


def startup(mod="test", isCluster=0, rootdir="./", io500Dir="io500-log/2022.06.16-13.32.58/"):
    con = create_connection(r"../IO-Knowledge-API/pythonsqlite.db")
    if mod == 'test':
        io500 = read_io500(io500Dir)
        generate_tables(con)
        insert_IOFHs(con, io500)
    elif mod == "darshan":
        generate_tables(con)
        get_darshan(con)
    #elif mod == "darshanExtended":
     #   generate_tables(con)
      #  get_darshanExtended(con)
    elif mod == "reset":
        delete_tables(con)
    elif mod == "io500":
        io500 = read_io500(io500Dir)
        generate_tables(con)
        insert_IOFHs(con, io500)
    elif mod == "hacc":
        generate_tables(con)
        read_haccio(con)
    elif mod == 'ior':
        generate_tables(con)
        if isCluster:
            fs = get_fs_settings()
            for subdir, dirs, files in os.walk(rootdir):
                for file in files:
                    if file == 'stdout':
                        print(os.path.join(subdir, file))
                        pm = read_log(os.path.join(subdir, file), fs)
                        insert_performance(con, pm)
                        insert_filesystem(con, pm)
        else:
            for subdir, dirs, files in os.walk(rootdir):
                fs = Beegfs('1M', 'desired: 4', 'RAID0', '694-62447785-1', 'directory', 'mds01 [ID: 1]')
                for file in files:
                    if file == 'stdout':
                        print(os.path.join(subdir, file))
                        pm = read_log(os.path.join(subdir, file), fs)
                        insert_performance(con, pm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Knowledge Extractor')
    parser.add_argument('--mod', type=str,
                        help='Choose modus in following options: io500, ior, darshan ,test, reset')
    parser.add_argument('--rootDir', type=str,
                        help='Parameter for IOR Extractor - Dir where to extract the ior json')
    parser.add_argument('--isCluster', type=bool,
                        help='Parameter for IOR Extractor for Cluster & 0 for local')
    parser.add_argument('--io500Dir', type=str,
                        help='Parameter for IO500 Extractor - Dir where to extract io500 results')
    args = parser.parse_args()
    if len(sys.argv) ==1:
        #startup("test", "./", "2022.06.16-13.32.58/", 0)
        #startup("darshan")
        #startup("io500", io500Dir="io500-log/2022.06.16-13.32.58/")
        startup("hacc")
    else:
        startup(args.mod, args.isCluster, args.rootDir, args.io500Dir)

