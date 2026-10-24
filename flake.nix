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

        mkDevShell =
          python:
          pkgs.mkShell {
            packages =
              with pkgs;
              [
                actionlint
                cargo
                cargo-deny
                cargo-machete
                clippy
                deadnix
                editorconfig-checker
                gitleaks
                just
                maturin
                nixfmt
                pngquant
                prek
                python
                rumdl
                rust-analyzer
                rustc
                rustfmt
                statix
                tombi
                typos
                uv
                yamlfmt
                zizmor
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
      in
      {
        # one shell per supported Python, so CI can test each against the
        # same glibc the extension is built with
        devShells = {
          default = mkDevShell pkgs.python315;
        }
        // lib.genAttrs [
          "python311"
          "python312"
          "python313"
          "python314"
          "python315"
        ] (name: mkDevShell pkgs.${name});
      }
    );
}
