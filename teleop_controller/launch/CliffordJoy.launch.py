import os   

from launch_ros.actions import Node
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time') #look more into
    


    joy_params = os.path.join(get_package_share_directory('teleop_controller'),'config','joystick.yaml')
    
    #launch joy node.
    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[
            joy_params, 
            {'use_sim_time':use_sim_time}
            ]
    )

    CliffordJoy_teleop = Node(
        package='teleop_controller',
        executable='CliffordJoy',
        parameters=[
            {'use_sim_time':use_sim_time}
            ]


    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='false',
                description='use sim time if true'
            ),
            joy_node,
            CliffordJoy_teleop

        ]
    )