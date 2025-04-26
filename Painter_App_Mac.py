import sys
import os
import time
import serial
import serial.tools.list_ports
import numpy as np
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget

# Ensure proper scaling on macOS Retina displays
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Check for typical Arduino identifiers on macOS:
        # "Arduino" and "CH340" in the description,
        # or device names like "usbmodem" (official boards) or "wchusbserial" (clones)
        if ("Arduino" in port.description or
            "CH340" in port.description or
            "usbmodem" in port.device or
            "wchusbserial" in port.device):
            return port.device  # e.g. "/dev/cu.usbmodemXXXX" or "/dev/cu.wchusbserialXXXX"
    return None

arduino_port = find_arduino()
if arduino_port:
    print(f"Arduino found on port: {arduino_port}")
else:
    print("No Arduino detected.")

# --------------------------------------------- COMMUNICATION -------------------------------------------------- #

def send_serial_data(ser, message):
    if ser and ser.is_open:
        ser.write(message.encode())  # Convert message to bytes
        ser.flush()  # Ensure the data is sent immediately
        time.sleep(0.05)
        received = read_serial_data(ser)
        # If the response is not "ACK", print it and try resending
        if received != "ACK":
            print("Received:", received)
            send_serial_data(ser, message)
        print("Received:", received)
    else:
        print("Error: Serial port not open!")

def read_serial_data(ser):
    if ser and ser.is_open and ser.in_waiting > 0:
        received_data = ser.readline()  # Read until newline
        if received_data:
            return received_data.decode(errors="replace").strip()
    return None

# ---------------------------------------- PAINT_APP -------------------------------------------------- #

class PaintApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painter App")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # Lists to store coordinates
        self.x_coords = []
        self.y_coords = []

        # Try to open the serial connection if an Arduino port was found
        self.ser = None
        if arduino_port is not None:
            try:
                self.ser = serial.Serial(arduino_port, 9600, timeout=1)
                time.sleep(2)  # Allow time for the Arduino to reset on connection
            except serial.SerialException as e:
                print(f"Error: {e}")
                self.ser = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.x_coords.append(event.x())
            # Invert y coordinate to match a common coordinate system (origin at bottom left)
            self.y_coords.append(self.height() - event.y())
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        # Draw trajectory if there are at least 2 points
        if len(self.x_coords) > 1:
            for i in range(1, len(self.x_coords)):
                painter.drawLine(QPoint(self.x_coords[i-1], self.height() - self.y_coords[i-1]),
                                 QPoint(self.x_coords[i], self.height() - self.y_coords[i]))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.x_coords = []
            self.y_coords = []
            self.update()
        elif event.key() == Qt.Key_S:
            self.send_coords()

    def send_coords(self):
        """Sends the downsampled coordinates via serial and saves them to a file."""
        # Downsample and adjust coordinates according to the assumed range
        x_send = list(np.round(np.array(self.x_coords) * 10 / 800, 2))
        y_send = list(np.round(np.array(self.y_coords) * 6 / 600 + 10, 2))

        # Save the trajectory points to a text file
        with open("trajectory_points.txt", "w") as file:
            for x, y in zip(x_send, y_send):
                file.write(f"{x},{y}\n")

        # Send each coordinate pair over the serial port
        for x, y in zip(x_send, y_send):
            # Use "\n" (or "\r\n" if your Arduino expects Windows-style line endings)
            message = f"{x},{y}\n"
            send_serial_data(self.ser, message)
            time.sleep(0.1)  # Short delay to maintain stability

        # Signal the end of transmission
        send_serial_data(self.ser, "stop\n")

# ------------------------------------- MAIN ------------------------------------------ #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec_())