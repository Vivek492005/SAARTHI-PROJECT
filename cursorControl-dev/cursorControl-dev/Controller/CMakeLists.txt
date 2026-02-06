add_library(Controller mousectl.cpp)

target_include_directories(Controller PUBLIC 
                        ../
                        )

install(TARGETS Controller DESTINATION lib)
install(FILES Controller.h DESTINATION include)
