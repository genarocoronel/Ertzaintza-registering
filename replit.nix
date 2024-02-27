{pkgs}: {
  deps = [
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.xmlsec
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
    pkgs.python310Packages.xmlsec
  ];
}