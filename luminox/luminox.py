from serial import Serial
from enum import IntEnum

# region Errors


class CommsError(Exception):
    """Exception raised for Comms error scenarios.

    Attributes:
        message -- Error Code
    """

    def __init__(self, message):
        match int(message[-1]):
            case 0:
                self.message = f"Error in communication.\nCode: {message}\nDescription: USART Receiver Overflow"
            case 1:
                self.message = f"Error in communication.\nCode: {message}\nDescription: Invalid Command"
            case 2:
                self.message = f"Error in communication.\nCode: {message}\nDescription: Invalid Frame"
            case 3:
                self.message = f"Error in communication.\nCode: {message}\nDescription: Invalid Argument"
            case _:
                self.message = f"Error in communication.\nCode: {message}"
        super().__init__(self.message)


# endregion
# region Enum


class OutputMode(IntEnum):
    """
    Enum For the standard output modes of the sensor
    """

    STREAM = 0
    POLL = 1
    OFF = 2


# endregion


class Lox(Serial):
    """
    Main object for Luminox communication

    :param Serial: Child of Serial to use all included methods as standard
    """

    def __init__(self, port_name: str):
        """
        Initialiser for Luminox communication.

        :param port_name: _description_
        :type port_name: Portname for the connection. Likely "COM*" on windows or "/dev/ttyUSB*" in Linux
        """
        self._port = port_name
        Serial.__init__(self, port=self._port, baudrate=9600, timeout=1)

        self._output_mode = OutputMode(int(self.issue_command("M")[-1]))

    # region properties

    @property
    def output_mode(self) -> OutputMode:
        """
        Get latest output mode read from sensor.

        :return: Element of Output Mode Enum
        :rtype: OutputMode
        """
        return OutputMode(self._output_mode)

    @output_mode.setter
    def output_mode(self, value: OutputMode) -> None:
        """
        Setter for sensor output mode

        :param value: Supplied as OutputMode Ennum
        :type value: OutputMode
        """
        self.issue_command(f"M {value}")
        self._output_mode = value

    @property
    def ppo2(self) -> float:
        """
        Current PPO2 reading from the sensor.

        :return: PPO2
        :rtype: float
        """
        if self.output_mode == OutputMode.STREAM:
            return self.get_stream_decoded()["O"]
        else:
            response = self.issue_command("O").split()
            return float(response[-1])

    @property
    def o2_percent(self) -> float:
        """
        Current O2 Percent reading from Sensor

        :return: O2 Percent
        :rtype: float
        """
        if self.output_mode == OutputMode.STREAM:
            return self.get_stream_decoded()["%"]
        else:
            response = self.issue_command("%").split()
            return float(response[-1])

    @property
    def temperature(self) -> float:
        """
        Current temperature reading from sensor

        :return: Temperature
        :rtype: float
        """
        if self.output_mode == OutputMode.STREAM:
            return self.get_stream_decoded()["T"]
        else:
            response = self.issue_command("T").split()
            return float(response[-1])

    @property
    def pressure(self) -> float:
        """
        Current pressure reading from sensor

        :return: Pressure
        :rtype: float
        """
        if self.output_mode == OutputMode.STREAM:
            return self.get_stream_decoded()["P"]
        else:
            response = self.issue_command("P").split()
            return float(response[-1])

    @property
    def sensor_status(self) -> str:
        """
        Current status of sensor

        :return: e Status
        :rtype: float
        """
        if self.output_mode == OutputMode.STREAM:
            return self.get_stream_decoded()["e"]
        else:
            response = self.issue_command("e").split()
            return response[-1]

    @property
    def date_of_manufacture(self) -> str:
        """
        Manufactured date of the sensor

        :return: 'YYYY DDD'
        :rtype: str
        """
        response = self.issue_command("# 0").split()
        year = int(response[1])
        day = int(response[2])
        return f"{year} {day}"

    @property
    def serial_number(self) -> int:
        """
        Sensor Serial number. Decoded from 2 registers

        :return: Serial Number
        :rtype: int
        """
        response = self.issue_command("# 1").split()
        _serial_number = (int(response[1]) << 16) + int(response[2])
        return _serial_number

    @property
    def software_revision(self) -> int:
        """
        Sensor internal software revision.

        :return: Revision Number
        :rtype: int
        """
        response = self.issue_command("# 2").split()
        return int(response[-1])

    # endregion

    # region methods
    def issue_command(self, command: str) -> str:
        """
        Issue a single command to the sensor and return the response.
        This will add or strip end characters as required from the returning string.

        :param command: Single Coimmand from 'USART Command Set'
        :type command: str
        :raises CommsError: If Error is returned exception will be raised/
        :return: _description_
        :rtype: str
        """
        self.write(f"{command}\r\n".encode())
        response = self.readline().decode().strip()
        if response[0] == "E" or not response:
            raise CommsError(response)
        else:
            return response

    def get_stream_raw(self) -> str:
        """
        Returns the raw stream from the sensor

        :return: Single stream string
        :rtype: str
        """
        if self.output_mode != OutputMode.STREAM:
            self.output_mode = OutputMode.STREAM

        self.reset_input_buffer()
        return self.readline().decode()

    def get_stream_decoded(self) -> dict[str : float | str]:
        """
        Decodes the streamed output from the sensor into a dictionary

        :return: Decoded stream
        :rtype: dict[str: float|str]
        """
        if self.output_mode != OutputMode.STREAM:
            self.output_mode = OutputMode.STREAM

        self.reset_input_buffer()
        line = self.readline().decode().strip()
        split_line = line.split(" ")
        line_dictionary = {}
        for index, i in enumerate(split_line):
            if index % 2 != 0:
                continue
            if index + 1 == len(split_line):
                break
            if i == "e":
                line_dictionary[i] = split_line[index + 1]
            else:
                line_dictionary[i] = float(split_line[index + 1])
        return line_dictionary

    # endregion
