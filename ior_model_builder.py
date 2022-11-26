import json
import copy
from typing_extensions import Self

#from symbol import test


class Parameters:
    def __init__(self, testID, refnum, api, platform, testFileName,  deadlineForStonewall, stoneWallingWearOut,
                 maxTimeDuration, outlierThreshold,
                 options, dryRun, nodes, memoryPerTask, memoryPerNode, tasksPerNode, repetitions, multiFile,
                 interTestDelay, fsync, fsyncperwrite, useExistingTestFile,  uniqueDir,  singleXferAttempt,
                 readFile, writeFile, filePerProc, reorderTasks, reorderTasksRandom, reorderTasksRandomSeed,
                 randomOffset, checkWrite, checkRead, keepFile, keepFileWithError, quitOnError,
                 verbose, collective, segmentCount, transferSize,
                 blockSize, hintsFileName="", showHints=-1, individualDataSets=-1, preallocate=-1, useFileView=-1,
                 setAlignment=-1, storeFileOffset=-1, useSharedFilePointer=-1, useStridedDatatype=-1, warningAsErrors=-1):
        self.testID = testID
        self.refnum = refnum
        self.api = api
        self.platform = platform
        self.testFileName = testFileName
        self.hintsFileName = hintsFileName
        self.deadlineForStonewall = deadlineForStonewall
        self.stoneWallingWearOut = stoneWallingWearOut
        self.maxTimeDuration = maxTimeDuration
        self.outlierThreshold = outlierThreshold
        self.options = options
        self.dryRun = dryRun
        self.nodes = nodes
        self.memoryPerTask = memoryPerTask
        self.memoryPerNode = memoryPerNode
        self.tasksPerNode = tasksPerNode
        self.repetitions = repetitions
        self.multiFile = multiFile
        self.interTestDelay = interTestDelay
        self.fsync = fsync
        self.fsyncperwrite = fsyncperwrite
        self.useExistingTestFile = useExistingTestFile
        self.showHints =  showHints
        self.uniqueDir = uniqueDir
        self.individualDataSets = individualDataSets
        self.singleXferAttempt = singleXferAttempt
        self.readFile = readFile
        self.writeFile = writeFile
        self.filePerProc = filePerProc
        self.reorderTasks = reorderTasks
        self.reorderTasksRandom = reorderTasksRandom
        self.reorderTasksRandomSeed = reorderTasksRandomSeed
        self.randomOffset = randomOffset
        self.checkWrite = checkWrite
        self.checkRead = checkRead
        self.preallocate = preallocate
        self.useFileView = useFileView
        self.setAlignment = setAlignment
        self.storeFileOffset = storeFileOffset
        # self.dataPacketType = dataPacketType
        self.useSharedFilePointer = useSharedFilePointer
        self.useStridedDatatype = useStridedDatatype
        self.keepFile = keepFile
        self.keepFileWithError = keepFileWithError
        self.quitOnError = quitOnError
        self.verbose = verbose
#        self.data_packet_type = data_packet_type
#       self.setTimeStampSignature_incompressibleSeed = setTimeStampSignature_incompressibleSeed
        self.collective = collective
        self.segmentCount = segmentCount
        self.transferSize = transferSize
        self.blockSize = blockSize
        self.warningAsErrors = warningAsErrors

    def ParametersToJSON(self):
        return json.dumps(self.__dict__)


    # @staticmethod
    # def create_from_json(json_dictionary):
    #     # json_dictionary = json.loads(data.read())
    #     p = json_dictionary['tests'][0]['Parameters']
    #     return Parameters(**p)


