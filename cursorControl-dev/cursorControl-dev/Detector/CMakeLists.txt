add_library(Detector cvfacedetect.cpp)

target_include_directories(Detector PUBLIC
                        ../
                        )

install(TARGETS Detector DESTINATION lib)
install(FILES Detector.h DESTINATION include)