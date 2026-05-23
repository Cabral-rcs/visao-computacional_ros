import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from turtlesim_msgs.srv import TeleportAbsolute, SetPen

BASE_DIR = Path(__file__).resolve().parent.parent
POINTS_PATH = BASE_DIR / "points.txt"


class TurtleDrawer(Node):

    def __init__(self):
        super().__init__("turtle_drawer")

        self.teleport_client = self.create_client(
            TeleportAbsolute,
            "/turtle1/teleport_absolute"
        )

        self.pen_client = self.create_client(
            SetPen,
            "/turtle1/set_pen"
        )

        self.get_logger().info("Esperando serviços do turtlesim...")

        self.teleport_client.wait_for_service()
        self.pen_client.wait_for_service()

        self.get_logger().info("Serviços conectados.")

    def set_pen(self, off):
        request = SetPen.Request()
        request.r = 255
        request.g = 255
        request.b = 255
        request.width = 2
        request.off = off

        future = self.pen_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

    def teleport(self, x, y):
        request = TeleportAbsolute.Request()
        request.x = float(x)
        request.y = float(y)
        request.theta = 0.0

        future = self.teleport_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

    def draw(self):
        points = []

        if not POINTS_PATH.exists():
            self.get_logger().error(f"Arquivo não encontrado: {POINTS_PATH}")
            return

        with open(POINTS_PATH, "r") as f:
            for line in f:
                parts = line.strip().split(",")

                if len(parts) != 3:
                    continue

                x = float(parts[0])
                y = float(parts[1])
                pen = int(parts[2])

                points.append((x, y, pen))

        self.get_logger().info(f"{len(points)} pontos carregados")

        for x, y, pen in points:
            self.set_pen(pen == 0)
            self.teleport(x, y)
            time.sleep(0.001)

        self.set_pen(True)
        self.get_logger().info("Desenho concluído")


def main(args=None):
    rclpy.init(args=args)

    node = TurtleDrawer()
    node.draw()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()