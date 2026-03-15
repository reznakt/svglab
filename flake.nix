{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (pkgs) lib;

        python = pkgs.python314;
      in
      {
        devShells.default = pkgs.mkShellNoCC {
          packages =
            with pkgs;
            [
              cairo
              freetype
              just
              libjpeg
              libpng
              pngquant
              pre-commit
              uv
            ]
            ++ [ python ];

          env = {
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON = lib.getExe python;

            LD_LIBRARY_PATH = lib.makeLibraryPath (
              with pkgs;
              [
                cairo
                freetype
                libffi
                libjpeg
                libpng
                stdenv.cc.cc.lib
                zlib
              ]
            );
          };

          shellHook = ''
            export VIRTUAL_ENV="$PWD/.venv"
            export PATH="$VIRTUAL_ENV/bin:$PATH"

            if [ ! -d "$VIRTUAL_ENV" ]; then
              uv venv "$VIRTUAL_ENV"
            fi

            if [ -d .git ] && [ ! -f .git/hooks/pre-commit ]; then
              pre-commit install
            fi
          '';
        };
      }
    );
}
