{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1"; # unstable Nixpkgs

  outputs =
    { self, ... }@inputs:

    let
      inherit (inputs.nixpkgs) lib;

      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      forEachSupportedSystem =
        f:
        lib.genAttrs supportedSystems (
          system:
          f {
            inherit system;
            pkgs = import inputs.nixpkgs { inherit system; };
          }
        );

      pythonVersion = "3.13";
    in
    {
      packages = forEachSupportedSystem (
        { pkgs, system }:
        let
          concatMajorMinor =
            v:
            lib.pipe v [
              lib.versions.splitVersion
              (lib.sublist 0 2)
              lib.concatStrings
            ];

          python = pkgs."python${concatMajorMinor pythonVersion}";

          pyprojectToml = builtins.fromTOML (builtins.readFile ./pyproject.toml);

          aniworld-cli-unwrapped = python.pkgs.buildPythonApplication {
            pname = "aniworld-cli";
            version = pyprojectToml.project.version;
            pyproject = true;

            src = ./.;

            build-system = with python.pkgs; [ setuptools ];

            dependencies = with python.pkgs; [
              requests
              beautifulsoup4
              questionary
            ];

            pythonImportsCheck = [ "aniworld_cli" ];
          };
          aniworld-cli = pkgs.symlinkJoin {
            name = "aniworld-cli";
            paths = [ aniworld-cli-unwrapped ];
            buildInputs = [ pkgs.makeWrapper ];
            postBuild = ''
              wrapProgram $out/bin/aniworld-cli \
                --suffix PATH : ${lib.makeBinPath [ pkgs.mpv ]}
            '';
          };
        in
        {
          inherit aniworld-cli;
          default = aniworld-cli;
        }
      );

      apps = forEachSupportedSystem (
        { pkgs, system }:
        {
          aniworld-cli = {
            type = "app";
            program = "${self.packages.${system}.aniworld-cli}/bin/aniworld-cli";
          };
          default = self.apps.${system}.aniworld-cli;
        }
      );

      devShells = forEachSupportedSystem (
        { pkgs, system }:
        let
          concatMajorMinor =
            v:
            lib.pipe v [
              lib.versions.splitVersion
              (lib.sublist 0 2)
              lib.concatStrings
            ];

          python = pkgs."python${concatMajorMinor pythonVersion}";
        in
        {
          default = pkgs.mkShellNoCC {
            venvDir = ".venv";

            postShellHook = ''
              venvVersionWarn() {
              	local venvVersion
              	venvVersion="$("$venvDir/bin/python" -c 'import platform; print(platform.python_version())')"

              	[[ "$venvVersion" == "${python.version}" ]] && return

              	cat <<EOF
              Warning: Python version mismatch: [$venvVersion (venv)] != [${python.version}]
                       Delete '$venvDir' and reload to rebuild for version ${python.version}
              EOF
              }

              venvVersionWarn
            '';

            packages =
              (with python.pkgs; [
                venvShellHook
                pip
              ])
              ++ [ self.formatter.${system} ];
          };
        }
      );

      formatter = forEachSupportedSystem ({ pkgs, ... }: pkgs.nixfmt);
    };
}
