CITY_TABLE_SCHEMA = [
    "cityId TEXT PRIMARY KEY",
    "cityNameEn TEXT",
    "cityNameAr TEXT",
]

CITY_COLUMNS = [
    "cityId",
    "cityNameEn",
    "cityNameAr"
]

CATEGORY_TABLE_SCHEMA = [
    "categoryId TEXT PRIMARY KEY",
    "categoryNameEn TEXT",
    "categoryNameAr TEXT",
]

CATEGORY_COLUMNS = [
    "categoryId",
    "categoryNameEn",
    "categoryNameAr"
]

PROPERTY_TABLE_SCHEMA = [
    "propertyTypeId TEXT PRIMARY KEY",
    "propertyTypeNameEn TEXT",
    "propertyTypeNameAr TEXT",
]

PROPERTY_COLUMNS = [
    "propertyTypeId",
    "propertyTypeNameEn",
    "propertyTypeNameAr"
]

LISTING_TABLE_SCHEMA = [
    "listingId TEXT PRIMARY KEY",
    "cityId TEXT",
    "categoryId TEXT",
    "propertyTypeId TEXT",
    "purpose TEXT",
    "price REAL",
    "priceType TEXT",
    "area REAL",
    "createdBy TEXT",
    "advertiser TEXT",
    "status TEXT",
    "notificationMethods TEXT",
    "promotion TEXT",
    "published TEXT",
    "refreshedAt TEXT",
    "paymentMethod TEXT",
    "code TEXT",
    "createdAt TEXT",
    "updatedAt TEXT",
    "userReportedThisAd TEXT",
    "read TEXT",
    "accept TEXT",
    "reject TEXT",
    "favorite TEXT",
    "regaRawData TEXT",
    "FOREIGN KEY(cityId) REFERENCES city(id)",
    "FOREIGN KEY(categoryId) REFERENCES category(id)",
    "FOREIGN KEY(propertyTypeId) REFERENCES property_type(id)"
]

LISTING_COLUMNS = [
    "listingId",
    "cityId",
    "categoryId",
    "propertyTypeId",
    "purpose",
    "price",
    "priceType",
    "area",
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
    "read",
    "accept",
    "reject",
    "favorite",
    "regaRawData",
]

COLUMNS_THAT_EXPAND = [
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

COLUMNS_TO_IGNORE = [
    "media",
    "id",
    "developerAgent"
]
