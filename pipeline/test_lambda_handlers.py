"""A script to test the plant monitoring system lambda handlers."""
from unittest.mock import MagicMock, patch
from lambda_handlers import etl_lambda_handler


@patch("lambda_handlers.run_pipeline")
def test_lambda_handler_success(mock_run_pipeline):
    mock_run_pipeline.return_value = None

    event = {}
    context = MagicMock()
    response = etl_lambda_handler(event, context)

    mock_run_pipeline.assert_called_once()

    assert response["statusCode"] == 200
    assert response["body"] == "ETL pipeline executed successfully."