class Summary:
    def __init__(self, operation, API, TestID, ReferenceNumber, segmentCount, blockSize, transferSize, numTasks,
                 tasksPerNode, repetitions, filePerProc, reorderTasks, taskPerNodeOffset, reorderTasksRandom,
                 reorderTasksRandomSeed,
                 bwMaxMIB, bwMinMIB, bwMeanMIB, bwStdMIB, OPsMax, OPsMin, OPsMean, OPsSD, MeanTime, xsizeMiB):
        self.operation = operation
        self.API = API
        self.TestID = TestID
        self.ReferenceNumber = ReferenceNumber
        self.segmentCount = segmentCount
        self.blockSize = blockSize
        self.transferSize = transferSize
        self.numTasks = numTasks
        self.tasksPerNode = tasksPerNode
        self.repetitions = repetitions
        self.filePerProc = filePerProc
        self.reorderTasks = reorderTasks
        self.taskPerNodeOffset = taskPerNodeOffset
        self.reorderTasksRandom = reorderTasksRandom
        self.reorderTasksRandomSeed = reorderTasksRandomSeed
        self.bwMaxMIB = bwMaxMIB
        self.bwMinMIB = bwMinMIB
        self.bwMeanMIB = bwMeanMIB
        self.bwStdMIB = bwStdMIB
        self.OPsMax = OPsMax
        self.OPsMin = OPsMin
        self.OPsMean = OPsMean
        self.OPsSD = OPsSD
        self.MeanTime = MeanTime
        self.xsizeMiB = xsizeMiB
    
    def SummaryToJSON(self):
        return json.dumps(self.__dict__)

    # @staticmethod
    # def create_from_json(json_dictionary):
    #     summaries = []
    #     for summary in json_dictionary['summary']:
    #         summaries.append(Summary(**summary))
    #     return summaries


class Result:
    def __init__(self, access, bwMiB, blockKiB, xferKiB, iops, latency, openTime, wrRdTime,
                 closeTime, totalTime):
        self.access = access
        self.bwMiB = bwMiB
        self.blockKiB = blockKiB
        self.xferKiB = xferKiB
        self.iops = iops
        self.latency = latency
        self.openTime = openTime
        self.wrRdTime = wrRdTime
        self.closeTime = closeTime
        self.totalTime = totalTime

    def ResultToJSON(self):
        r = {
            "access": self.access,
            "bwMiB": self.bwMiB,
            "blockKiB": self.blockKiB,
            "xferKiB": self.xferKiB,
            "iops": self.iops,
            "latency": self.latency,
            "openTime": self.openTime,
            "wrRdTime": self.wrRdTime,
            "closeTime": self.closeTime,
            "totalTime": self.totalTime
        }

    # @staticmethod
    # def create_from_json(json_dictionary):
    #     results = []
    #     for result in json_dictionary['tests'][0]['Results']:
    #         results.append(Result(**result))
    #     return results


class Test:
    def __init__(self, test_id, start_time, path, used_capacity, inodes, used_inodes, parameters, options,
                 results, finished):
        self.TestID = test_id
        self.StartTime = start_time
        self.Path = path
        self.Used_Capacity = used_capacity
        self.Inodes = inodes
        self.Used_Inodes = used_inodes
        self.Parameters = parameters
        self.Options = options
        self.Results = results
        self.Finished = finished
    
    def TestToJSON(self):
        return {"TestID": self.TestID, "StartTime": self.StartTime, "Path":self.Path, "Used_Capacity": self.Used_Capacity, "Inodes": self.Inodes, "Used_Inodes": self.Used_Inodes, "Parameters": self.Parameters, "Options": self.Options, "Results": self.Results, "Finished": self.Finished}


class Builder:
    def create_from_json(json_dictionary, fs):
        # print(json_dictionary)
        results = []
        summaries = []
        # for result in json_dictionary['tests'][0]['Results']:
        for result_s in json_dictionary['tests'][0]['Results']:
            for result in result_s:
                #print(result)
                results.append(Result(**result))
        for summary in json_dictionary['summary']:
            summaries.append(Summary(**summary))
        p = json_dictionary['tests'][0]['Parameters']
        p.pop('data packet type')
        p.pop('setTimeStampSignature/incompressibleSeed')
        cmd = json_dictionary['Command line']
        ts = json_dictionary['Began']
        te = json_dictionary['Finished']
        return PerformanceModel(cmd, ts, te, Parameters(**p), summaries, results, fs)


