{ pkgs, ... }:
let
  tex = (pkgs.texlive.combine {
    inherit (pkgs.texlive)
      scheme-small dvisvgm
      amsmath hyperref comment;
  });
in pkgs.mkShell {
  name = "python-venv";
  venvDir = "./.venv";

  packages = with pkgs; [ tex graphviz pdf2svg elan gnumake poetry ];



  shellHook = ''
    poetry install
  '';
}
