class IorRunModel:
    def __init__(self, tBegan, commandLine, machine, testId, tStart, path, fs, options):
        self.tBegan = tBegan
        self.commandLine = commandLine
        self.machine = machine
        self.testId = testId
        self.tStart = tStart
        self.path = path
        self.fs = fs
        self.options = options
