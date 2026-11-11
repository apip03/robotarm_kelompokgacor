import math
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

JOINTS = ["base", "shoulder", "elbow", "wrist", "gripper_servo"]
WAYPOINTS_DEG = [(0, 0, 0, 0, 0), (90, 60, 60, 60, 30), (0, 0, 0, 0, 0)]
SEGMENT_S = 3


def main():
    rclpy.init()
    node = Node("send_trajectory")
    client = ActionClient(node, FollowJointTrajectory, "/arm_controller/follow_joint_trajectory")
    node.get_logger().info("Menunggu arm_controller ...")
    client.wait_for_server()

    goal = FollowJointTrajectory.Goal()
    goal.trajectory.joint_names = JOINTS
    for k, wp in enumerate(WAYPOINTS_DEG, start=1):
        pt = JointTrajectoryPoint()
        pt.positions = [math.radians(v) for v in wp]
        pt.velocities = [0.0] * len(JOINTS)
        pt.time_from_start = Duration(sec=SEGMENT_S * k)
        goal.trajectory.points.append(pt)

    fut = client.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, fut)
    handle = fut.result()
    if not handle.accepted:
        node.get_logger().error("Goal ditolak (cek nama joint dan batas)")
    else:
        res = handle.get_result_async()
        rclpy.spin_until_future_complete(node, res)
        node.get_logger().info(f"Selesai, error_code = {res.result().result.error_code}")
    rclpy.shutdown()


if __name__ == "__main__":
    main()
