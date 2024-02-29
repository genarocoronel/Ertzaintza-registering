{pkgs}: {
  deps = [
    pkgs.libtool
    pkgs.pkg-config
    pkgs.arrow-cpp
    pkgs.rustc
    pkgs.stdenv.cc.cc.lib
    pkgs.libxml2
    pkgs.python310Packages.pyarrow
    pkgs.python310Packages.xmlsec
    pkgs.python310Packages.pydantic
    pkgs.xmlsec
    pkgs.poetry
];
  environment = {
    sessionVariables = {
      LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
    };
  };
}