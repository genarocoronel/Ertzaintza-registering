{pkgs}: {
  deps = [
    pkgs.libtool
    pkgs.pkg-config
    pkgs.arrow-cpp
    pkgs.rustc
    pkgs.stdenv.cc.cc.lib
    pkgs.libxml2
    #pkgs.libiconv
    #pkgs.cargo
    #pkgs.cacert
    #pkgs.zlib
    #pkgs.xcodebuild
    #pkgs.libxcrypt
    pkgs.xmlsec
    #pkgs.openssl
    pkgs.python311Packages.pyarrow
    pkgs.poetry
];
  environment = {
    sessionVariables = {
      LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
    };
  };
}