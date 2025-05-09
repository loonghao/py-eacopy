cmake_minimum_required(VERSION 3.15)
project(lzma C) 
 
add_library(lzma INTERFACE) 
target_include_directories(lzma INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/liblzma/api) 
