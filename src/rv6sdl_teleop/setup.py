from setuptools import find_packages, setup

package_name = 'rv6sdl_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdeldjalil-dhm',
    maintainer_email='abdeldjalil-dhm@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'teleop_node = rv6sdl_teleop.teleop_node:main',
        'cr2da_teleop_node = rv6sdl_teleop.cr2da_teleop_node:main',
        'cr2da_bridge_node = rv6sdl_teleop.cr2da_bridge_node:main',
    ],
},
)
