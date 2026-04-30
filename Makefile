ifneq ("$(wildcard ./.env)","")
    include .env
	export
endif

DB_DSN="postgres://mcpserver:open-db@localhost:5432/school-db?sslmode=disable"


podman.all:
	@podman compose up --build

podman.all.no_build:
	@podman compose up

migrate.create:
	@migrate create -ext sql -dir .db/migrations -seq $(name)

migrate.version:
	@migrate -database $(DB_DSN) -path=.db/migrations version

migrate.all.up:
	@migrate -database $(DB_DSN) -path .db/migrations up

migrate.all.down:
	@migrate -database $(DB_DSN) -path .db/migrations down

migrate.goto:
	@migrate -database $(DB_DSN) -path .db/migrations goto $(V)

db.data.dump:
	@podman exec -i postgresdb pg_dump -U postgres -a school-db > pgdump.sql

db.data.restore:
	@podman exec -i postgresdb psql -U postgres -d school-db < pgdump.sql