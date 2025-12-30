import environs


env = environs.Env()
env.read_env()

DATABASE_URL = env.str("DATABASE_URL", default="postgresql://postgres@localhost/f1data")
