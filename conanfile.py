from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.33.0"


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    version = "4.2.1"
    
    description = "HarfBuzz is an OpenType text shaping engine."
    topics = ("opentype", "text", "engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://harfbuzz.org"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_gdi": [True, False],
        "with_uniscribe": [True, False],
        "with_directwrite": [True, False],
        "with_subset": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_freetype": True,
        "with_gdi": False,
        "with_uniscribe": False,
        "with_directwrite": False,
        "with_subset": False,
    }

    short_paths = True

    exports_sources = "*"
    generators = "cmake_paths"
    no_copy_source=True


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_gdi
            del self.options.with_uniscribe
            del self.options.with_directwrite

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/[]")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["HB_HAVE_FREETYPE"] = self.options.with_freetype
        cmake.definitions["HB_HAVE_GRAPHITE2"] = False
        cmake.definitions["HB_HAVE_GLIB"] = False
        cmake.definitions["HB_HAVE_ICU"] = False
        if tools.is_apple_os(self.settings.os):
            cmake.definitions["HB_HAVE_CORETEXT"] = True
        elif self.settings.os == "Windows":
            cmake.definitions["HB_HAVE_GDI"] = self.options.with_gdi
            cmake.definitions["HB_HAVE_UNISCRIBE"] = self.options.with_uniscribe
            cmake.definitions["HB_HAVE_DIRECTWRITE"] = self.options.with_directwrite
        cmake.definitions["HB_BUILD_UTILS"] = False
        cmake.definitions["HB_BUILD_SUBSET"] = self.options.with_subset
        cmake.definitions["HB_HAVE_GOBJECT"] = False
        cmake.definitions["HB_HAVE_INTROSPECTION"] = False
        cmake.definitions["CMAKE_PROJECT_" + self.name + "_INCLUDE"] = os.path.join(self.build_folder, "conan_paths.cmake")

        debug_prefix_mapping = '-ffile-prefix-map=' + os.path.abspath(self.source_folder) + '=' + self.name
        cmake.definitions["CMAKE_C_FLAGS"] = debug_prefix_mapping
        cmake.definitions["CMAKE_CXX_FLAGS"] = debug_prefix_mapping
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
                
        # fix for MinGW debug build
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            cmake.definitions["CMAKE_C_FLAGS"] = "-Wa,-mbig-obj"
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wa,-mbig-obj"

        cmake.configure(source_folder=self.source_folder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        cmake = self._configure_cmake()
        cmake.install()


