-- baby's first sql attempt
DROP TABLE IF EXISTS sdwps;
CREATE TABLE sdwps (
    sdwp_id      INT AUTO_INCREMENT NOT NULL,
    word_1       VARCHAR(128) NOT NULL,
    word_2       VARCHAR(128) NOT NULL,
    split_1      VARCHAR(128) NOT NULL,
    split_2      VARCHAR(128) NOT NULL,
    shape_index  INT NOT NULL,
    shape_length INT NOT NULL,
    prompt       VARCHAR(128) NOT NULL,
    solution     VARCHAR(128) NOT NULL,
    usable       BOOLEAN NOT NULL,
    mistakes_id  INT NOT NULL,
    PRIMARY KEY (`sdwp_id`)
);