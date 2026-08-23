class EstimationError(Exception):
    pass


class CategoryNotFoundError(EstimationError):
    def __init__(self, category: str):
        self.category = category
        super().__init__(f"Category not found: {category}")


class CategoryNotActiveError(EstimationError):
    def __init__(self, category: str):
        self.category = category
        super().__init__(f"Category not active: {category}")


class TimeRangeInvalidError(EstimationError):
    def __init__(self, min_time: int, max_time: int):
        self.min_time = min_time
        self.max_time = max_time
        super().__init__(f"Invalid time range: {min_time}-{max_time}")


class EstimationOutOfRangeError(EstimationError):
    def __init__(self, estimated: int, min_time: int, max_time: int):
        self.estimated = estimated
        self.min_time = min_time
        self.max_time = max_time
        super().__init__(f"Estimation {estimated} out of range {min_time}-{max_time}")


class DescriptionEmptyError(EstimationError):
    def __init__(self):
        super().__init__("Description is empty")


class AIServiceError(EstimationError):
    def __init__(self, message: str):
        super().__init__(f"AI Service error: {message}")


class CatalogServiceError(EstimationError):
    def __init__(self, message: str):
        super().__init__(f"Catalog Service error: {message}")
