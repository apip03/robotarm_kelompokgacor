import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ryandaffa/robotic_arm_pjbl_ws/install/robotic_arm_pjbl_control'
