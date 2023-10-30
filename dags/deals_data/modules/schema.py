CITY_TABLE_SCHEMA = [
    "cityId VARCHAR(50) PRIMARY KEY",
    "cityNameEn TEXT",
    "cityNameAr TEXT",
]

CATEGORY_TABLE_SCHEMA = [
    "categoryId VARCHAR(50) PRIMARY KEY",
    "categoryNameEn TEXT",
    "categoryNameAr TEXT",
]

PROPERTY_TABLE_SCHEMA = [
    "propertyTypeId VARCHAR(50) PRIMARY KEY",
    "propertyTypeNameEn TEXT",
    "propertyTypeNameAr TEXT",
]

LISTING_TABLE_SCHEMA = [
    "listingId VARCHAR(50) PRIMARY KEY",
    "cityId VARCHAR(50)",
    "cityNameEn TEXT",
    "cityNameAr TEXT",
    "categoryId VARCHAR(50)",
    "categoryNameEn TEXT",
    "categoryNameAr TEXT",
    "propertyTypeId VARCHAR(50)",
    "propertyTypeNameEn TEXT",
    "propertyTypeNameAr TEXT",
    "districtId VARCHAR(50)",
    "districtNameEn TEXT",
    "districtNameAr TEXT",
    "purpose TEXT",
    "price REAL",
    "priceType TEXT",
    "area REAL NULL",
    "title VARCHAR NULL",
    "rentType VARCHAR NULL",
    "relatedQuestions TEXT",
    "developerAgent VARCHAR NULL",
    "createdBy TEXT",
    "advertiser TEXT",
    "status TEXT",
    "notificationMethods TEXT",
    "promotion TEXT",
    "published TEXT",
    "refreshedAt TEXT",
    "paymentMethod TEXT",
    "code INTEGER",
    "createdAt TEXT",
    "updatedAt TEXT",
    "userReportedThisAd TEXT",
    "readFlag TEXT",
    "accept TEXT",
    "reject TEXT",
    "favorite TEXT",
    "regaRawData TEXT",
]

FOREIGN_KEY_CONSTRAINTS = [
    "CONSTRAINT FK_cityId FOREIGN KEY(\"cityId\") REFERENCES city(\"cityId\")",
    "CONSTRAINT FK_categoryId FOREIGN KEY(\"categoryId\") REFERENCES category(\"categoryId\")",
    "CONSTRAINT FK_propertyTypeId FOREIGN KEY(\"propertyTypeId\") REFERENCES propertyType(\"propertyTypeId\")"
]


LISTING_COLUMNS = [
    "listingId",
    "cityId",
    "cityNameEn",
    "cityNameAr",
    "categoryId",
    "categoryNameEn",
    "categoryNameAr",
    "propertyTypeId",
    "propertyTypeNameEn",
    "propertyTypeNameAr",
    "districtId",
    "districtNameEn",
    "districtNameAr",
    "purpose",
    "price",
    "priceType",
    "area",
    "title",
    "rentType",
    "relatedQuestions",
    "developerAgent",
    "createdBy",
    "advertiser",
    "status",
    "notificationMethods",
    "promotion",
    "published",
    "refreshedAt",
    "paymentMethod",
    "code",
    "createdAt",
    "updatedAt",
    "userReportedThisAd",
    "readFlag",
    "accept",
    "reject",
    "favorite",
    "regaRawData",
]

ALL_RAW_COLUMNS_TO_PARSE = [
    "_id",
    "purpose",
    "price",
    "priceType",
    "area",
    "title",
    "developerAgent",
    "rentType",
    "status",
    "published",
    "paymentMethod",
    "code",
    "createdAt",
    "updatedAt",
    "userReportedThisAd",
    "read",
    "accept",
    "reject",
    "favorite",
    "regaRawData",
    "propertyType",
    "city",
    "district",
    "relatedQuestions",
    "createdBy",
    "advertiser",
    "promotion",
    "refreshed",
    "notificationMethods"
]