CREATE TABLE products  (
    productId BIGINT NOT NULL PRIMARY KEY,
    productSku BIGINT NOT NULL,
    productName VARCHAR(20),
    productAmount BIGINT,
    productData VARCHAR(120)
);

CREATE TABLE loyality_data  (
    productSku BIGINT NOT NULL PRIMARY KEY,
    loyalityData VARCHAR(120)
);


INSERT INTO loyality_data (productsku, loyalitydata) VALUES (20001, 'Loyality_on');
INSERT INTO loyality_data (productsku, loyalitydata) VALUES (30001, 'Loyality_on');
INSERT INTO loyality_data (productsku, loyalitydata) VALUES (50001, 'Loyality_on');
INSERT INTO loyality_data (productsku, loyalitydata) VALUES (60001, 'Loyality_on');
