from datetime import datetime


class ReviewSchema:
    def __init__(
        self,
        productId: str,
        userId: str,
        rating: int,
        comment: str,
        userName: str
    ):
        self.productId = productId
        self.userId = userId
        self.rating = rating
        self.comment = comment
        self.userName = userName
        self.createdAt = datetime.utcnow()
        self.updatedAt = datetime.utcnow()
    
    def to_dict(self):
        return {
            "productId": self.productId,
            "userId": self.userId,
            "rating": self.rating,
            "comment": self.comment,
            "userName": self.userName,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            productId=data["productId"],
            userId=data["userId"],
            rating=data["rating"],
            comment=data["comment"],
            userName=data["userName"]
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updatedAt = datetime.utcnow()
