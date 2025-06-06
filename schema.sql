DROP TABLE IF EXISTS FACT_plant_reading;
DROP TABLE IF EXISTS DIM_plant;
DROP TABLE IF EXISTS DIM_botanist;
DROP TABLE IF EXISTS DIM_origin_location;
DROP TABLE IF EXISTS DIM_country;


CREATE TABLE DIM_country (
    country_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL,
);

CREATE TABLE DIM_origin_location (
    location_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    longitude FLOAT,
    latitude FLOAT,
    city VARCHAR(55),
    country_id SMALLINT,
    FOREIGN KEY (country_id) REFERENCES DIM_country(country_id)
);

CREATE TABLE DIM_botanist (
    botanist_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    botanist_name VARCHAR(55),
    email VARCHAR(255),
    phone VARCHAR(30),
);

CREATE TABLE DIM_plant (
    plant_id SMALLINT PRIMARY KEY,
    plant_name VARCHAR(255),
    scientific_name VARCHAR(255),
    regular_url VARCHAR(MAX),
    botanist_id SMALLINT,
    location_id SMALLINT,
    FOREIGN KEY (botanist_id) REFERENCES DIM_origin_location(location_id)
);

CREATE TABLE FACT_plant_reading (
    plant_health_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    temperature FLOAT,
    soil_moisture FLOAT,
    recording_taken DATETIME2,
    last_watered DATETIME2,
    error_msg VARCHAR(255),
    plant_id SMALLINT,
    FOREIGN KEY (plant_id) REFERENCES DIM_plant(plant_id)
);

INSERT INTO DIM_country (country_name) VALUES
('Albania'),
('American Samoa'),
('Antigua and Barbuda'),
('Bosnia and Herzegovina'),
('Cameroon'),
('Canada'),
('Cayman Islands'),
('China'),
('Congo'),
('Cyprus'),
('Egypt'),
('French Southern Territories'),
('Greece'),
('Greenland'),
('Guernsey'),
('Heard Island and McDonald Islands'),
('Italy'),
('Jamaica'),
('Jersey'),
('Liberia'),
('Macao'),
('Mali'),
('Mauritius'),
('Mexico'),
('Mozambique'),
('Nicaragua'),
('Nigeria'),
('Norway'),
('Palau'),
('Peru'),
('Pitcairn Islands'),
('Puerto Rico'),
('Russian Federation'),
('Saint Kitts and Nevis'),
('Saint Martin'),
('Saint Vincent and the Grenadines'),
('Senegal'),
('Sweden'),
('Taiwan'),
('Togo'),
('Wallis and Futuna'),
('Western Sahara'),
('Yemen');

