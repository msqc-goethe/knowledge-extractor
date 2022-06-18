

class I0500OptionsModel:
    def __init__(self, api, apiVersion, testFileName, access, type, segments, orderingInaFile, orderingInterFile, taskOffset, nodes,
                 tasks, clientsPerNode, repetitions, xfersize, blocksize, aggregateFilesize, stonewallingTime =-1, stoneWallingWearOut=-1):
        self.api = api
        self.apiVersion = apiVersion
        self.testFileName = testFileName
        self.access = access
        self.type = type
        self.segments = segments
        self.orderingInaFile = orderingInaFile
        self.orderingInterFile = orderingInterFile
        self.taskOffset = taskOffset
        self.nodes = nodes
        self.tasks = tasks
        self.clientsPerNode = clientsPerNode
        self.repetitions = repetitions
        self.xfersize = xfersize
        self.blocksize = blocksize
        self.aggregateFilesize = aggregateFilesize
        self.stonewallingTime = stonewallingTime
        self.stoneWallingWearOut = stoneWallingWearOut


class IO500ResultsModel:
    def __init__(self, access, bwMiB, iops, latency, blockKiB, xferKiB, openTime, wrRdTime, closeTime, totalTime, iter):
        self.access = access
        self.bwMiB = bwMiB
        self.iops = iops
        self.latency = latency
        self.blockKiB = blockKiB
        self.xferKiB = xferKiB
        self.openTime = openTime
        self.wrRdTime = wrRdTime
        self.closeTime = closeTime
        self.totalTime = totalTime
        self.iter = iter

