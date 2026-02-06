add_library(InputBuffer videobuf.cpp)

target_include_directories(Controller PUBLIC 
                        ../
                        )

install(TARGETS InputBuffer DESTINATION lib)
install(FILES InputBuffer.h DESTINATION include)