INSERT INTO DIM_origin_location (longitude, latitude, city, country_id) VALUES
(-11.5098, 43.74, 'Stammside', 1),
(-48.7087, 47.8428, 'Floshire', 2),
(-36.1349, -25.4878, 'Dale City', 25),
(46.4049, 63.3661, 'West Tedboro', 39),
(0.6279, 82.8917, 'North Felicia', 34),
(-12.1055, -40.3521, 'Ferryfort', 23),
(8.6662, 54.1635, 'Edwardfurt', 20),
(-11.0358, 22.1228, 'Port Johan', 7),
(178.9976, -85.7462, 'North Adriel', 26),
(-108.526, 89.0252, 'Dorianland', 22),
(-108.5545, 86.2589, 'Fort Maya', 41),
(54.0918, 26.7106, 'Annaboro', 12),
(81.3907, -54.9306, 'Felixberg', 6),
(100.898, -22.6373, 'New Clark', 7),
(39.0588, -60.739, 'Boscomouth', 28),
(158.4221, -81.6237, 'Herzogland', 18),
(42.0051, 21.299, 'Miramar', 9),
(175.4523, -69.713, 'Port Jennings', 21),
(152.5746, -79.3405, 'Oceanside', 11),
(-108.5995, 85.3837, 'Hollisfurt', 8),
(-37.76, 34.8822, 'Joaquinton', 31),
(-125.5911, 64.0127, 'New Glenda', 38),
(-81.7968, -17.3909, 'Adamshaven', 17),
(36.6064, 3.58, 'Laronburgh', 41),
(166.9358, -38.6402, 'South Nyasia', 15),
(54.2456, -34.7829, 'South Dawn', 4),
(89.3708, 80.1723, 'Greenholtland', 37),
(45.8024, -80.3481, 'Potomac', 29),
(-31.0999, 22.6292, 'Portsmouth', 35),
(-72.1543, -37.6215, 'Ottomouth', 11),
(166.9654, 10.0446, 'Steuberfurt', 5),
(6.5244, -58.3733, 'Cutler Bay', 24),
(22.1729, -59.666, 'New Danika', 42),
(-146.1691, 8.8125, 'Clearwater', 43),
(-65.8502, 87.3702, 'South Armani', 32),
(-17.7032, -40.9469, 'Port Fredrick', 33),
(-30.8766, 83.5292, 'Peoria', 13),
(-109.3082, -7.7324, 'Littlehaven', 36),
(-61.2803, 89.6714, 'South Hectorstead', 32),
(-128.8359, 87.938, 'Ernserworth', 27),
(74.927, -73.4156, 'Buffalo Grove', 30),
(-108.7315, 23.114, 'Catonsville', 10),
(21.8921, 14.31, 'South Julianview', 16),
(-78.697, -34.1863, 'Kathrynville', 21),
(-148.5469, 83.9217, 'Gavinstad', 19),
(-72.4879, -82.1806, 'Lake Norbertstead', 14),
(148.993, 15.7997, 'Ginaberg', 40),
(18.6216, -62.6313, 'Joanyland', 3);


