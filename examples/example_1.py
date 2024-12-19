from luminox.luminox import Lox, OutputMode
from time import sleep

if __name__ == "__main__":
    lox = Lox("COM5")

    print(f"{lox.output_mode = }")

    lox.output_mode = OutputMode.POLL

    print(f"{lox.output_mode = }")
    print(f"{lox.ppo2 = }")
    print(f"{lox.o2_percent = }")
    print(f"{lox.temperature = }")
    print(f"{lox.pressure = }")
    print(f"{lox.sensor_status = }")
    print(f"{lox.date_of_manufacture = }")
    print(f"{lox.serial_number = }")
    print(f"{lox.software_revision = }")

    sleep(1)

    lox.output_mode = OutputMode.STREAM

    sleep(1)
    print(f"{lox.output_mode = }")
    print(f"{lox.ppo2 = }")
    print(f"{lox.o2_percent = }")
    print(f"{lox.temperature = }")
    print(f"{lox.pressure = }")
    print(f"{lox.sensor_status = }")
    print(f"{lox.date_of_manufacture = }")
    print(f"{lox.serial_number = }")
    print(f"{lox.software_revision = }")

    sleep(1)

    lox.output_mode = OutputMode.POLL

    print(f"{lox.output_mode = }")

    for i in range(5):
        print(lox.get_stream_raw())
        print(lox.get_stream_decoded())

    print(f"{lox.output_mode = }")
