{
  formatPython = {
    enable = true;
    targets = [
      "/"
    ];
  };
  lintPython = {
    modules = {
      pokeapi = {
        python = "3.9";
        src = "/pokeapi";
      };
    };
  };
}
