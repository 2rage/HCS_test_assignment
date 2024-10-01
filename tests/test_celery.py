from celery.result import EagerResult
from app.tasks import calculate_bill
from app.database import db
from unittest.mock import patch


def test_calculate_bill():
    house_id = "64f837f25c1234567890abcd"
    month = "September"
    year = 2024

    with patch.object(db.houses, "find_one") as mock_find_one, patch.object(
        db.tariffs, "find_one"
    ) as mock_find_tariff, patch.object(db.bills, "insert_one") as mock_insert:

        mock_find_one.return_value = {
            "_id": house_id,
            "address": "Test House",
            "apartments": [
                {"_id": "1", "area": 100, "meters": [{"readings": [10, 20]}]}
            ],
        }
        mock_find_tariff.side_effect = [
            {"name": "water", "price_per_unit": 2},
            {"name": "maintenance", "price_per_unit": 1},
        ]

        result = calculate_bill.apply(args=[house_id, month, year])

        assert isinstance(result, EagerResult)
        assert result.status == "SUCCESS"
        mock_insert.assert_called_once()
