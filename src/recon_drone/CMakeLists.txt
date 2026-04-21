cmake_minimum_required(VERSION 3.8)
project(recon_drone)
find_package(ament_cmake REQUIRED)
install(DIRECTORY urdf launch config scripts
  DESTINATION share/${PROJECT_NAME}
)
ament_package()
