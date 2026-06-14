{
  description = "espHome";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShell = pkgs.mkShell {
        packages = with pkgs; [
          python312
          python312Packages.pip
          stdenv.cc.cc.lib
          expat
          libGL
          libGLU
          libX11
          libXrender
          zlib
          glib
          fontconfig
          freetype
        ];

        shellHook = ''
          export HISTFILE="$PWD/.bash_history"

          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath (with pkgs; [
            stdenv.cc.cc.lib
            expat
            libGL
            libGLU
            libX11
            libXrender
            zlib
            glib
            fontconfig
            freetype
          ])}:$LD_LIBRARY_PATH

          if [ ! -d .venv ]; then
            python -m venv .venv
            .venv/bin/pip install build123d ocp-vscode
          fi
          source .venv/bin/activate
        '';
      };
    });
}
