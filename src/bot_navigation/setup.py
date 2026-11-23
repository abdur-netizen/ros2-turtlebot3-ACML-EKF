from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'bot_navigation'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdur',
    maintainer_email='abdur@todo.todo',
    description='Autonomous waypoint navigation controller using Nav2 Simple Commander',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'waypoint_navigator = bot_navigation.waypoint_navigator:main',
        ],
    },
)
