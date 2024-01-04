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
        lambdanas = hcs.outputs.packages.lambdanas;
      in
      {
        formatter = pkgs.nixpkgs-fmt;
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python310
            black
            lambdanas
          ];
        };
      });
}
