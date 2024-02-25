{pkgs}: {
  deps = [
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.python310
    pkgs.python310Packages.pydantic
    pkgs.python310Packages.zeep
    pkgs.python310Packages.xmlsec
    pkgs.python310Packages.dicttoxml
    pkgs.python310Packages.attrs
    pkgs.libtool
    pkgs.libxcrypt
    pkgs.zlib
    pkgs.xcodebuild
    pkgs.cacert
    pkgs.openssl
    pkgs.pkg-config
    pkgs.coreutils
    pkgs.libxml2
    pkgs.streamlit
  ];
}