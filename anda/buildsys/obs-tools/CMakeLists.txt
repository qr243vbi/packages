cmake_minimum_required(VERSION 3.16)

project(obs_tools LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core Xml Qml Gui Widgets)

add_executable(obs_tools
    obs_tools.h
    obs_tools.cpp
)

add_library(obs_edit
    SHARED
    obs_edit.qrc
    obs_edit.h
    obs_edit.cpp
)

target_link_libraries(obs_tools
    Qt6::Core
    Qt6::Xml
)

target_link_libraries(obs_edit
    Qt6::Core
    Qt6::Xml
    Qt6::Qml
    Qt6::Gui
    Qt6::Widgets
)


install(
    PROGRAMS "${CMAKE_BINARY_DIR}/obs_tools"
    DESTINATION "${CMAKE_INSTALL_BINDIR}"
)

install(TARGETS obs_edit
        LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)
