# Basic script to read O2 values continually

from serial import Serial
from time import sleep

lox = Serial("COM5")


lox.write("M 1\r\n".encode())

sleep(1)
lox.flushInput()

while True:
    lox.write("%\r\n".encode())
    resp = lox.readline().decode().split()
    resp = resp[-1]

    fltO2 = float(resp)
    print("O2 % = ", fltO2)

    sleep(1)
