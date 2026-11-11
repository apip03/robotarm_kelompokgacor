from setuptools import setup

package_name = "robotic_arm_pjbl_control"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    entry_points={"console_scripts": [
        "send_trajectory = robotic_arm_pjbl_control.send_trajectory:main",
    ]},
)