INSERT INTO DIM_botanist (botanist_name, email, phone) VALUES
('Santiago Ortiz', 'santiago.ortiz@lnhm.co.uk', '(770) 924-1572 x884'),
('Lindsay Feest', 'lindsay.feest@lnhm.co.uk', '(590) 404-7387 x7681'),
('Helen Waters', 'helen.waters@lnhm.co.uk', '1-520-943-3657 x23140'),
('Kristin Lakin V', 'kristin.lakin.v@lnhm.co.uk', '(903) 973-1504 x9409'),
('Benny Block', 'benny.block@lnhm.co.uk', '687-647-1094'),
('Dallas Terry', 'dallas.terry@lnhm.co.uk', '489-414-1969 x514'),
('Nathan Kuhic', 'nathan.kuhic@lnhm.co.uk', '(470) 586-3930 x591'),
('Bradford Mitchell DVM', 'bradford.mitchell.dvm@lnhm.co.uk', '(230) 859-2277 x3537'),
('Dr. Phillip Lind', 'dr..phillip.lind@lnhm.co.uk', '(889) 896-3821'),
('Sandra Pfeffer', 'sandra.pfeffer@lnhm.co.uk', '1-944-604-9635 x77682'),
('Jacob Jacobi', 'jacob.jacobi@lnhm.co.uk', '(459) 933-0647'),
('Clinton Prohaska-Christiansen III', 'clinton.prohaska-christiansen.iii@lnhm.co.uk', '1-957-526-2533 x4543'),
('Darrel Lesch', 'darrel.lesch@lnhm.co.uk', '975-666-9644 x58578'),
('Marty Lang', 'marty.lang@lnhm.co.uk', '1-539-229-4058'),
('Sadie Romaguera', 'sadie.romaguera@lnhm.co.uk', '(415) 921-6221 x26702'),
('Ms. Diana King', 'ms..diana.king@lnhm.co.uk', '673.641.8851'),
('Chester Smith', 'chester.smith@lnhm.co.uk', '1-730-711-3377 x08275'),
('Patricia Howell', 'patricia.howell@lnhm.co.uk', '1-886-335-2758 x2333'),
('Darin Friesen-Stark MD', 'darin.friesen-stark.md@lnhm.co.uk', '734-212-1797 x507'),
('Iris Jenkins', 'iris.jenkins@lnhm.co.uk', '288.875.3012 x4682'),
('Betty Kreiger', 'betty.kreiger@lnhm.co.uk', '(430) 985-1362 x54710'),
('Lucas Quitzon', 'lucas.quitzon@lnhm.co.uk', '(400) 791-2051 x0032'),
('Earnest Stanton', 'earnest.stanton@lnhm.co.uk', '1-849-419-7923 x487'),
('Clifton Brekke', 'clifton.brekke@lnhm.co.uk', '(889) 712-9685 x61463'),
('Henrietta Gleichner', 'henrietta.gleichner@lnhm.co.uk', '(879) 206-9116 x8935'),
('Jorge Torp', 'jorge.torp@lnhm.co.uk', '312.868.8819 x8410'),
('Jacquelyn Quigley', 'jacquelyn.quigley@lnhm.co.uk', '1-672-222-8133 x105'),
('Helen Stracke', 'helen.stracke@lnhm.co.uk', '1-219-392-5283'),
('Kenneth Murphy', 'kenneth.murphy@lnhm.co.uk', '(682) 358-8815 x08653'),
('Wendy Swift', 'wendy.swift@lnhm.co.uk', '(774) 986-4550 x796'),
('Dr. Camille Kreiger', 'dr..camille.kreiger@lnhm.co.uk', '1-288-382-3655 x5892'),
('Gordon Boehm', 'gordon.boehm@lnhm.co.uk', '464.633.6597 x7370'),
('Peter Hartmann', 'peter.hartmann@lnhm.co.uk', '(718) 765-2084 x0261'),
('Oscar Schinner-Little', 'oscar.schinner-little@lnhm.co.uk', '570-593-4399 x49703'),
('Ms. Ashley Stracke', 'ms..ashley.stracke@lnhm.co.uk', '1-666-690-3171 x152'),
('Eduardo Okuneva II', 'eduardo.okuneva.ii@lnhm.co.uk', '408-816-2276 x87051'),
('Bob Hartmann', 'bob.hartmann@lnhm.co.uk', '408-747-3878 x32922'),
('Wilson Welch', 'wilson.welch@lnhm.co.uk', '(953) 607-4239 x328'),
('Terrance Leuschke', 'terrance.leuschke@lnhm.co.uk', '1-661-425-6823 x4455'),
('Jo Baumbach', 'jo.baumbach@lnhm.co.uk', '976-364-3090'),
('Dr. Jacob Glover', 'dr..jacob.glover@lnhm.co.uk', '705-893-6693 x509'),
('Vicky Leuschke', 'vicky.leuschke@lnhm.co.uk', '(462) 735-6685 x8065'),
('Kathy Haley', 'kathy.haley@lnhm.co.uk', '(514) 473-7641 x14748'),
('Leroy Hudson', 'leroy.hudson@lnhm.co.uk', '872-709-8943 x15830'),
('Carolyn Jakubowski', 'carolyn.jakubowski@lnhm.co.uk', '464.539.9779'),
('Bernice Schulist', 'bernice.schulist@lnhm.co.uk', '516.311.7225'),
('Kenneth Buckridge', 'kenneth.buckridge@lnhm.co.uk', '763.914.8635 x57724'),
('Irma Ortiz Jr.', 'irma.ortiz.jr.@lnhm.co.uk', '(456) 348-3790 x868');

