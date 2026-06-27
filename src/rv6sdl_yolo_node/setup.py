from setuptools import setup
import os
from glob import glob

package_name = 'rv6sdl_yolo_node'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'),
            glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Abdeldjalil',
    author_email='you@example.com',
    description='YOLO11 Detection Node for RV-6SDL',
    license='MIT',
    entry_points={
        'console_scripts': [
            'yolo_node = rv6sdl_yolo_node.yolo_detection_node:main',
        ],
    },
)
