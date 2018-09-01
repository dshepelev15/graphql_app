export PGUSER=postgres
psql <<- EOSQL
    CREATE USER graphql_user WITH PASSWORD '5l085x1vl4hk575qcr88p8yj4qr0a-j5f6';
    CREATE DATABASE graphql_db;
    GRANT ALL PRIVILEGES ON DATABASE graphql_db to graphql_user;

    CREATE DATABASE graphql_db_test;
    GRANT ALL PRIVILEGES ON DATABASE graphql_db_test to graphql_user;
EOSQL

psql graphql_db graphql_user <<- EOSQL
    CREATE TABLE account
    (
        id serial NOT NULL,
        login text NOT NULL,
        password text NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT login UNIQUE (login)
    )
    WITH (
        OIDS = FALSE
    );

    ALTER TABLE account
        OWNER to graphql_user;

    CREATE TABLE card
    (
        id serial NOT NULL,
        code character varying(4),
        last4digit character varying(4),
        type text,
        account_id bigint NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT account_id FOREIGN KEY (account_id)
            REFERENCES account (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
    )
    WITH (
        OIDS = FALSE
    );

    ALTER TABLE card
        OWNER to graphql_user;
EOSQL

psql graphql_db_test graphql_user <<- EOSQL
    CREATE TABLE account
    (
        id serial NOT NULL,
        login text NOT NULL,
        password text NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT login UNIQUE (login)
    )
    WITH (
        OIDS = FALSE
    );

    ALTER TABLE account
        OWNER to graphql_user;

    CREATE TABLE card
    (
        id serial NOT NULL,
        code character varying(4),
        last4digit character varying(4),
        type text,
        account_id bigint NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT account_id FOREIGN KEY (account_id)
            REFERENCES account (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
    )
    WITH (
        OIDS = FALSE
    );

    ALTER TABLE card
        OWNER to graphql_user;
EOSQL
