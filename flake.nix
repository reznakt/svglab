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

        systemLibs = with pkgs; [
          cairo # pycairo
          freetype # matplotlib
          libffi # cffi
          libjpeg_turbo # Pillow
          libpng # Pillow
          libxml2 # lxml
          libxslt # lxml
          zlib # Pillow
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages =
            with pkgs;
            [
              just
              pngquant
              pre-commit
              uv
              python
            ]
            ++ systemLibs;

          env = rec {
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON = lib.getExe python;
            CPATH = lib.makeSearchPathOutput "dev" "include" systemLibs;
            C_INCLUDE_PATH = CPATH;
            LIBRARY_PATH = lib.makeLibraryPath systemLibs;
            LD_LIBRARY_PATH = lib.makeLibraryPath (systemLibs ++ [ pkgs.stdenv.cc.cc.lib ]);
          };

          shellHook = ''
            if [ -d .git ] && [ ! -f .git/hooks/pre-commit ]; then
              pre-commit install
            fi
          '';
        };
      }
    );
}