class PerformanceModel:
    def __init__(self, cmd, ts, te, parameters, summaries, results, fs):
        self.id = 0
        self.cmd = cmd
        self.ts = ts
        self.te = te
        self.parameters = parameters
        self.summaries = summaries
        self.results = results
        self.fs = fs
    
    def PerformanceModel(self):
        return {"ID": self.id, "cmd": self.cmd, "ts": self.ts, "te": self.te, "parameters": self.parameters, "summaries": self.summaries, "results": self.results, "fs": self.fs}


class FilesystemModel:
    def __init__(self, type="", settings=""):
        self.type = type
        self.settings = settings
    
    def FileSystemModeltoJSON(self):
        return {"Type": self.type, "Settigns": self.settings}


class Beegfs:
    def __init__(self, entryType, entryID, metadataNode, StripePatternType, StripePatternChunkSize, StripePatternStoragePool):
        self.entryType = entryType
        self.entryID = entryID
        self.metadataNode = metadataNode
        self.StripePatternType = StripePatternType
        self.StripePatternChunkSize = StripePatternChunkSize
        self.StripePatternStoragePool = StripePatternStoragePool
    
    def Beegfs(self):
        return {"EntryType": self.entryType, "EntryID": self.entryID, "metadataNode": self.metadataNode, "StripePatternType": self.StripePatternType, "StripePatternChunkSize": self.StripePatternChunkSize, "StripePatternStoragePool": self.StripePatternStoragePool}

class Testcase:
    def __init__(self, name, t_start, exe, score, t_delta, t_end, stonewall =-1, opt=-1, results=-1):
        self.name = name
        self.t_start = t_start
        self.exe = exe
        self.score = score
        self.t_delta = t_delta
        self.t_end = t_end
        self.stonewall = stonewall
        self.options = opt
        self.results = results
    
    def TestCaseToJSON(self):
        if isinstance(self.options, dict) or self.results == -1:
            read = [{"Name": self.name,
                "t_start": self.t_start,
                "exe": self.exe,
                "score": self.score,
                "t_delta": self.t_delta,
                "t_end": self.t_end,
                "stonewall": self.stonewall,
                "options": self.options,
                "results": self.results
                }]
            return read
        else:
            write = [{"Name": self.name,
                "t_start": self.t_start,
                "exe": self.exe,
                "score": self.score,
                "t_delta": self.t_delta,
                "t_end": self.t_end,
                "stonewall": self.stonewall,
                "options": json.loads(self.options.IO500OptionsToJSON()),
                "results": json.loads(self.results.IO500ResultsToJSON())
                }]
            return write


class Score:
    def __init__(self, MD, BW, score, hash):
        self.MD = MD
        self.BW = BW
        self.SCORE = score
        self.hash = hash
    
    def ScoreToJSON(self):
        return [{"MD": self.MD, "BW": self.BW, "Score": self.SCORE, "hash": self.hash}]

class Run:
    def __init__(self, procs, version, config_hash, result_dir, mode):
        self.procs = procs
        self.version = version
        self.config_hash = config_hash
        self.result_dir = result_dir
        self.mode = mode

    def RunToJSON(self):
        return [{"Procs": self.procs, "Version": self.version, "Config_Hash": self.config_hash, "Result_Dir": self.result_dir, "Mode": self.mode}]

class IO500:
    def __init__(self, run, testcases, score, start, end, sysinfo):
        self.run = run
        self.testcases = testcases
        self.score = score
        self.start = start
        self.end = end
        self.sysinfo = sysinfo
    
    def io500ToJSON(self):
        io500 = {
            "Run": self.run.RunToJSON(),
            "Testcases": self.getTestcaseJSON(),
            "Score": self.score.ScoreToJSON(),
            "Start": self.start,
            "End": self.end,
            "SysInfo": self.sysinfo.SysmodelToJSON()
        }

        return [io500]
    
    def getTestcaseJSON(self):
        tcs = []
        count = 0
        for t in self.testcases:
            tcs.append( t.TestCaseToJSON())
        
        return tcs
