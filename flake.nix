{
  description = "Epitech Coding Style Checker Language Server";

  inputs = {
    hcs.url = "github:Sigmapitech/hcs";
    nixpkgs.url = "nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, hcs, utils, ... }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        lambdananas = hcs.outputs.packages.${system}.lambdananas;
      in rec
      {
        formatter = pkgs.nixpkgs-fmt;
        devShells.default = pkgs.mkShell {
          inputsFrom = [ packages.echsls ];
          packages = [ pkgs.black lambdananas ];
        };

        packages = rec {
          default = ehcsls;
          echsls = ehcsls; # legacy exposed package typo :<
          ehcsls =
            let
              pypkgs = pkgs.python311Packages;
            in
            pypkgs.buildPythonPackage {
              pname = "ehcsls";
              version = "0.0.1";
              src = ./.;

              propagatedBuildInputs = [ pypkgs.pygls ];
              nativeBuildInputs = [ pkgs.makeWrapper ];
              doCheck = false;

              postFixup = ''
                wrapProgram $out/bin/ehcsls_run \
                --set PATH ${pkgs.lib.makeBinPath ([ lambdananas ])}
              '';
            };
        };
      });
}
