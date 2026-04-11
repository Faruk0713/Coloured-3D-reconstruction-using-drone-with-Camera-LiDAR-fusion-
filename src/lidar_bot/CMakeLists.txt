cmake_minimum_required(VERSION 3.8)
project(lidar_bot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()