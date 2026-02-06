cmake_minimum_required(VERSION 3.10)

# project name
project(cursorControl VERSION 0.1.1)

# secify C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

configure_file(cursorControl.h.in cursorControl.h)

# include third-party packages
set(BOOST_ROOT ".\\third_party\\boost_1_76_0") 
find_package(Boost 1.76.0 REQUIRED) 
if(Boost_FOUND)
    message(STATUS "Boost_VERSION: ${Boost_VERSION}")
    message(STATUS "Boost_INCLUDE_DIRS: ${Boost_INCLUDE_DIRS}")
    message(STATUS "Boost_LIBRARIES: ${Boost_LIBRARIES}")
    include_directories(${Boost_INCLUDE_DIR}) 
endif()

set(OpenCV_STATIC ON)
set(OpenCV_DIR "third_party\\opencv\\build")
find_package(OpenCV REQUIRED)
if(OpenCV_FOUND)
    message(STATUS "OpenCV_VERSION: ${OpenCV_VERSION}")
    message(STATUS "OpenCV_INCLUDE_DIRS: ${OpenCV_INCLUDE_DIRS}")
    message(STATUS "OpenCV_LIBRARIES: ${OpenCV_LIBS}")
    include_directories(${OpenCV_INCLUDE_DIRS})
endif()

# include subdirectories to be built
add_subdirectory(Controller)
add_subdirectory(InputBuffer)
add_subdirectory(EventProcessor)
add_subdirectory(Detector)
add_subdirectory(Engine)

# add executables
add_executable(cursorControl cursorControl.cpp)

target_link_libraries(cursorControl PUBLIC
                    Controller
                    InputBuffer
                    EventProcessor
                    Detector
                    Engine
                    ${OpenCV_LIBS}
                    )

target_include_directories(cursorControl PUBLIC
                        "${PROJECT_BINARY_DIR}"
                        "${OpenCV_INCLUDE_DIRS}"
                        )

install(TARGETS cursorControl DESTINATION bin)
install(FILES "${PROJECT_BINARY_DIR}/cursorControl.h" DESTINATION include)
