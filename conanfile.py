from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.33.0"


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    version = "5.1.0"
    
    description = "HarfBuzz is an OpenType text shaping engine."
    topics = ("opentype", "text", "engine")
    url = "https://gitlab.worldiety.net/worldiety/customer/wdy/libriety/cpp/forks"
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

    no_copy_source = True
    exports_sources = ["*"]
    python_requires = "wdyConanHelper/[]"
    python_requires_extend = "wdyConanHelper.ConanCMake"

    def requirements(self):
        if self.options.with_freetype:
            self.requires("freetype/[]")

    def cmake_definitions(self):
        defs = {
            "HB_HAVE_FREETYPE": self.options.with_freetype,
            "HB_HAVE_GRAPHITE2": False,
            "HB_HAVE_GLIB": False,
            "HB_HAVE_ICU": False,
            "HB_BUILD_UTILS": False,
            "HB_BUILD_SUBSET": self.options.with_subset,
            "HB_HAVE_GOBJECT": False,
            "HB_HAVE_INTROSPECTION": False,
            "HB_HAVE_CORETEXT": False,
        }

        if self.settings.os == "Windows":
            defs["HB_HAVE_GDI"] = self.options.with_gdi
            defs["HB_HAVE_UNISCRIBE"] = self.options.with_uniscribe
            defs["HB_HAVE_DIRECTWRITE"] = self.options.with_directwrite
        # fix for MinGW debug build
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            defs["CMAKE_C_FLAGS"] = "-Wa,-mbig-obj "
            defs["CMAKE_CXX_FLAGS"] = "-Wa,-mbig-obj"
        return defs

