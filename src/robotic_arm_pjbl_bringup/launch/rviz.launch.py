from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    rviz_file = PathJoinSubstitution(
        [FindPackageShare("robotic_arm_pjbl_description"), "rviz", "display.rviz"])
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true",
                              description="true jika melihat Gazebo, false jika melihat mock"),
        Node(package="rviz2", executable="rviz2", arguments=["-d", rviz_file],
             parameters=[{"use_sim_time": ParameterValue(LaunchConfiguration("use_sim_time"), value_type=bool)}]),
    ])
