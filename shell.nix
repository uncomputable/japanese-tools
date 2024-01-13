{ pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/057f9aecfb71c4437d2b27d3323df7f93c010b7e.tar.gz";
    sha256 = "1ndiv385w1qyb3b18vw13991fzb9wg4cl21wglk89grsfsnra41k";
  }) {}
}:
let
  python = pkgs.python3.withPackages (p: with p; []);
in
  pkgs.mkShell {
    buildInputs = [
      python
    ];
  }
