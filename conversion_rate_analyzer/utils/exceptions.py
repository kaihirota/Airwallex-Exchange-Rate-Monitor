class SpotRateWriterError(Exception):
    """Exception raised when SpotRateWriter encounters an error while writing jsonlines.

    Attributes:
        message: explanation of the error
        path: path of the output file
    """

    def __init__(self, message="Exception encountered while writing to output.", path: str = None):
        self.message = f"{message} Output path: {path}"
        self.path = path
        super().__init__(self.message)