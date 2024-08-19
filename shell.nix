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


  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    poetry install
  '';
}
