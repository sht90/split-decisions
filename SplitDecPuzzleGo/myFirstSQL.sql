-- baby's first sql attempt
DROP TABLE IF EXISTS sdwps;
CREATE TABLE sdwps (
    sdwp_id        INT NOT NULL AUTO_INCREMENT,
    word_1         VARCHAR(128) NOT NULL,
    word_2         VARCHAR(128) NOT NULL,
    split_1        VARCHAR(128) NOT NULL,
    split_2        VARCHAR(128) NOT NULL,
    shape_index    INT NOT NULL,
    shape_length   INT NOT NULL,
    solution       VARCHAR(128) NOT NULL,
    usable         BOOLEAN NOT NULL,
    mistakes_id    INT NOT NULL,
    constraints_id INT NOT NULL,
    PRIMARY KEY (sdwp_id)
);

DROP TABLE IF EXISTS usable_sdwps;
CREATE TABLE usable_sdwps (
    sdwp_id        INT NOT NULL AUTO_INCREMENT,
    word_1         VARCHAR(128) NOT NULL,
    word_2         VARCHAR(128) NOT NULL,
    split_1        VARCHAR(128) NOT NULL,
    split_2        VARCHAR(128) NOT NULL,
    shape_index    INT NOT NULL,
    shape_length   INT NOT NULL,
    solution       VARCHAR(128) NOT NULL,
    usable         BOOLEAN NOT NULL,
    mistakes_id    INT NOT NULL,
    constraints_id INT NOT NULL,
    PRIMARY KEY (sdwp_id)
);