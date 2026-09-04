import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'amar_simulation'

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

model_files = package_files('models')
model_data_files = []
for file in model_files:
    # Target directory path inside the install folder
    install_dir = os.path.join('share', package_name, os.path.dirname(file))
    model_data_files.append((install_dir, [file]))


data_files_list = [
         ('share/ament_index/resource_index/packages',
             ['resource/' + package_name]),
         ('share/' + package_name, ['package.xml']),
         (os.path.join('share', package_name, 'launch'),
             glob('launch/*.py')),
         # [(os.path.join('share', package_name, root), [os.path.join(root, f) for f in files]) for root, dirs, files in os.walk('models') if files],
         (os.path.join('share', package_name, 'rviz/'),
             glob('rviz/*.rviz')),
         (os.path.join('share', package_name, 'urdf/'),
             glob('urdf/*.urdf.xacro')),
         (os.path.join('share', package_name, 'worlds/'),
             glob('worlds/*.world')),
         (os.path.join('share', package_name, 'params/'),
                 glob('params/*.yaml')),
    ]

data_files_list.extend(model_data_files)

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files_list,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lenovoi',
    maintainer_email='bhagabantagiri@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
