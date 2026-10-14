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
              cargo
              cargo-deny
              clippy
              just
              maturin
              pngquant
              prek
              python
              rust-analyzer
              rustc
              rustfmt
              uv
            ]
            ++ systemLibs;

          env = rec {
            C_INCLUDE_PATH = CPATH;
            CPATH = lib.makeSearchPathOutput "dev" "include" systemLibs;
            LD_LIBRARY_PATH = lib.makeLibraryPath (systemLibs ++ [ pkgs.stdenv.cc.cc.lib ]);
            LIBRARY_PATH = lib.makeLibraryPath systemLibs;
            RUST_SRC_PATH = "${pkgs.rustPlatform.rustLibSrc}";
            UV_PYTHON = lib.getExe python;
            UV_PYTHON_DOWNLOADS = "never";
          };

          shellHook = ''
            unset PYTHONPATH

            if [ -d .git ] && ! grep -qs prek .git/hooks/pre-commit; then
              prek install
            fi
          '';
        };
      }
    );
}
