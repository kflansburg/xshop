"""
XShop Daemon

This service runs inside of the test environment and executes test functions
as instructed by the host. It also provides a context to test functions which
includes test information and exploit tools. 
"""

class TestContext:
    """
    Object which is passed to the test function, includes test parameters and
    variables. 

    Provides additional functionality for requesting exploit related 
    information. 
    """
    def __init__(self, config):
        # Set Configuration Information
        pass

    def getROPGadget(self, search):
        """
        Allows user to request the location of ROP Gadget in memory. 
        """
        pass
    

def run_function():
    """
    POST /run?func=<function_name>
    Runs the requested function, passing it the test context object and returns
    STDOUT and STDERR
    """
    pass

if __name__=="__main__":
    # Load Available Functions
    # Start Server
    pass
