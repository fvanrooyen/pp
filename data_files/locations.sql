CREATE TABLE `locations` (
  `iso_country_code` varchar(2) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `city_name` varchar(180) DEFAULT NULL,
  `state_name` varchar(100) DEFAULT NULL,
  `state_abbrev` varchar(20) DEFAULT NULL,
  `county_name` varchar(100) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  PRIMARY KEY (`iso_country_code`,`postal_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;