INSERT INTO DIM_plant (plant_id, plant_name, scientific_name, regular_url, botanist_id, location_id) VALUES
(1,'Venus flytrap', 'NULL', NULL, 47, 1),
(2,'Corpse flower', 'NULL', NULL, 16, 2),
(3,'Rafflesia arnoldii', 'NULL', NULL, 36, 3),
(4,'Black bat flower', 'NULL', NULL, 38, 4),
(5,'Pitcher plant', 'Sarracenia catesbaei', 'https://perenual.com/storage/image/upgrade_access.jpg', 5, 5),
(6,'Wollemi pine', 'Wollemia nobilis', 'https://perenual.com/storage/image/upgrade_access.jpg', 20, 6),
(7, NULL, NULL, NULL, NULL, NULL),
(8,'Bird of paradise', 'Heliconia schiedeana ''Fire and Ice''', 'https://perenual.com/storage/image/upgrade_access.jpg', 8, 7),
(9, 'Cactus', 'Pereskia grandifolia', 'https://perenual.com/storage/image/upgrade_access.jpg', 40, 8),
(10,'Dragon tree', 'NULL', NULL, 39, 9),
(11,'Asclepias Curassavica', 'Asclepias curassavica', 'https://perenual.com/storage/species_image/1007_asclepias_curassavica/regular/51757177616_7ca0baaa87_b.jpg', 17, 10),
(12, 'Brugmansia X Candida', 'NULL', NULL, 29, 11),
(13, 'Canna ‘Striata’', 'NULL', NULL, 48, 12),
(14, 'Colocasia Esculenta', 'Colocasia esculenta', 'https://perenual.com/storage/species_image/2015_colocasia_esculenta/regular/24325097844_14719030a3_b.jpg', 43, 13),
(15,'Cuphea ‘David Verity’', 'NULL', NULL, 11, 14),
(16, 'Euphorbia Cotinifolia', 'Euphorbia cotinifolia', 'https://perenual.com/storage/species_image/2868_euphorbia_cotinifolia/regular/51952243235_061102bd05_b.jpg', 32, 15),
(17, 'Ipomoea Batatas', 'Ipomoea batatas', 'https://perenual.com/storage/image/upgrade_access.jpg', 22, 16),
(18, 'Manihot Esculenta ‘Variegata’', 'NULL', NULL, 23, 17),
(19, 'Musa Basjoo', 'Musa basjoo', 'https://perenual.com/storage/image/upgrade_access.jpg', 28, 18),
(20, 'Salvia Splendens', 'Salvia splendens', 'https://perenual.com/storage/image/upgrade_access.jpg', 46, 19),
(21, 'Anthurium', 'Anthurium andraeanum', 'https://perenual.com/storage/species_image/855_anthurium_andraeanum/regular/49388458462_0ef650db39_b.jpg', 34, 20),
(22, 'Bird of Paradise', 'Heliconia schiedeana ''Fire and Ice''', 'https://perenual.com/storage/image/upgrade_access.jpg', 35, 21),
(23, 'Cordyline Fruticosa', 'Cordyline fruticosa', 'https://perenual.com/storage/species_image/2045_cordyline_fruticosa/regular/2560px-Cordyline_fruticosa_Rubra_1.jpg', 24, 22),
(24, 'Ficus', 'Ficus carica', 'https://perenual.com/storage/species_image/288_ficus_carica/regular/52377169610_b7a247a378_b.jpg', 9, 23),
(25, 'Palm Trees', 'NULL', NULL, 6, 24),
(26, 'Dieffenbachia Seguine', 'Dieffenbachia seguine', 'https://perenual.com/storage/species_image/2468_dieffenbachia_seguine/regular/24449059743_2aee995991_b.jpg', 27, 25),
(27, 'Spathiphyllum', 'Spathiphyllum (group)', 'https://perenual.com/storage/image/upgrade_access.jpg', 30, 26),
(28, 'Croton', 'Codiaeum variegatum', 'https://perenual.com/storage/species_image/1999_codiaeum_variegatum/regular/29041866364_2c535b2297_b.jpg', 15, 27),
(29, 'Aloe Vera', 'Aloe vera', 'https://perenual.com/storage/species_image/728_aloe_vera/regular/52619084582_6ebcfe6a74_b.jpg', 45, 28),
(30, 'Ficus Elastica', 'Ficus elastica', 'https://perenual.com/storage/species_image/2961_ficus_elastica/regular/533092219_8da73ba0d2_b.jpg', 44, 29),
(31, 'Sansevieria Trifasciata', 'Sansevieria trifasciata', 'https://perenual.com/storage/image/upgrade_access.jpg', 13, 30),
(32, 'Philodendron Hederaceum', 'Philodendron hederaceum', 'https://perenual.com/storage/image/upgrade_access.jpg', 3, 31),
(33, 'Schefflera Arboricola', 'Schefflera arboricola', 'https://perenual.com/storage/image/upgrade_access.jpg', 14, 32),
(34, 'Aglaonema Commutatum', 'Aglaonema commutatum', 'https://perenual.com/storage/species_image/625_aglaonema_commutatum/regular/24798632751_3a039ecbc6_b.jpg', 21, 33),
(35, 'Monstera Deliciosa', 'Monstera deliciosa', 'https://perenual.com/storage/image/upgrade_access.jpg', 26, 34),
(36, 'Tacca Integrifolia', 'Tacca integrifolia', 'https://perenual.com/storage/image/upgrade_access.jpg', 25, 35),
(37, 'Psychopsis Papilio', 'NULL', NULL, 18, 36),
(38, 'Saintpaulia Ionantha', 'Saintpaulia ionantha', 'https://perenual.com/storage/image/upgrade_access.jpg', 1, 37),
(39, 'Gaillardia', 'Gaillardia aestivalis', 'https://perenual.com/storage/image/upgrade_access.jpg', 2, 38),
(40, 'Amaryllis', 'Hippeastrum (group)', 'https://perenual.com/storage/image/upgrade_access.jpg', 10, 39),
(41, 'Caladium Bicolor', 'Caladium bicolor', 'https://perenual.com/storage/species_image/1457_caladium_bicolor/regular/25575875658_d782fb76f1_b.jpg', 19, 40),
(42, 'Chlorophytum Comosum', 'Chlorophytum comosum ''Vittatum''', 'https://perenual.com/storage/species_image/1847_chlorophytum_comosum_vittatum/regular/2560px-Chlorophytum_comosum_27Vittatum27_kz02.jpg', 4, 41),
(43, NULL, NULL, NULL, NULL, NULL),
(44, 'Araucaria Heterophylla', 'Araucaria heterophylla', 'https://perenual.com/storage/species_image/917_araucaria_heterophylla/regular/49833684212_2aff9d7b3c_b.jpg', 31, 42),
(45, 'Begonia', 'Begonia ''Art Hodes''', NULL, 7, 43),
(46, 'Medinilla Magnifica', 'Medinilla magnifica', 'https://perenual.com/storage/image/upgrade_access.jpg', 12, 44),
(47, 'Calliandra Haematocephala', 'Calliandra haematocephala', 'https://perenual.com/storage/species_image/1477_calliandra_haematocephala/regular/52063600268_834ebc0538_b.jpg', 42, 45),
(48, 'Zamioculcas Zamiifolia', 'Zamioculcas zamiifolia', 'https://perenual.com/storage/image/upgrade_access.jpg', 37, 46),
(49, 'Crassula Ovata', 'Crassula ovata', 'https://perenual.com/storage/species_image/2193_crassula_ovata/regular/33253726791_980c738a1e_b.jpg', 41, 47),
(50, 'Epipremnum Aureum', 'Epipremnum aureum', 'https://perenual.com/storage/species_image/2773_epipremnum_aureum/regular/2560px-Epipremnum_aureum_31082012.jpg', 33, 48),
(51, NULL, NULL, NULL, NULL, NULL),
(52, NULL, NULL, NULL, NULL, NULL),
(53, NULL, NULL, NULL, NULL, NULL),
(54, NULL, NULL, NULL, NULL, NULL),
(55, NULL, NULL, NULL, NULL, NULL),
(56, NULL, NULL, NULL, NULL, NULL),
(57, NULL, NULL, NULL, NULL, NULL),
(58, NULL, NULL, NULL, NULL, NULL),
(59, NULL, NULL, NULL, NULL, NULL),
(60, NULL, NULL, NULL, NULL, NULL)
