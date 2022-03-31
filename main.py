import sys
import os
import json
import argparse
from ior_model_builder import Builder, PerformanceModel, Summary, Beegfs, FilesystemModel
import sqlite3
from sqlite3 import Error

sys.path.append(".")


def read_log(path, fs):
    with open(path) as json_file:
        json_dictionary = json.loads(json_file.read())
        pm = Builder.create_from_json(json_dictionary,fs)
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
    cur = con.cursor()
    tns = ["performances", "summaries", "results", "filesystems"]
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
                #print(sql_create_performances)
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
                                     "CONSTRAINT results_FK FOREIGN KEY (performance_id) REFERENCES performances(id));"
                con.cursor().execute(sql_create_filesystems)


def delete_tables(con):
    print(con.cursor().execute("DROP TABLE performances"))
    print(con.cursor().execute("DROP TABLE summaries"))
    print(con.cursor().execute("DROP TABLE results"))
    print(con.cursor().execute("DROP TABLE filesystems"))


def insert_filesystem(con, pm):
    sql_insert_result = '''INSERT INTO filesystems (performance_id, type, settings) VALUES(?, ?, ?);'''
    cursor = con.cursor()
    cursor.execute(sql_insert_result, (pm.id, pm.fs.type, pm.fs.settings))
    con.commit()


def insert_performance(con, pm):
    sql_insert_performance = '''INSERT INTO performances (cmd, ts, te, testID, refnum, api, platform, testFileName, hintsFileName,
        deadlineForStonewall, stoneWallingWearOut, maxTimeDuration, outlierThreshold, \"options\", 
        dryRun, nodes, memoryPerTask, memoryPerNode, tasksPerNode, repetitions, multiFile, interTestDelay, 
        fsync, fsyncperwrite, useExistingTestFile, showHints,  uniqueDir, individualDataSets, singleXferAttempt, readFile, writeFile, filePerProc,
         reorderTasks, reorderTasksRandom, reorderTasksRandomSeed, randomOffset, checkWrite, checkRead, preallocate, useFileView, setAlignment, storeFileOffset, useSharedFilePointer, useStridedDatatype,
          keepFile, keepFileWithError, verbose, collective, 
          segmentCount, transferSize, blockSize, warningAsErrors) VALUES(?, ?,?,?,? ,?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    #print(sql_insert_performance)
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


def get_beegfs_settings():
    settings = []
    with os.popen('beegfs-ctl --getentryinfo .') as stream:
        for i, line in enumerate(stream):
            if len(line.split(': ', 1)) > 1:
                settings.append(line.split(': ', 1)[1])
    print(settings[0],'\n',settings[1], '\n', settings[2], settings[3], settings[4], settings[5])
    return Beegfs(settings[0], settings[1], settings[2], settings[3], settings[4], settings[5])


def startup(flag, con, mod):
    if flag:
        parser = argparse.ArgumentParser(description='file system')
        parser.add_argument('-j', type=str,
                            help='Path to IOR json output')
        args = parser.parse_args()
        print(args.j)
        if args.j is not None:
            pm = read_log(args.j)
        else:
            pm = read_log('ior_sample_i4.json')
        if 0:
            delete_tables(con)
        else:
            generate_tables(con)
            insert_performance(con, pm)
    else:
        if 0:
            delete_tables(con)
        else:
            if mod == "cluster":
                fs = get_fs_settings()
                generate_tables(con)
                rootdir = '.'
                for subdir, dirs, files in os.walk(rootdir):
                    for file in files:
                        if file == 'stdout':
                            print(os.path.join(subdir, file))
                            pm = read_log(os.path.join(subdir, file), fs)
                            insert_performance(con, pm)
                            insert_filesystem(con, pm)
            else:
                generate_tables(con)
                rootdir = '.'
                for subdir, dirs, files in os.walk(rootdir):
                    for file in files:
                        if file == 'stdout':
                            print(os.path.join(subdir, file))
                            pm = read_log(os.path.join(subdir, file))
                            insert_performance(con, pm)



if __name__ == '__main__':
    con = create_connection(r"pythonsqlite.db")
    startup(0, con, "cluster")
