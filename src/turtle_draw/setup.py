from setuptools import setup

package_name = 'turtle_draw'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rafael',
    maintainer_email='rafael@email.com',
    description='Turtle Draw',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'draw_turtle = turtle_draw.draw_turtle:main',
        ],
    },
)