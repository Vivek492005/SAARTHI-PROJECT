add_library(Engine engine.cpp)

target_link_libraries(Engine PUBLIC
                    Controller
                    InputBuffer
                    EventProcessor
                    Detector
                    )

target_include_directories(Engine PUBLIC
                        ../
                        )

install(TARGETS Engine DESTINATION lib)
install(FILES Engine.h DESTINATION include)