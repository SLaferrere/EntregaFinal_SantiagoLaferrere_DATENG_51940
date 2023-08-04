CREATE TABLE if not exists laferreresantiago_coderhouse.UsersInformation (
    prefix varchar(50) NOT NULL,
    full_name varchar(50) NOT NULL,
    email varchar(50) NOT NULL DISTKEY,
    age int NOT NULL,
    date_of_birth DATE NOT NULL,
    cellphone varchar(50) NOT NULL,
    nationality varchar(50) NOT NULL,
    load_date DATE NOT NULL
) compound sortkey(email)
