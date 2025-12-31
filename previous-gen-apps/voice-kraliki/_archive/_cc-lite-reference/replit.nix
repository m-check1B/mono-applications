{ pkgs }: {
  deps = [
    pkgs.nodejs_20
    pkgs.nodePackages.pnpm
    pkgs.postgresql_15
    pkgs.redis
    pkgs.openssl
    pkgs.git
    pkgs.bash
    pkgs.curl
    pkgs.wget
    pkgs.gnumake
    pkgs.gcc
    pkgs.python3
    pkgs.libuv
    pkgs.pkg-config
  ];
  env = {
    NODE_ENV = "development";
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/cc_lite";
    REDIS_URL = "redis://localhost:6379";
    PORT = "3010";
    FRONTEND_PORT = "3007";
    JWT_SECRET = "CHANGE_ME_IN_PRODUCTION";
    COOKIE_SECRET = "CHANGE_ME_IN_PRODUCTION";
  };
}