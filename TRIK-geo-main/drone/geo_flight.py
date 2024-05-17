from pioneer_sdk import Pioneer, Camera
from math import pi
import time
import cv2
import threading
import sys

CLOCKWISE = 1
COUNTER_CLOCKWISE = -1


class CameraService():

    # TODO передать ресурсы камеры
    def __init__(self, working_dir):
        self.camera = cv2.VideoCapture(0)
        self.working_dir = working_dir

    def capture(self, event: threading.Event):
        i = 0
        while True:
            # TODO something useful
            print("tick")
            ret, frame = self.camera.read()
            cv2.imwrite(f'{self.working_dir}/frames/frame{i}.jpg', frame)
            i += 1
            time.sleep(1.0)

            if event.is_set():
                break



class Program():

    def __init__(self, working_dir):
        self.working_dir = working_dir
        self.drone = Pioneer(connection_method='serial', device='/dev/ttyS0', baud=57600, logger=True)
        self.home = [0, 0, 0]

    def start(self):
        print("Starting flight!")
        # включение светодиодов на плате автопилота (8-бит на канал)
        # self.drone.led_control(r=0, g=0, b=220)

        # включение двигателей перед полётом
        self.drone.arm()
        time.sleep(0.7)

        # взлёт
        self.drone.takeoff()
        time.sleep(2.0)

        # запоминаем координаты возврата
        self.home = self.drone.get_local_position_lps()
        print(self.home)

        # Включаем запись и передачу
        # TODO передать ресурсы камеры
        cameraService = CameraService(self.working_dir)
        event = threading.Event()
        cameraThread = threading.Thread(target=cameraService.capture, args=(event,))
        cameraThread.start()

        # делаем, что должно
        R = 1 # 1 meter
        T = 10 # 10 seconds
        # self.make_circle(R, T)
        self.make_square_area(2, 0.5)
        time.sleep(1.0)

        # останавливаем запись
        event.set()
        cameraThread.join()

        # летим домой
        self.drone.go_to_local_point(*self.home, 0)
        time.sleep(1.0)

        # посадка
        self.drone.land()
        time.sleep(2.0)

        # дизарм
        self.drone.disarm()
        self.drone.led_control(r=0, g=0, b=0)
        print("Flight finished.")

    '''
    Пролететь по окружности радиусом R и периодом T в направлении direction (по умолчани против часовой стрелки)
    '''
    def make_circle(self, R, T, direction=COUNTER_CLOCKWISE):
        assert T > 0
        omega = 2 * pi / T * direction
        vx = omega * R
        initial = time.time()
        while time.time() - initial < T:
            self.drone.set_manual_speed_body_fixed(vx, 0, 0, omega)

    '''
    Пролететь по квадрату со стороной d
    '''
    def make_square(self, d):
        assert d > 0
        [x, y, z] = self.home
        z += 2
        # self.drone.get_local_position_lps()
        self.drone.go_to_local_point(x + d, y, z, 0)
        time.sleep(3.0)
        self.drone.go_to_local_point(x + d, y + d, z, 0)
        time.sleep(3.0)
        self.drone.go_to_local_point(x, y + d, z, 0)
        time.sleep(3.0)
        self.drone.go_to_local_point(x, y, z, 0)
        time.sleep(3.0)

    '''
    Облететь рисунком zig-zag квадратную площадь со стороной d, дистанцией между прогонами l и центром в текущей точке
    '''
    def make_square_area(self, d, l):
        assert d > 0
        assert l > 0
        h = 2
        [x, y, z] = [0, 0, h]
        # начинаем облет
        n = int(d / l)
        for i in range(n):
            self.drone.go_to_local_point(d, 0, z, 0)
            self.drone.go_to_local_point(d, 2*i*l + l, z, 0)
            self.drone.go_to_local_point(0, 2*i*l + l, z, 0)
            self.drone.go_to_local_point(0, 2*i*l + 2 * l, z, 0)

if __name__ == '__main__':
    working_dir = sys.argv[1]
    program = Program(working_dir)
    program.start()


