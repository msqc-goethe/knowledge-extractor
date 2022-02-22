class IorOptionsModel:
    def __init__(self, api, apiVersion, testFileName, access, type, segments, orderingInaFile, nodes, tasks, clientsPerNode, repetitions, xfersize, blocksize, aggregateFilesize):
        self.api = api
        self.apiVersion = apiVersion
        self.testFileName = testFileName
        self.access = access
        self.type = type
        self.segments = segments
        self.orderingInaFile = orderingInaFile
        self.nodes = nodes
        self.tasks = tasks
        self.clientsPerNode = clientsPerNode
        self.repetitions = repetitions
        self.xfersize = xfersize
        self.blocksize = blocksize
        self.aggregateFilesize = aggregateFilesize

