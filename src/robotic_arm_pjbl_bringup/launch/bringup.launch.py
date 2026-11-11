import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

DESC_PKG = "robotic_arm_pjbl_description"
BRINGUP_PKG = "robotic_arm_pjbl_bringup"


def generate_launch_description():
    use_sim = LaunchConfiguration("use_sim")
    rviz = LaunchConfiguration("rviz")
    world = LaunchConfiguration("world")
    sim_time = ParameterValue(use_sim, value_type=bool)

    controllers = PathJoinSubstitution([FindPackageShare(BRINGUP_PKG), "config", "controllers.yaml"])
    xacro_file = PathJoinSubstitution([FindPackageShare(DESC_PKG), "urdf", "robotic_arm_pjbl.urdf.xacro"])
    rviz_file = PathJoinSubstitution([FindPackageShare(DESC_PKG), "rviz", "display.rviz"])
    default_world = PathJoinSubstitution([FindPackageShare(BRINGUP_PKG), "worlds", "arm_world.sdf"])

    robot_description = ParameterValue(Command([
        FindExecutable(name="xacro"), " ", xacro_file,
        " use_sim:=", use_sim, " controllers_file:=", controllers]), value_type=str)

    def spawner(name):
        return Node(package="controller_manager", executable="spawner",
                    arguments=[name, "--controller-manager-timeout", "60"],
                    parameters=[{"use_sim_time": sim_time}])

    return LaunchDescription([
        DeclareLaunchArgument("use_sim", default_value="false", description="true = Gazebo, false = mock"),
        DeclareLaunchArgument("rviz", default_value="true", description="buka RViz atau tidak"),
        DeclareLaunchArgument("world", default_value=default_world, description="file world Gazebo"),

        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH",
            os.path.dirname(get_package_share_directory(DESC_PKG))),

        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": robot_description, "use_sim_time": sim_time}]),

        # mode mock hardware
        Node(package="controller_manager", executable="ros2_control_node",
             parameters=[controllers],
             remappings=[("~/robot_description", "/robot_description")],
             condition=UnlessCondition(use_sim)),

        # mode Gazebo Harmonic
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])),
            launch_arguments={"gz_args": ["-r ", world], "on_exit_shutdown": "true"}.items(),
            condition=IfCondition(use_sim)),
        Node(package="ros_gz_sim", executable="create",
             arguments=["-topic", "robot_description", "-name", "robotic_arm_pjbl"],
             condition=IfCondition(use_sim)),
        Node(package="ros_gz_bridge", executable="parameter_bridge",
             arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
             condition=IfCondition(use_sim)),

        spawner("joint_state_broadcaster"),
        spawner("arm_controller"),

        Node(package="rviz2", executable="rviz2", arguments=["-d", rviz_file],
             parameters=[{"use_sim_time": sim_time}], condition=IfCondition(rviz)),
    ])
