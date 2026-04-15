from pysimverse import Drone
import time

from zmq.ssh import forward

drone = Drone()
drone.connect()

drone.take_off(40)
drone.set_speed(250)
for _ in range(9):
    drone.move_forward(25)
    drone.move_right(23.3)
drone.land()
