from typing import List, Tuple

from sentio_prober_control.Sentio.CommandGroups.CommandGroupBase import CommandGroupBase
from sentio_prober_control.Sentio.Response import Response
from sentio_prober_control.Sentio.Enumerations import VirtualCarrierInitFlags, VirtualCarrierStepProcessingState, LoaderStation


class LoaderVirtualCarrierCommandGroup(CommandGroupBase):
    """A command group for the Virtual Carrier functionality.

    You are not meant to instantiate this class directly. Access it via the loader attribute
    of the [SentioProber](SentioProber.md) class.
    """

    def __init__(self, parent : CommandGroupBase) -> None:
        super().__init__(parent)


    def list(self) -> List[str]:
        """List all virtual carriers defined in SENTIO.

        Wraps Sentios "loader:vc:list" remote command.

        Returns:
            carriers (Tuple[str]): A tuple with the names of the virtual carriers.
        """

        try:
            self.comm.send("loader:vc:list")
            resp = Response.check_resp(self.comm.read_line())
            
            list : List[str] = resp.message().split(',')
            return list
        except:
            return []
        

    def select(self, vc_name : str) -> Response:
        """Select a virtual carrier.

        Wraps Sentios "loader:vc:select" remote command.

        Args:
            vc_name (str): The name of the virtual carrier to select.

        Returns:
            response (Response): A Response object.
        """

        self.comm.send(f"loader:vc:select {vc_name}")
        return Response.check_resp(self.comm.read_line())


    def start_load_first(self, cleanup : bool = False) -> Response:
        """Start loading the first wafer in the selected virtual carrier.
            
            This is an async command. You need to wait for the command to 
            complete.

        Wraps Sentios "loader:vc:start_load_first" remote command.

        Returns:
            resp (Response): A response object.
        """

        self.comm.send(f"loader:vc:start_load_first {cleanup}")
        resp = Response.check_resp(self.comm.read_line())
        return resp


    def initialize(self, carrier_name : str, mode : VirtualCarrierInitFlags = VirtualCarrierInitFlags.Start, timeout : int = 90) -> List[Tuple[VirtualCarrierStepProcessingState, str, LoaderStation, int, float, int]]:
        """Initializes the selected virtual carrier.
        
            Wraps Sentios "loader:vc:start_initialize" remote command. This command synchronizes the async
            start_initialize command with a wait_complete command.

            Args:
                carrier_name (str): The name of the virtual carrier to initialize. This carrier will be made SENTIO's active carrier.
                continue_process (bool): A boolean flag to indicate if a previous virtual carrier measurement shall be continued. (default is False)
                timeout (int): The timeout in seconds. (default is 90 seconds)

            Returns:
                A List of steps to execute.
        """

        self.comm.send(f"loader:vc:start_initialize {carrier_name}, {mode.toSentioAbbr()}")
        resp : Response = Response.check_resp(self.comm.read_line())

        self.prober.wait_complete(resp.cmd_id())

        # parse processing steps into a list of tuples
        steps : List[Tuple[VirtualCarrierStepProcessingState, str, LoaderStation, int, float, int]] = []

        steps_as_str : List[str] = resp.message().split(',')
        for it in steps_as_str:
            col = it.split(' ')
            
            state = VirtualCarrierStepProcessingState[col[0]]
            id = col[1]
            station = LoaderStation[col[2]]
            slot = int(col[3])
            temp = float(col[4])
            probecard_idx = int(col[5])
            steps.append((state, id, station, slot, temp, probecard_idx))

        return steps


    def next_step(self, timeout : int = 90) -> Tuple[VirtualCarrierStepProcessingState, str, LoaderStation, int, float, int]:
        """Execute the next processing step of the virtual carrier.

            Wraps Sentios "loader:vc:start_next_step" remote command.

        Returns:
            A tuple with the processing step information.
        """

        self.comm.send("loader:vc:start_next_step")
        resp : Response = Response.check_resp(self.comm.read_line())

        self.comm.send(f"wait_complete {resp.cmd_id()}, {timeout}")
        Response.check_resp(self.comm.read_line())

        col = resp.message().split(',')
        state = VirtualCarrierStepProcessingState[col[0]]
        id = col[1]
        station = LoaderStation[col[2]]
        slot = int(col[3])
        temp = float(col[4])
        probecard_idx = int(col[5])

        return (state, id, station, slot, temp, probecard_idx)
    

    def load_first(self, cleanup : bool = False, timeout : int = 90) -> None:
        """Loads the first wafer of the virtual carrier. This is a blocking version of the start_load_first method.
            
            Wraps Sentios "loader:vc:start_load_first" remote command.

            Args:
                cleanup (bool): A boolean flag to indicate the wafer on the chuck shall be returned to its origin
                timeour (int): The timeout in seconds. (default is 90 seconds
        """

        resp : Response = self.start_load_first(cleanup)
        self.comm.send(f"wait_complete {resp.cmd_id()}, {timeout}")
        Response.check_resp(self.comm.read_line())


    def start_load_next(self) -> Response:
        """Start loading the next wafer in the selected virtual carrier.
            
            This is an async command. You need to wait for the command to 
            complete.

            Wraps Sentios "loader:vc:start_load_next" remote command.

        Returns:
            resp (Response): A response object.
        """

        self.comm.send(f"loader:vc:start_load_next")
        resp = Response.check_resp(self.comm.read_line())
        return resp
    
    
    def load_next(self, timeout : int = 90) -> None:
        """Loads the first wafer of the virtual carrier. This is a blocking version of the start_load_first method.
            
            Wraps Sentios "loader:vc:start_load_first" remote command.

            Args:
                cleanup (bool): A boolean flag to indicate the wafer on the chuck shall be returned to its origin
                timeour (int): The timeout in seconds. (default is 90 seconds
        """

        resp : Response = self.start_load_next()
        self.comm.send(f"wait_complete {resp.cmd_id()}, {timeout}")
        Response.check_resp(self.comm.read_line())
