cmake_minimum_required(VERSION 2.8.3)
project(pyzmp)

# Minimal Python module setup - catkin is assumed preinstalled along with ROS
# This assume catkin is installed along with a minimal ROS system.
find_package(catkin REQUIRED COMPONENTS
    catkin_pip
)

# We need to install the pip dependencies in the workspace being created
catkin_pip_requirements(${CMAKE_CURRENT_SOURCE_DIR}/dev-requirements.txt --ignore-installed)

# defining current package as a package that should be managed by pip (not catkin - even though we make it usable with workspaces)
catkin_pip_setup()
catkin_package()

## Unit tests
if (CATKIN_ENABLE_TESTING)

    ############
    # Nose Tests
    ############

    catkin_add_pytests(pyzmp/tests)

endif()
