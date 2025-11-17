# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-25.05"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python314
    pkgs.uv
    pkgs.htop
  ];
  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
      "google.gemini-cli-vscode-ide-companion"
      "ms-python.python"
      "ms-python.debugpy"
      "PKief.material-icon-theme"
      "PKief.material-product-icons"
      "zhuangtongfa.material-theme"
    ];
    # Enable previews
    previews = {
      enable = true;
      previews = {
      };
    };
    workspace = {
      onCreate = {
        default.openFiles = [ "README.md" ];
      };
      onStart = {
      };
    };
  };
}
